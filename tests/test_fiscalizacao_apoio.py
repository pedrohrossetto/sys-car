"""Apoio aos testes da Fiscalização (não contém testes).

BancoTemporario troca o banco do sistema por um arquivo SQLite novo
antes de cada teste e cria as tabelas do sistema e da fiscalização.

A propriedade de teste é inserida direto por SQL, só com nome e
proprietario_id e com as FKs desligadas nesse INSERT. Assim os testes
não dependem do formato da tabela de proprietários, que pertence à
Frente 1 e muda durante o desenvolvimento dela.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from controller.fiscalizacao.instalacao import preparar_banco
from database import database


class BancoTemporario(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._originais = (database.DATA_DIR, database.DB_PATH)
        database.DATA_DIR = Path(self._tmp.name)
        database.DB_PATH = database.DATA_DIR / "teste.db"
        preparar_banco()
        self.propriedade_id = self.criar_propriedade("Sítio Teste")

    def tearDown(self):
        database.DATA_DIR, database.DB_PATH = self._originais
        self._tmp.cleanup()

    def criar_propriedade(self, nome):
        conn = database.get_connection()
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            cursor = conn.execute(
                "INSERT INTO propriedades_rurais (nome, proprietario_id) VALUES (?, 1)", (nome,)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def contar(self, tabela):
        conn = database.get_connection()
        try:
            return conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        finally:
            conn.close()

    def tabelas(self):
        conn = database.get_connection()
        try:
            linhas = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            return {linha[0] for linha in linhas}
        finally:
            conn.close()
