from interpreter import HinglishInterpreter

# Read Hinglish source
with open(r"G:\DTUN acad docs\DTU ACAD ALL\FIVTHSEM\compiler design\Hinglish\test.hl", "r", encoding="utf-8") as f:
    code = f.read()

interpreter = HinglishInterpreter()
interpreter.run(code)
