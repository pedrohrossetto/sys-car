"""Apoio aos testes do Cadastro (não contém testes).

BancoTemporario troca o banco do sistema por um arquivo SQLite novo,
dentro de um diretório temporário, antes de cada teste.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from database import database


class BancoTemporario(unittest.TestCase):
    CRIAR_TABELAS = True

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._originais = (database.DATA_DIR, database.DB_PATH)
        database.DATA_DIR = Path(self._tmp.name)
        database.DB_PATH = database.DATA_DIR / "teste.db"
        if self.CRIAR_TABELAS:
            database.init_db()

    def tearDown(self):
        database.DATA_DIR, database.DB_PATH = self._originais
        self._tmp.cleanup()

    def tabelas(self):
        conn = database.get_connection()
        try:
            linhas = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            return {linha[0] for linha in linhas}
        finally:
            conn.close()
