from model.base import ModeloBase

SCHEMA = """
CREATE TABLE IF NOT EXISTS notificacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registro_id INTEGER NOT NULL
        REFERENCES registros_desmatamento(id) ON DELETE CASCADE,
    unidade_id INTEGER NOT NULL
        REFERENCES unidades_competentes(id) ON DELETE CASCADE,
    data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ENVIADA' CHECK (status IN ('ENVIADA', 'LIDA')),
    mensagem TEXT NOT NULL
);
"""


class Notificacao(ModeloBase):
    TABELA = "notificacoes"
    COLUNAS = ("registro_id", "unidade_id", "data", "mensagem", "status")

    def __init__(self, registro_id, unidade_id, data, mensagem, status="ENVIADA", id=None):
        self.id = id
        self.registro_id = registro_id
        self.unidade_id = unidade_id
        self.data = data
        self.mensagem = mensagem
        self.status = status

    # ---- buscas específicas ----
    @classmethod
    def listar_todas(cls):
        """Da mais nova para a mais antiga."""
        return cls._buscar_varios("1 = 1", (), ordem="id DESC")

    @classmethod
    def listar_por_registro(cls, registro_id):
        return cls._buscar_varios("registro_id = ?", (registro_id,))
