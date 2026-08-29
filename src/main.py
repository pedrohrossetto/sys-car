import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import init_db
from view.proprietario_view import ProprietarioView


def main():
    init_db()
    print("=== SYS-CAR ===")
    print("1. CRUD Proprietário")
    opcao = input("Escolha uma opção: ").strip()
    if opcao == "1":
        ProprietarioView().exibir_menu()
    else:
        print("Opção inválida.")


if __name__ == "__main__":
    main()
