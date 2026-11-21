from model.base import ModeloBase
from model.fiscalizacao.fonte import FonteDeteccao
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento

SCHEMA = """
CREATE TABLE IF NOT EXISTS satelites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    entidade_responsavel TEXT
);
"""


class Satelite(ModeloBase, FonteDeteccao):
    TABELA = "satelites"
    COLUNAS = ("nome", "entidade_responsavel")

    def __init__(self, nome, entidade_responsavel=None, id=None):
        self.id = id
        self.nome = nome
        self.entidade_responsavel = entidade_responsavel

    # ---- Factory Method ----
    def criar_registro(self, propriedade_id, descricao, latitude, longitude, data):
        return RegistroDesmatamento(
            propriedade_id, descricao, data, latitude, longitude, satelite_id=self.id
        )

    def detectar_desmatamento(self, propriedade_id, descricao, latitude, longitude, data):
        """Satélite não precisa de evidência anexada: a própria imagem é a detecção."""
        return self.criar_registro(propriedade_id, descricao, latitude, longitude, data)
