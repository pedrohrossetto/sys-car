from model.base import ModeloBase
from model.fiscalizacao.status import StatusAlerta, estado_de

SCHEMA = """
CREATE TABLE IF NOT EXISTS registros_desmatamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    data TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('PENDENTE', 'CONFIRMADO', 'RESOLVIDO', 'CANCELADO')),
    latitude REAL NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    propriedade_id INTEGER NOT NULL
        REFERENCES propriedades_rurais(id) ON DELETE CASCADE,
    satelite_id INTEGER REFERENCES satelites(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    CHECK ((satelite_id IS NULL) <> (usuario_id IS NULL))
);
"""


class RegistroDesmatamento(ModeloBase):
    """Alerta de desmatamento. As coordenadas ficam embutidas (ADR-F04)."""

    TABELA = "registros_desmatamento"
    COLUNAS = (
        "descricao", "data", "status", "latitude", "longitude",
        "propriedade_id", "satelite_id", "usuario_id",
    )

    def __init__(self, propriedade_id, descricao, data, latitude, longitude,
                 satelite_id=None, usuario_id=None, status="PENDENTE", id=None):
        self.id = id
        self.propriedade_id = propriedade_id
        self.descricao = descricao
        self.data = data
        self.latitude = latitude
        self.longitude = longitude
        self.satelite_id = satelite_id
        self.usuario_id = usuario_id
        self.status = StatusAlerta(status).value

    @property
    def estado(self):
        return estado_de(self.status)

    def mudar_status(self, novo_status):
        """State: o estado atual decide se a transição é permitida."""
        self.status = self.estado.ir_para(novo_status).STATUS.value

    # ---- buscas específicas ----
    @classmethod
    def listar_por_propriedade(cls, propriedade_id):
        return cls._buscar_varios("propriedade_id = ?", (propriedade_id,))

    @classmethod
    def existe_da_fonte(cls, coluna, fonte_id):
        """True se algum registro veio do satélite/usuário informado."""
        if coluna not in ("satelite_id", "usuario_id"):
            raise ValueError("coluna inválida")
        return cls._existe(f"{coluna} = ?", (fonte_id,))
