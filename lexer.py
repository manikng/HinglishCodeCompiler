import re
from dataclasses import dataclass

# A single token in the Hinglish language
@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int

# Hinglish Language Lexer
class HinglishLexer:
    def __init__(self):
        # ✅ Hinglish keywords map
        self.keywords = {
            # types
            "no": "TYPE_INT",
            "binduno": "TYPE_FLOAT",       # float/double
            "sach": "TYPE_BOOL",
            "shabd": "TYPE_STRING",
            # control flow
            "chal": "KW_FOR",
            "jabtk": "KW_WHILE",
            "agar": "KW_IF",
            "warna": "KW_ELSE",
            "lautao": "KW_RETURN",
            "tod": "KW_BREAK",
            "aage": "KW_CONTINUE",
            # boolean literals
            "sahi": "BOOL_TRUE",
            "jhooth": "BOOL_FALSE",
            # range helpers
            "se": "KW_FROM",
            "tak": "KW_TO",
            "tk": "KW_TO",
            # logical words
            "aur": "OP_AND",
            "ya": "OP_OR",
            "nahin": "OP_NOT",
            # print
            "likh": "KW_PRINT"
        }

        #  Token patterns
        token_specification = [
            ("COMMENT", r"//[^\n]*|/\*[\s\S]*?\*/"),
            ("STRING", r'"([^"\\]|\\.)*"'),
            ("CHAR", r"'([^'\\]|\\.)'"),
            ("FLOAT", r"\d+\.\d+"),
            ("INT", r"\d+"),
            ("ID", r"[A-Za-z_\u0900-\u097F][A-Za-z0-9_\u0900-\u097F_]*"),
            ("OP", r"==|!=|<=|>=|\+\+|--|&&|\|\||->|[-+*/%<>=!~^]"),
            ("SEMI", r";"),
            ("COMMA", r","),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("LBRACE", r"\{"),
            ("RBRACE", r"\}"),
            ("ASSIGN", r"="),
            ("NEWLINE", r"\n"),
            ("SKIP", r"[ \t\r]+"),
            ("MISMATCH", r"."),
        ]

        # Compile master regex
        parts = [f"(?P<{name}>{pattern})" for name, pattern in token_specification]
        self.master_re = re.compile("|".join(parts), re.UNICODE)

    def tokenize(self, code: str):
        """Turn Hinglish source code into tokens."""
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
                if low in self.keywords:
                    tokens.append(Token(self.keywords[low], lexeme, line_num, col))
                else:
                    tokens.append(Token("IDENTIFIER", lexeme, line_num, col))

            elif kind == "INT":
                tokens.append(Token("INT_LITERAL", lexeme, line_num, col))

            elif kind == "FLOAT":
                tokens.append(Token("FLOAT_LITERAL", lexeme, line_num, col))

            elif kind == "STRING":
                tokens.append(Token("STRING_LITERAL", lexeme, line_num, col))

            elif kind == "CHAR":
                tokens.append(Token("CHAR_LITERAL", lexeme, line_num, col))

            elif kind == "MISMATCH":
                tokens.append(Token("UNKNOWN", lexeme, line_num, col))

            else:
                tokens.append(Token(kind, lexeme, line_num, col))

        return tokens
