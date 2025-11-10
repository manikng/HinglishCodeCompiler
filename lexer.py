import re
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int


class HinglishLexer:
    def __init__(self):
        self.keywords = {
            # Types
            "no": "TYPE_INT",
            "binduno": "TYPE_FLOAT",
            "sach": "TYPE_BOOL",
            "shabd": "TYPE_STRING",
            # Control flow
            "chal": "KW_FOR",
            "jabtk": "KW_WHILE",
            "agar": "KW_IF",
            "warna": "KW_ELSE",
            "lautao": "KW_RETURN",
            "tod": "KW_BREAK",
            "aage": "KW_CONTINUE",
            # Booleans
            "sahi": "BOOL_TRUE",
            "jhooth": "BOOL_FALSE",
            # Operators
            "aur": "OP_AND",
            "ya": "OP_OR",
            "nahin": "OP_NOT",
            # Print
            "likh": "KW_PRINT"
        }

        token_specification = [
            ("COMMENT", r"//[^\n]*|/\*[\s\S]*?\*/"),
            ("STRING", r'"([^"\\]|\\.)*"'),
            ("FLOAT", r"\d+\.\d+"),
            ("INT", r"\d+"),
            ("ID", r"[A-Za-z_\u0900-\u097F][A-Za-z0-9_\u0900-\u097F_]*"),
            ("OP", r"==|!=|<=|>=|\+\+|--|[-+*/%<>=!]"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("LBRACE", r"\{"),
            ("RBRACE", r"\}"),
            ("ASSIGN", r"="),
            ("NEWLINE", r"\n"),
            ("SKIP", r"[ \t\r]+"),
            ("MISMATCH", r"."),
        ]

        parts = [f"(?P<{name}>{pattern})" for name, pattern in token_specification]
        self.master_re = re.compile("|".join(parts), re.UNICODE)

    def tokenize(self, code: str):
        tokens = []
        line_num = 1
        line_start = 0

        for mo in self.master_re.finditer(code):
            kind = mo.lastgroup
            lexeme = mo.group(kind)
            col = mo.start() - line_start + 1

            if kind == "NEWLINE":
                line_num += 1
                line_start = mo.end()
                continue
            elif kind in ("SKIP", "COMMENT"):
                continue
            elif kind == "ID":
                low = lexeme.lower()
                token_type = self.keywords.get(low, "IDENTIFIER")
                tokens.append(Token(token_type, lexeme, line_num, col))
            elif kind in ("INT", "FLOAT", "STRING"):
                tokens.append(Token(f"{kind}_LITERAL", lexeme, line_num, col))
            elif kind == "MISMATCH":
                tokens.append(Token("UNKNOWN", lexeme, line_num, col))
            else:
                tokens.append(Token(kind, lexeme, line_num, col))

        return tokens
