"""Apoio aos testes da Fiscalização (não contém testes).

BancoTemporario troca o banco do sistema por um arquivo SQLite novo
antes de cada teste e cria as tabelas do sistema e da fiscalização.

A propriedade de teste é inserida direto por SQL, com nome,
proprietario_id e uma área de teste (area_de_teste), e com as FKs
desligadas nesse INSERT. Assim os testes
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


def area_de_teste(indice, lado=0.01):
    """Quadrado de 'lado' graus perto de Passo Fundo. Índices diferentes não se sobrepõem."""
    lat, lon = -28.26, -52.41 + (indice - 1) * 2 * lado
    vertices = [(lat, lon), (lat, lon + lado), (lat + lado, lon + lado), (lat + lado, lon)]
    return ";".join(f"{a:g},{b:g}" for a, b in vertices)


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

    def criar_propriedade(self, nome, poligono=None):
        """Insere a propriedade com uma área de teste (um quadrado ao lado do outro)."""
        self._areas_criadas = getattr(self, "_areas_criadas", 0) + 1
        conn = database.get_connection()
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            cursor = conn.execute(
                "INSERT INTO propriedades_rurais (nome, proprietario_id, poligono) VALUES (?, 1, ?)",
                (nome, poligono or area_de_teste(self._areas_criadas)),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def centro_da(self, propriedade_id):
        """Um ponto dentro da área da propriedade: o centroide."""
        from model.propriedade_rural import PropriedadeRural

        return PropriedadeRural.buscar_por_id(propriedade_id).centroide

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
