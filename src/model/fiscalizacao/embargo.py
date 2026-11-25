from model.base import ModeloBase

# O índice único parcial garante no banco: no máximo UM embargo ativo por propriedade.
SCHEMA = """
CREATE TABLE IF NOT EXISTS embargos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propriedade_id INTEGER NOT NULL
        REFERENCES propriedades_rurais(id) ON DELETE CASCADE,
    unidade_id INTEGER NOT NULL REFERENCES unidades_competentes(id),
    registro_id INTEGER NOT NULL
        REFERENCES registros_desmatamento(id) ON DELETE CASCADE,
    data TEXT NOT NULL,
    motivo TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_embargo_ativo_por_propriedade
    ON embargos (propriedade_id) WHERE ativo = 1;
"""


class Embargo(ModeloBase):
    TABELA = "embargos"
    COLUNAS = ("propriedade_id", "unidade_id", "registro_id", "data", "motivo", "ativo")

    def __init__(self, propriedade_id, unidade_id, registro_id, data, motivo,
                 ativo=1, id=None):
        self.id = id
        self.propriedade_id = propriedade_id
        self.unidade_id = unidade_id
        self.registro_id = registro_id
        self.data = data
        self.motivo = motivo
        self.ativo = ativo

    # ---- buscas específicas ----
    @classmethod
    def listar_todos(cls):
        """Do mais novo para o mais antigo."""
        return cls._buscar_varios("1 = 1", (), ordem="id DESC")

    @classmethod
    def buscar_ativo(cls, propriedade_id):
        return cls._buscar_um("propriedade_id = ? AND ativo = 1", (propriedade_id,))

    @classmethod
    def existe_da_unidade(cls, unidade_id):
        return cls._existe("unidade_id = ?", (unidade_id,))
