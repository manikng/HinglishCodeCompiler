#!/usr/bin/env python3
import sys
from interpreter import HinglishInterpreter

def main():
    if len(sys.argv) < 2:
        print(" Usage: hinglish <file.hl>")
        return
    
    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return

    interpreter = HinglishInterpreter()
    interpreter.run(code)

if __name__ == "__main__":
    main()
