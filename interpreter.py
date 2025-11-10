# interpreter.py
import re
from typing import List, Tuple

# Control exceptions
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class ReturnSignal(Exception):
    def __init__(self, value=None):
        self.value = value

# ---------- helpers: string-aware transforms ----------
_quote_split_re = re.compile(r"('(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\")")

def _split_keep_quotes(s: str) -> List[str]:
    # returns list of segments where quoted segments appear as their own items
    return re.split(_quote_split_re, s)

def _replace_outside_quotes(s: str, pattern: str, repl: str) -> str:
    parts = _split_keep_quotes(s)
    for i in range(0, len(parts), 2):  # even indices are outside quotes
        parts[i] = re.sub(pattern, repl, parts[i])
    return "".join(parts)

def _subst_vars_with_quotes(expr: str, vars_dict: dict) -> str:
    # substitute variable names with repr(value) but only outside quoted strings
    parts = _split_keep_quotes(expr)
    for idx in range(0, len(parts), 2):
        seg = parts[idx]
        # replace longer names first to avoid partial replacements
        for var in sorted(vars_dict.keys(), key=len, reverse=True):
            val = vars_dict[var]
            if isinstance(val, str):
                replacement = repr(val)  # adds proper quotes & escapes
            else:
                replacement = str(val)
            seg = re.sub(rf'\b{re.escape(var)}\b', replacement, seg)
        parts[idx] = seg
    return "".join(parts)

def _is_blank_or_comment(line: str) -> bool:
    s = line.strip()
    return not s or s.startswith("//")

# ---------- Interpreter ----------
class HinglishInterpreter:
    def __init__(self):
        self.vars = {}
        self.safe_builtins = {
            'str': str, 'int': int, 'float': float, 'bool': bool,
            'len': len, 'abs': abs, 'round': round, 'range': range,
            'max': max, 'min': min
        }

    # Evaluate Hinglish expression safely
    def eval_expr(self, expr: str):
        if expr is None:
            return None
        expr = expr.strip()
        # logical/boolean words outside strings
        expr = _replace_outside_quotes(expr, r'\baur\b', 'and')
        expr = _replace_outside_quotes(expr, r'\bya\b', 'or')
        expr = _replace_outside_quotes(expr, r'\bnahin\b', 'not')
        expr = _replace_outside_quotes(expr, r'\bsahi\b', 'True')
        expr = _replace_outside_quotes(expr, r'\bjhooth\b', 'False')
        # substitute identifiers with values outside strings
        expr_subst = _subst_vars_with_quotes(expr, self.vars)
        try:
            return eval(expr_subst, {"__builtins__": {}}, self.safe_builtins)
        except Exception as e:
            print(f"⚠️ Error evaluating: {expr} → {e}")
            return None

    # --------- Block parsing for a global lines list ---------
    # returns (block_lines, end_index) where end_index is index of the closing '}' line
    def parse_block(self, lines: List[str], header_index: int) -> Tuple[List[str], int]:
        # find the position of the first '{' at or after header_index
        i = header_index
        found_open = False
        while i < len(lines):
            if '{' in lines[i]:
                found_open = True
                break
            i += 1
        if not found_open:
            return [], header_index
        # block content starts after i
        start = i + 1
        block = []
        depth = 0
        j = start
        while j < len(lines):
            line = lines[j]
            # naive brace counting by characters (assumes braces not inside strings)
            if '{' in line:
                depth += line.count('{')
            if '}' in line:
                if depth == 0:
                    return block, j
                depth -= line.count('}')
            block.append(line)
            j += 1
        return block, j - 1

    # --------- Local block parsing inside an already extracted block ---------
    def _parse_block_local(self, lines: List[str], header_index: int) -> Tuple[List[str], int]:
        # find line containing '{' at/after header_index
        i = header_index
        while i < len(lines) and '{' not in lines[i]:
            i += 1
        if i >= len(lines):
            return [], header_index
        start = i + 1
        block = []
        depth = 0
        j = start
        while j < len(lines):
            s = lines[j]
            if '{' in s:
                depth += s.count('{')
            if '}' in s:
                if depth == 0:
                    return block, j
                depth -= s.count('}')
            block.append(s)
            j += 1
        return block, len(lines) - 1

    # ---------- Top-level program run ----------
    def run(self, code: str):
        raw_lines = code.splitlines()
        self._run_lines(raw_lines)

    def _run_lines(self, lines: List[str]):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("//"):
                i += 1
                continue

            # IF / ELSE
            if line.startswith("agar"):
                m = re.search(r"agar\s*\((.*?)\)", line)
                cond = m.group(1).strip() if m else ""
                body, end_idx = self.parse_block(lines, i)
                if bool(self.eval_expr(cond)):
                    try:
                        self.run_block(body)
                    except ReturnSignal as r:
                        # bubble return up to the outermost caller
                        raise r
                else:
                    nxt = end_idx + 1
                    if nxt < len(lines) and lines[nxt].strip().startswith("warna"):
                        else_body, else_end = self.parse_block(lines, nxt)
                        try:
                            self.run_block(else_body)
                        except ReturnSignal as r:
                            raise r
                        i = else_end + 1
                        continue
                i = end_idx + 1
                continue

            # WHILE jabtk
            if line.startswith("jabtk"):
                m = re.search(r"jabtk\s*\((.*?)\)", line)
                cond_expr = m.group(1).strip() if m else ""
                body, end_idx = self.parse_block(lines, i)
                while True:
                    cond_val = self.eval_expr(cond_expr)
                    if not bool(cond_val):
                        break
                    try:
                        self.run_block(body)
                    except BreakSignal:
                        break
                    except ContinueSignal:
                        continue
                    except ReturnSignal as r:
                        raise r
                i = end_idx + 1
                continue

            # FOR chal (init; cond; update)
            if line.startswith("chal"):
                m = re.search(r"chal\s*\((.*?)\)", line)
                content = m.group(1).strip() if m else ""
                parts = [p.strip() for p in content.split(";")]
                if len(parts) != 3:
                    print("⚠️ For-loop syntax invalid. Expected 3 parts: init; cond; update")
                    i += 1
                    continue
                init, cond, update = parts
                if init:
                    self.execute_line(init)
                body, end_idx = self.parse_block(lines, i)
                while True:
                    if cond and not bool(self.eval_expr(cond)):
                        break
                    try:
                        self.run_block(body)
                    except BreakSignal:
                        break
                    except ContinueSignal:
                        if update:
                            self.execute_line(update)
                        continue
                    if update:
                        self.execute_line(update)
                i = end_idx + 1
                continue

            # Non-structural statement
            try:
                self.execute_line(line)
            except ReturnSignal as r:
                # bubble to outer level
                raise r
            i += 1

    # ---------- Execute a list of lines as a block ----------
    def run_block(self, block_lines: List[str]):
        j = 0
        while j < len(block_lines):
            raw = block_lines[j]
            line = raw.strip()
            if not line or line.startswith("//"):
                j += 1
                continue

            # Nested structures handled locally so we do not abort the rest of the block
            if line.startswith("agar"):
                m = re.search(r"agar\s*\((.*?)\)", line)
                cond = m.group(1).strip() if m else ""
                if_body, if_end = self._parse_block_local(block_lines, j)
                if bool(self.eval_expr(cond)):
                    self.run_block(if_body)
                    j = if_end + 1
                    # optional else
                    if j < len(block_lines) and block_lines[j].strip().startswith("warna"):
                        else_body, else_end = self._parse_block_local(block_lines, j)
                        # skip else since if executed
                        j = else_end + 1
                    continue
                else:
                    # skip if body, maybe execute else
                    j = if_end + 1
                    if j < len(block_lines) and block_lines[j].strip().startswith("warna"):
                        else_body, else_end = self._parse_block_local(block_lines, j)
                        self.run_block(else_body)
                        j = else_end + 1
                    continue

            if line.startswith("jabtk"):
                m = re.search(r"jabtk\s*\((.*?)\)", line)
                cond_expr = m.group(1).strip() if m else ""
                while_body, while_end = self._parse_block_local(block_lines, j)
                while True:
                    if not bool(self.eval_expr(cond_expr)):
                        break
                    try:
                        self.run_block(while_body)
                    except BreakSignal:
                        break
                    except ContinueSignal:
                        continue
                j = while_end + 1
                continue

            if line.startswith("chal"):
                m = re.search(r"chal\s*\((.*?)\)", line)
                content = m.group(1).strip() if m else ""
                parts = [p.strip() for p in content.split(";")]
                if len(parts) != 3:
                    print("⚠️ For-loop syntax invalid inside block.")
                    j += 1
                    continue
                init, cond, update = parts
                if init:
                    self.execute_line(init)
                for_body, for_end = self._parse_block_local(block_lines, j)
                while True:
                    if cond and not bool(self.eval_expr(cond)):
                        break
                    try:
                        self.run_block(for_body)
                    except BreakSignal:
                        break
                    except ContinueSignal:
                        if update:
                            self.execute_line(update)
                        continue
                    if update:
                        self.execute_line(update)
                j = for_end + 1
                continue

            # Simple line
            try:
                self.execute_line(line)
            except (BreakSignal, ContinueSignal, ReturnSignal) as sig:
                # propagate to enclosing loop or caller
                raise sig
            j += 1

    # ---------- Execute a single non-structural line ----------
    def execute_line(self, raw_line: str):
        s = raw_line.strip()
        if not s or s.startswith("//"):
            return

        # PRINT
        if s.startswith("likh"):
            rest = s[len("likh"):].strip()
            if rest.startswith("(") and rest.endswith(")"):
                rest = rest[1:-1].strip()
            val = self.eval_expr(rest)
            print("🪶", val)
            return

        # RETURN
        if s.startswith("lautao"):
            rest = s[len("lautao"):].strip()
            val = self.eval_expr(rest) if rest else None
            raise ReturnSignal(val)

        # BREAK / CONTINUE
        if s == "tod":
            raise BreakSignal()
        if s == "aage":
            raise ContinueSignal()

        # DECLARATIONS: no|binduno|shabd|sach
        m = re.match(r'^(no|binduno|shabd|sach)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:=\s*(.+))?$', s)
        if m:
            typ, name, rhs = m.groups()
            if rhs is None:
                defaults = {'no': 0, 'binduno': 0.0, 'shabd': "", 'sach': False}
                value = defaults.get(typ)
            else:
                value = self.eval_expr(rhs)
            self.vars[name] = value
            return

        # ASSIGNMENT name = expr
        if "=" in s and not s.startswith(("agar", "jabtk", "chal")):
            name, expr = s.split("=", 1)
            name = name.strip()
            expr = expr.strip()
            value = self.eval_expr(expr)
            self.vars[name] = value
            return

        # Unknown (ignore silently or print)
        # print("!!! Unknown statement:", s)
