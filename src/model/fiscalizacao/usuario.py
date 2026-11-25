from model.base import ModeloBase
from model.fiscalizacao.fonte import FonteDeteccao
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL
);
"""


class Usuario(ModeloBase, FonteDeteccao):
    """Pessoa que denuncia desmatamento."""

    TABELA = "usuarios"
    COLUNAS = ("nome", "cpf", "email")

    def __init__(self, nome, cpf, email, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email

    # ---- Factory Method ----
    def criar_registro(self, propriedade_id, descricao, latitude, longitude, data):
        return RegistroDesmatamento(
            propriedade_id, descricao, data, latitude, longitude, usuario_id=self.id
        )

    def reportar_desmatamento(self, propriedade_id, descricao, latitude, longitude,
                              data, evidencias):
        """Denúncia de pessoa precisa de pelo menos uma evidência."""
        if not evidencias:
            raise ValueError("Denúncia de usuário exige pelo menos uma evidência.")
        return self.criar_registro(propriedade_id, descricao, latitude, longitude, data)

    # ---- buscas específicas ----
    @classmethod
    def buscar_por_cpf(cls, cpf):
        return cls._buscar_um("cpf = ?", (cpf,))
