from database.database import get_connection
from model.base import ModeloBase

SCHEMA = """
CREATE TABLE IF NOT EXISTS proprietarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('PF', 'PJ')),
    cpf TEXT UNIQUE,
    cnpj TEXT UNIQUE,
    CHECK (
        (tipo = 'PF' AND cpf IS NOT NULL AND cnpj IS NULL) OR
        (tipo = 'PJ' AND cnpj IS NOT NULL AND cpf IS NULL)
    )
);
"""


class Proprietario(ModeloBase):
    TABELA = "proprietarios"
    COLUNAS = ("nome", "tipo", "cpf", "cnpj")

    def __init__(self, nome, tipo, cpf=None, cnpj=None, id=None):
        self.id = id
        self.nome = nome
        # 'PF' (pessoa física, usa CPF) ou 'PJ' (pessoa jurídica, usa CNPJ).
        self.tipo = tipo
        self.cpf = cpf
        self.cnpj = cnpj

    @property
    def documento(self):
        return self.cpf if self.tipo == "PF" else self.cnpj

    @classmethod
    def buscar_por_cpf(cls, cpf):
        return cls._buscar_um("cpf = ?", (cpf,))

    @classmethod
    def buscar_por_cnpj(cls, cnpj):
        return cls._buscar_um("cnpj = ?", (cnpj,))

    @classmethod
    def buscar_por_documento(cls, tipo, documento):
        if tipo == "PF":
            return cls.buscar_por_cpf(documento)
        return cls.buscar_por_cnpj(documento)

    @staticmethod
    def schema_desatualizado():
        """True se o banco tem a tabela da versão antiga (sem a coluna 'tipo')."""
        conn = get_connection()
        try:
            colunas = [linha[1] for linha in conn.execute("PRAGMA table_info(proprietarios)")]
        finally:
            conn.close()
        return bool(colunas) and "tipo" not in colunas
