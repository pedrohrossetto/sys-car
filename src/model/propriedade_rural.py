from model.base import ModeloBase

# CONTRATO com a Frente 2 (Fiscalização): a tabela 'propriedades_rurais',
# as colunas id/nome/proprietario_id e os métodos buscar_por_id/listar_todos
# não podem mudar. Colunas novas precisam aceitar NULL ou ter DEFAULT.
SCHEMA = """
CREATE TABLE IF NOT EXISTS propriedades_rurais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cadastro_publico TEXT,
    proprietario_id INTEGER NOT NULL,
    FOREIGN KEY (proprietario_id) REFERENCES proprietarios(id)
        ON DELETE CASCADE
);
"""


class PropriedadeRural(ModeloBase):
    TABELA = "propriedades_rurais"
    COLUNAS = ("nome", "cadastro_publico", "proprietario_id")

    def __init__(self, nome, proprietario_id, cadastro_publico=None, id=None):
        self.id = id
        self.nome = nome
        self.cadastro_publico = cadastro_publico
        # Chave estrangeira: aponta para o proprietário dono desta propriedade.
        self.proprietario_id = proprietario_id
