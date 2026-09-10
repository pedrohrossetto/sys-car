import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import init_db


def main():
    init_db()
    from view.app_tk import HAS_TK
    if HAS_TK:
        from view.app_tk import main as main_tk
        main_tk()
    else:
        print("Tkinter não disponível neste ambiente. Usando o modo console...")
        from view.menu_console import main as main_console
        main_console()


if __name__ == "__main__":
    main()