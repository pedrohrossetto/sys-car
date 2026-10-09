from model.base import ModeloBase

SCHEMA = """
CREATE TABLE IF NOT EXISTS localizacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL,
    longitude REAL,
    altitude REAL,
    poligono_geometria TEXT,
    propriedade_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (propriedade_id) REFERENCES propriedades_rurais(id)
        ON DELETE CASCADE
);
"""


class Localizacao(ModeloBase):
    TABELA = "localizacoes"
    COLUNAS = ("latitude", "longitude", "altitude", "poligono_geometria", "propriedade_id")

    def __init__(
        self, propriedade_id, latitude=None, longitude=None, altitude=None,
        poligono_geometria=None, id=None,
    ):
        self.id = id
        # Chave estrangeira: cada localização pertence a uma propriedade rural (1:1).
        self.propriedade_id = propriedade_id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        # Texto normalizado 'lat,lon;lat,lon;...' (veja model/coordenadas.py).
        self.poligono_geometria = poligono_geometria

    @classmethod
    def buscar_por_propriedade(cls, propriedade_id):
        return cls._buscar_um("propriedade_id = ?", (propriedade_id,))

    @classmethod
    def listar_todas(cls):
        return cls.listar_todos()
