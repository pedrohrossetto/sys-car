from model.fiscalizacao.conexao import consultar, executar

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


class Evidencia:
    def __init__(self, registro_id, tipo, link, data, id=None):
        self.id = id
        self.registro_id = registro_id
        self.tipo = tipo
        self.link = link
        self.data = data

    def salvar(self):
        self.id = executar(
            "INSERT INTO evidencias (registro_id, tipo, link, data) VALUES (?, ?, ?, ?)",
            (self.registro_id, self.tipo, self.link, self.data),
        )

    @staticmethod
    def listar_por_registro(registro_id):
        linhas = consultar(
            "SELECT registro_id, tipo, link, data, id FROM evidencias "
            "WHERE registro_id = ? ORDER BY id",
            (registro_id,),
        )
        return [Evidencia(*l) for l in linhas]
