from lexer import HinglishLexer

class HinglishInterpreter:
    def __init__(self):
        self.vars = {}

    def evaluate_expr(self, expr):
        expr = expr.strip().rstrip(";")
        expr = expr.replace("sahi", "True").replace("jhooth", "False")
        try:
            return eval(expr, {}, self.vars)
        except Exception as e:
            print(" Error evaluating:", expr, "→", e)
            return 0

    def execute_block(self, lines):
        for line in lines:
            self.execute_line(line)

    def extract_block(self, code_lines, start_index):
        block = []
        i = start_index + 1
        brace_count = 1
        while i < len(code_lines) and brace_count > 0:
            line = code_lines[i].strip()
            if "{" in line:
                brace_count += 1
            if "}" in line:
                brace_count -= 1
            if brace_count > 0:
                block.append(line)
            i += 1
        return block, i

    def execute_line(self, line):
        line = line.strip().rstrip(";")
        if not line or line.startswith("//"):
            return

        # Variable Declarations
        if line.startswith("no "):  # int
            name = line.split()[1]
            value = 0
            if "=" in line:
                expr = line.split("=", 1)[1]
                value = self.evaluate_expr(expr)
            self.vars[name] = int(value)

        elif line.startswith("binduNo "):  # float
            name = line.split()[1]
            value = 0.0
            if "=" in line:
                expr = line.split("=", 1)[1]
                value = self.evaluate_expr(expr)
            self.vars[name] = float(value)

        elif line.startswith("sach "):  # bool
            name = line.split()[1]
            value = False
            if "=" in line:
                expr = line.split("=", 1)[1]
                value = self.evaluate_expr(expr)
            self.vars[name] = bool(value)

        # Print
        elif line.startswith("likh"):
            content = line.replace("likh", "", 1).strip()
            if content.startswith("(") and content.endswith(")"):
                content = content[1:-1]
            val = self.evaluate_expr(content)
            print("🪶", val)

        # Assignment
        elif "=" in line:
            name, expr = line.split("=", 1)
            self.vars[name.strip()] = self.evaluate_expr(expr)

        else:
            print("!!! Unknown statement:", line)

    def run(self, code):
        code_lines = [l.strip() for l in code.splitlines() if l.strip()]
        i = 0
        while i < len(code_lines):
            line = code_lines[i]

            # Handle if-else
            if line.startswith("agar"):
                cond = line[line.find("(") + 1: line.find(")")]
                cond_result = bool(self.evaluate_expr(cond))
                block, next_i = self.extract_block(code_lines, i)
                if cond_result:
                    self.execute_block(block)
                    if next_i < len(code_lines) and code_lines[next_i].startswith("warna"):
                        _, skip_i = self.extract_block(code_lines, next_i)
                        i = skip_i
                    else:
                        i = next_i
                else:
                    if next_i < len(code_lines) and code_lines[next_i].startswith("warna"):
                        warna_block, warna_end = self.extract_block(code_lines, next_i)
                        self.execute_block(warna_block)
                        i = warna_end
                    else:
                        i = next_i
                continue

            # Handle while (jabtk)
            elif line.startswith("jabtk"):
                cond = line[line.find("(") + 1: line.find(")")]
                loop_block, next_i = self.extract_block(code_lines, i)
                while bool(self.evaluate_expr(cond)):
                    self.execute_block(loop_block)
                i = next_i
                continue

            # Normal statements
            self.execute_line(line)
            i += 1
