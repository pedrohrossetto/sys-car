import sqlite3
from pathlib import Path

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
    """Cria as tabelas do banco, caso ainda não existam (IF NOT EXISTS).

    A tabela 'proprietarios' é criada primeiro porque as outras duas
    referenciam ela via FOREIGN KEY.
    """
    conn = get_connection()
    # 'cursor' é o objeto do sqlite3 que executa comandos SQL e
    # guarda o resultado da consulta. Ele "aponta" para as linhas
    # retornadas, permitindo percorrê-las com fetchone()/fetchall().
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS proprietarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            cnpj TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS propriedades_rurais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cadastro_publico TEXT,
            proprietario_id INTEGER NOT NULL,
            FOREIGN KEY (proprietario_id) REFERENCES proprietarios(id)
                ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS localizacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            poligono_geometria TEXT,
            propriedade_id INTEGER UNIQUE NOT NULL,
            FOREIGN KEY (propriedade_id) REFERENCES propriedades_rurais(id)
                ON DELETE CASCADE
        )
        """
    )
    # 'commit' grava as alterações no arquivo do banco.
    conn.commit()
    conn.close()