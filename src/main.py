import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SEM_TKINTER = (
    "O SYS-CAR precisa do Tkinter, que não está instalado neste Python.\n"
    "  - Linux (Debian/Ubuntu): sudo apt install python3-tk\n"
    "  - Windows/macOS: reinstale o Python pelo instalador oficial (python.org),\n"
    "    que já inclui o Tkinter."
)

BANCO_ANTIGO = (
    "O banco data/syscar.db foi criado por uma versão antiga do SYS-CAR.\n"
    "Apague o arquivo data/syscar.db e rode o programa de novo."
)


def main():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print(SEM_TKINTER)
        return 1

    from controller.proprietario_controller import ProprietarioController
    from database.database import init_db

    init_db()
    if ProprietarioController().banco_desatualizado():
        print(BANCO_ANTIGO)
        return 1

    from view.janela_principal import main as abrir_janela

    abrir_janela()
    return 0


if __name__ == "__main__":
    sys.exit(main())
