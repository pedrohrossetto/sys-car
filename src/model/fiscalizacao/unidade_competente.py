from model.base import ModeloBase

SCHEMA = """
CREATE TABLE IF NOT EXISTS unidades_competentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo_unidade_orgao TEXT,
    contato TEXT
);
"""


class UnidadeCompetente(ModeloBase):
    """Órgão que examina alertas e embarga propriedades (ex.: IBAMA, FEPAM)."""

    TABELA = "unidades_competentes"
    COLUNAS = ("nome", "tipo_unidade_orgao", "contato")

    def __init__(self, nome, tipo_unidade_orgao=None, contato=None, id=None):
        self.id = id
        self.nome = nome
        self.tipo_unidade_orgao = tipo_unidade_orgao
        self.contato = contato
