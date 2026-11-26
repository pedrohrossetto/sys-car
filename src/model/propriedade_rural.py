from model.base import ModeloBase
from model.geometria import Poligono

# CONTRATO com a Frente 2 (Fiscalização): a tabela 'propriedades_rurais',
# as colunas id/nome/proprietario_id e os métodos buscar_por_id/listar_todos
# não podem mudar. Colunas novas precisam aceitar NULL ou ter DEFAULT.
#
# 'poligono' guarda a área da propriedade no texto 'lat,lon;lat,lon;...'.
# No banco ela aceita NULL (contrato acima), mas o controller a exige (ADR-C05).
SCHEMA = """
CREATE TABLE IF NOT EXISTS propriedades_rurais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cadastro_publico TEXT,
    proprietario_id INTEGER NOT NULL,
    poligono TEXT,
    FOREIGN KEY (proprietario_id) REFERENCES proprietarios(id)
        ON DELETE CASCADE
);
"""


class PropriedadeRural(ModeloBase):
    TABELA = "propriedades_rurais"
    COLUNAS = ("nome", "cadastro_publico", "proprietario_id", "poligono")

    def __init__(self, nome, proprietario_id, cadastro_publico=None, poligono=None, id=None):
        self.id = id
        self.nome = nome
        self.cadastro_publico = cadastro_publico
        # Chave estrangeira: aponta para o proprietário dono desta propriedade.
        self.proprietario_id = proprietario_id
        self.poligono = poligono

    # ---- área (ADR-C05): calculada a partir do polígono ----
    @property
    def area(self):
        """Poligono da propriedade, ou None se ela não tem área gravada."""
        return Poligono.de_texto(self.poligono) if self.poligono else None

    @property
    def centroide(self):
        """Centro da área (lat, lon). Substitui a latitude/longitude da antiga Localização."""
        return self.area.centroide() if self.poligono else None

    @property
    def area_ha(self):
        return self.area.area_ha() if self.poligono else None

    def contem(self, latitude, longitude):
        return bool(self.poligono) and self.area.contem(latitude, longitude)

    @classmethod
    def schema_desatualizado(cls):
        """True se o banco é da versão com a tabela 'localizacoes' (sem a coluna 'poligono')."""
        colunas = cls.colunas_no_banco()
        return bool(colunas) and "poligono" not in colunas
