from model.fiscalizacao.conexao import consultar, consultar_um, executar

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

_SELECT = "SELECT propriedade_id, data, resultado, motivo, id FROM declaracoes"


class Declaracao:
    """Pedido de declaração de conformidade ambiental (emitida ou negada)."""

    def __init__(self, propriedade_id, data, resultado, motivo=None, id=None):
        self.id = id
        self.propriedade_id = propriedade_id
        self.data = data
        self.resultado = resultado
        self.motivo = motivo

    @property
    def emitida(self):
        return self.resultado == "EMITIDA"

    def salvar(self):
        self.id = executar(
            "INSERT INTO declaracoes (propriedade_id, data, resultado, motivo) "
            "VALUES (?, ?, ?, ?)",
            (self.propriedade_id, self.data, self.resultado, self.motivo),
        )

    @staticmethod
    def buscar_por_id(id):
        linha = consultar_um(f"{_SELECT} WHERE id = ?", (id,))
        return Declaracao(*linha) if linha else None

    @staticmethod
    def listar_todas():
        return [Declaracao(*l) for l in consultar(f"{_SELECT} ORDER BY id DESC")]
