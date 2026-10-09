from model.fiscalizacao.conexao import consultar, consultar_um, executar

SCHEMA = """
CREATE TABLE IF NOT EXISTS unidades_competentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo_unidade_orgao TEXT,
    contato TEXT
);
"""


class UnidadeCompetente:
    """Órgão que examina alertas e embarga propriedades (ex.: IBAMA, FEPAM)."""

    def __init__(self, nome, tipo_unidade_orgao=None, contato=None, id=None):
        self.id = id
        self.nome = nome
        self.tipo_unidade_orgao = tipo_unidade_orgao
        self.contato = contato

    def salvar(self):
        valores = (self.nome, self.tipo_unidade_orgao, self.contato)
        if self.id is None:
            self.id = executar(
                "INSERT INTO unidades_competentes (nome, tipo_unidade_orgao, contato) "
                "VALUES (?, ?, ?)",
                valores,
            )
        else:
            executar(
                "UPDATE unidades_competentes SET nome = ?, tipo_unidade_orgao = ?, "
                "contato = ? WHERE id = ?",
                valores + (self.id,),
            )

    def deletar(self):
        executar("DELETE FROM unidades_competentes WHERE id = ?", (self.id,))

    @staticmethod
    def buscar_por_id(id):
        linha = consultar_um(
            "SELECT nome, tipo_unidade_orgao, contato, id FROM unidades_competentes "
            "WHERE id = ?",
            (id,),
        )
        return UnidadeCompetente(*linha) if linha else None

    @staticmethod
    def listar_todos():
        linhas = consultar(
            "SELECT nome, tipo_unidade_orgao, contato, id FROM unidades_competentes ORDER BY id"
        )
        return [UnidadeCompetente(*l) for l in linhas]
