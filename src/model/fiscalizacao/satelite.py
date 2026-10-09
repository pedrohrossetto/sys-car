from model.fiscalizacao.conexao import consultar, consultar_um, executar
from model.fiscalizacao.fonte import FonteDeteccao
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento

SCHEMA = """
CREATE TABLE IF NOT EXISTS satelites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    entidade_responsavel TEXT
);
"""


class Satelite(FonteDeteccao):
    def __init__(self, nome, entidade_responsavel=None, id=None):
        self.id = id
        self.nome = nome
        self.entidade_responsavel = entidade_responsavel

    # ---- Factory Method ----
    def criar_registro(self, propriedade_id, descricao, latitude, longitude, data):
        return RegistroDesmatamento(
            propriedade_id, descricao, data, latitude, longitude, satelite_id=self.id
        )

    def detectar_desmatamento(self, propriedade_id, descricao, latitude, longitude, data):
        """Satélite não precisa de evidência anexada: a própria imagem é a detecção."""
        return self.criar_registro(propriedade_id, descricao, latitude, longitude, data)

    # ---- persistência ----
    def salvar(self):
        if self.id is None:
            self.id = executar(
                "INSERT INTO satelites (nome, entidade_responsavel) VALUES (?, ?)",
                (self.nome, self.entidade_responsavel),
            )
        else:
            executar(
                "UPDATE satelites SET nome = ?, entidade_responsavel = ? WHERE id = ?",
                (self.nome, self.entidade_responsavel, self.id),
            )

    def deletar(self):
        executar("DELETE FROM satelites WHERE id = ?", (self.id,))

    @staticmethod
    def buscar_por_id(id):
        linha = consultar_um(
            "SELECT nome, entidade_responsavel, id FROM satelites WHERE id = ?", (id,)
        )
        return Satelite(*linha) if linha else None

    @staticmethod
    def listar_todos():
        linhas = consultar("SELECT nome, entidade_responsavel, id FROM satelites ORDER BY id")
        return [Satelite(*l) for l in linhas]
