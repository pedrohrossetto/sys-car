import sqlite3
from pathlib import Path

from descoberta import modulos_com

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "syscar.db"


def get_connection():
    """Abre e retorna uma conexão com o banco SQLite.

    O diretório 'data/' é criado caso ainda não exista.
    PRAGMA foreign_keys = ON faz o SQLite respeitar as chaves
    estrangeiras e aplicar o ON DELETE CASCADE.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas de todos os models que definem a constante SCHEMA.

    Cada módulo do pacote 'model' (inclusive subpacotes) pode declarar
    SCHEMA com um ou mais 'CREATE TABLE IF NOT EXISTS'. Este arquivo não
    conhece nenhuma tabela: quem cria uma entidade nova não precisa editá-lo.
    """
    import model

    conn = get_connection()
    try:
        for modulo in modulos_com(model, "SCHEMA"):
            conn.executescript(modulo.SCHEMA)
        conn.commit()
    finally:
        conn.close()
