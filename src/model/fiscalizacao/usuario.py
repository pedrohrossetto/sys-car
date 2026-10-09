from model.fiscalizacao.conexao import consultar, consultar_um, executar
from model.fiscalizacao.fonte import FonteDeteccao
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL
);
"""


class Usuario(FonteDeteccao):
    """Pessoa que denuncia desmatamento."""

    def __init__(self, nome, cpf, email, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email

    # ---- Factory Method ----
    def criar_registro(self, propriedade_id, descricao, latitude, longitude, data):
        return RegistroDesmatamento(
            propriedade_id, descricao, data, latitude, longitude, usuario_id=self.id
        )

    def reportar_desmatamento(self, propriedade_id, descricao, latitude, longitude,
                              data, evidencias):
        """Denúncia de pessoa precisa de pelo menos uma evidência."""
        if not evidencias:
            raise ValueError("Denúncia de usuário exige pelo menos uma evidência.")
        return self.criar_registro(propriedade_id, descricao, latitude, longitude, data)

    # ---- persistência ----
    def salvar(self):
        if self.id is None:
            self.id = executar(
                "INSERT INTO usuarios (nome, cpf, email) VALUES (?, ?, ?)",
                (self.nome, self.cpf, self.email),
            )
        else:
            executar(
                "UPDATE usuarios SET nome = ?, cpf = ?, email = ? WHERE id = ?",
                (self.nome, self.cpf, self.email, self.id),
            )

    def deletar(self):
        executar("DELETE FROM usuarios WHERE id = ?", (self.id,))

    @staticmethod
    def buscar_por_id(id):
        linha = consultar_um("SELECT nome, cpf, email, id FROM usuarios WHERE id = ?", (id,))
        return Usuario(*linha) if linha else None

    @staticmethod
    def buscar_por_cpf(cpf):
        linha = consultar_um("SELECT nome, cpf, email, id FROM usuarios WHERE cpf = ?", (cpf,))
        return Usuario(*linha) if linha else None

    @staticmethod
    def listar_todos():
        linhas = consultar("SELECT nome, cpf, email, id FROM usuarios ORDER BY id")
        return [Usuario(*l) for l in linhas]
