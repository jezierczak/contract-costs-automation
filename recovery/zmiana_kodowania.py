import re
from difflib import unified_diff


def main():

    mapping = {
        "┼é": "ł",
        "┼ä": "ą",
        "┼â": "ń",
        "┼ü": "Ł",
        "┼Ü": "Ś",
        "─ä": "ą",
        "─ů": "ą",
        "┼Ť": "ś",
        "┼╗": "ż",
        "┬ú": "ż",
        "├│┼é": "ół",
        "├ô┼ü": "ół",
        "Wroc┼éaw": "Wrocław",
        "Krak├│w": "Kraków",
        "Zak┼éad": "Zakład",
        "Us┼éugowa": "Usługowa",
        "Jaros┼éaw": "Jarosław",
    }

    def fix(text):
        original = text
        for bad, good in mapping.items():
            text = text.replace(bad, good)
        return original, text

    with open("companies_recovery.sql", "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    for line in lines:
        orig, fixed = fix(line)
        if orig != fixed:
            print("ZMIANA:")
            print("ORIG :", orig.strip())
            print("FIX  :", fixed.strip())
            print("-" * 50)
        fixed_lines.append(fixed)

    with open("companies_recovery_fixed.sql", "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)
if __name__ == "__main__":
    main()