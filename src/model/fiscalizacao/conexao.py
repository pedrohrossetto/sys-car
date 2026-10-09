"""Acesso ao banco usado pelos models da fiscalização.

Cada função abre a conexão, executa e fecha, como os models originais
do projeto fazem. Assim os models não repetem o abre/commit/fecha.
"""
from database.database import get_connection


def executar(sql, parametros=()):
    """Executa INSERT/UPDATE/DELETE e devolve o id da última linha inserida."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, parametros)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def consultar(sql, parametros=()):
    """Executa um SELECT e devolve todas as linhas (lista de tuplas)."""
    conn = get_connection()
    try:
        return conn.execute(sql, parametros).fetchall()
    finally:
        conn.close()


def consultar_um(sql, parametros=()):
    """Executa um SELECT e devolve a primeira linha, ou None."""
    linhas = consultar(sql, parametros)
    return linhas[0] if linhas else None
