from model.fiscalizacao.conexao import consultar, consultar_um, executar
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

_COLUNAS = (
    "id, descricao, data, status, latitude, longitude, "
    "propriedade_id, satelite_id, usuario_id"
)


class RegistroDesmatamento:
    """Alerta de desmatamento. As coordenadas ficam embutidas (ADR-F04)."""

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

    def salvar(self):
        valores = (
            self.descricao, self.data, self.status, self.latitude, self.longitude,
            self.propriedade_id, self.satelite_id, self.usuario_id,
        )
        if self.id is None:
            self.id = executar(
                "INSERT INTO registros_desmatamento (descricao, data, status, latitude, "
                "longitude, propriedade_id, satelite_id, usuario_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                valores,
            )
        else:
            executar(
                "UPDATE registros_desmatamento SET descricao = ?, data = ?, status = ?, "
                "latitude = ?, longitude = ?, propriedade_id = ?, satelite_id = ?, "
                "usuario_id = ? WHERE id = ?",
                valores + (self.id,),
            )

    @staticmethod
    def _de_linha(linha):
        id, descricao, data, status, lat, lon, prop, sat, usu = linha
        return RegistroDesmatamento(prop, descricao, data, lat, lon, sat, usu, status, id)

    @staticmethod
    def buscar_por_id(id):
        linha = consultar_um(
            f"SELECT {_COLUNAS} FROM registros_desmatamento WHERE id = ?", (id,)
        )
        return RegistroDesmatamento._de_linha(linha) if linha else None

    @staticmethod
    def listar_todos():
        linhas = consultar(f"SELECT {_COLUNAS} FROM registros_desmatamento ORDER BY id")
        return [RegistroDesmatamento._de_linha(l) for l in linhas]

    @staticmethod
    def listar_por_propriedade(propriedade_id):
        linhas = consultar(
            f"SELECT {_COLUNAS} FROM registros_desmatamento "
            "WHERE propriedade_id = ? ORDER BY id",
            (propriedade_id,),
        )
        return [RegistroDesmatamento._de_linha(l) for l in linhas]

    @staticmethod
    def existe_da_fonte(coluna, fonte_id):
        """True se algum registro veio do satélite/usuário informado."""
        if coluna not in ("satelite_id", "usuario_id"):
            raise ValueError("coluna inválida")
        return consultar_um(
            f"SELECT 1 FROM registros_desmatamento WHERE {coluna} = ? LIMIT 1", (fonte_id,)
        ) is not None
