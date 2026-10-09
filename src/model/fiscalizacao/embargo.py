from model.fiscalizacao.conexao import consultar, consultar_um, executar

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

_SELECT = (
    "SELECT propriedade_id, unidade_id, registro_id, data, motivo, ativo, id FROM embargos"
)


class Embargo:
    def __init__(self, propriedade_id, unidade_id, registro_id, data, motivo,
                 ativo=1, id=None):
        self.id = id
        self.propriedade_id = propriedade_id
        self.unidade_id = unidade_id
        self.registro_id = registro_id
        self.data = data
        self.motivo = motivo
        self.ativo = ativo

    def salvar(self):
        if self.id is None:
            self.id = executar(
                "INSERT INTO embargos (propriedade_id, unidade_id, registro_id, data, "
                "motivo, ativo) VALUES (?, ?, ?, ?, ?, ?)",
                (self.propriedade_id, self.unidade_id, self.registro_id, self.data,
                 self.motivo, self.ativo),
            )
        else:
            executar("UPDATE embargos SET ativo = ? WHERE id = ?", (self.ativo, self.id))

    @staticmethod
    def buscar_por_id(id):
        linha = consultar_um(f"{_SELECT} WHERE id = ?", (id,))
        return Embargo(*linha) if linha else None

    @staticmethod
    def buscar_ativo(propriedade_id):
        linha = consultar_um(f"{_SELECT} WHERE propriedade_id = ? AND ativo = 1", (propriedade_id,))
        return Embargo(*linha) if linha else None

    @staticmethod
    def listar_todos():
        return [Embargo(*l) for l in consultar(f"{_SELECT} ORDER BY id DESC")]

    @staticmethod
    def existe_da_unidade(unidade_id):
        return consultar_um(
            "SELECT 1 FROM embargos WHERE unidade_id = ? LIMIT 1", (unidade_id,)
        ) is not None
