from model.base import ModeloBase

SCHEMA = """
CREATE TABLE IF NOT EXISTS evidencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registro_id INTEGER NOT NULL
        REFERENCES registros_desmatamento(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL,
    link TEXT NOT NULL,
    data TEXT NOT NULL
);
"""

TIPOS_EVIDENCIA = ("Foto", "Vídeo", "Documento", "Imagem de satélite", "Outro")


class Evidencia(ModeloBase):
    TABELA = "evidencias"
    COLUNAS = ("registro_id", "tipo", "link", "data")

    def __init__(self, registro_id, tipo, link, data, id=None):
        self.id = id
        self.registro_id = registro_id
        self.tipo = tipo
        self.link = link
        self.data = data

    # ---- buscas específicas ----
    @classmethod
    def listar_por_registro(cls, registro_id):
        return cls._buscar_varios("registro_id = ?", (registro_id,))
