from model.fiscalizacao.conexao import consultar, executar

SCHEMA = """
CREATE TABLE IF NOT EXISTS notificacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registro_id INTEGER NOT NULL
        REFERENCES registros_desmatamento(id) ON DELETE CASCADE,
    unidade_id INTEGER NOT NULL
        REFERENCES unidades_competentes(id) ON DELETE CASCADE,
    data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ENVIADA' CHECK (status IN ('ENVIADA', 'LIDA')),
    mensagem TEXT NOT NULL
);
"""

_SELECT = "SELECT registro_id, unidade_id, data, mensagem, status, id FROM notificacoes"


class Notificacao:
    def __init__(self, registro_id, unidade_id, data, mensagem, status="ENVIADA", id=None):
        self.id = id
        self.registro_id = registro_id
        self.unidade_id = unidade_id
        self.data = data
        self.mensagem = mensagem
        self.status = status

    def salvar(self):
        if self.id is None:
            self.id = executar(
                "INSERT INTO notificacoes (registro_id, unidade_id, data, status, mensagem) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.registro_id, self.unidade_id, self.data, self.status, self.mensagem),
            )
        else:
            executar("UPDATE notificacoes SET status = ? WHERE id = ?", (self.status, self.id))

    @staticmethod
    def buscar_por_id(id):
        linhas = consultar(f"{_SELECT} WHERE id = ?", (id,))
        return Notificacao(*linhas[0]) if linhas else None

    @staticmethod
    def listar_todas():
        return [Notificacao(*l) for l in consultar(f"{_SELECT} ORDER BY id DESC")]

    @staticmethod
    def listar_por_registro(registro_id):
        linhas = consultar(f"{_SELECT} WHERE registro_id = ? ORDER BY id", (registro_id,))
        return [Notificacao(*l) for l in linhas]
