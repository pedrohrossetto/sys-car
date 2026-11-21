from model.base import ModeloBase

SCHEMA = """
CREATE TABLE IF NOT EXISTS declaracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propriedade_id INTEGER NOT NULL
        REFERENCES propriedades_rurais(id) ON DELETE CASCADE,
    data TEXT NOT NULL,
    resultado TEXT NOT NULL CHECK (resultado IN ('EMITIDA', 'NEGADA')),
    motivo TEXT
);
"""


class Declaracao(ModeloBase):
    """Pedido de declaração de conformidade ambiental (emitida ou negada)."""

    TABELA = "declaracoes"
    COLUNAS = ("propriedade_id", "data", "resultado", "motivo")

    def __init__(self, propriedade_id, data, resultado, motivo=None, id=None):
        self.id = id
        self.propriedade_id = propriedade_id
        self.data = data
        self.resultado = resultado
        self.motivo = motivo

    @property
    def emitida(self):
        return self.resultado == "EMITIDA"

    # ---- buscas específicas ----
    @classmethod
    def listar_todas(cls):
        """Da mais nova para a mais antiga."""
        return cls._buscar_varios("1 = 1", (), ordem="id DESC")
