from lexer import HinglishLexer

# Use full path to your test file
with open(r"G:\DTUN acad docs\DTU ACAD ALL\FIVTHSEM\compiler design\Hinglish\test.hl", "r", encoding="utf-8") as f:
    code = f.read()

lexer = HinglishLexer()
tokens = lexer.tokenize(code)

print(" Hinglish Token Stream:\n")
for t in tokens:
    print(f"{t.line:2}:{t.col:3} {t.type:12} {t.lexeme}")
