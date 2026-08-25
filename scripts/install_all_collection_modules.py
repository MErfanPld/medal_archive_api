#!/usr/bin/env python3
"""Install all 7 collection modules. Run from project root."""
import runpy
from pathlib import Path
HERE = Path(__file__).resolve().parent
APPS = ["banknotes", "seals", "tasbih", "rings", "knives", "antiques", "stamps"]
def main():
    for app in APPS:
        print("===", app, "===")
        runpy.run_path(str(HERE / f"install_{app}.py"), run_name="__main__")
    print("\nAll done. Next: python manage.py migrate && python manage.py check")
if __name__ == "__main__":
    main()
