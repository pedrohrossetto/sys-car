from model.documento import VALIDADORES
from model.proprietario import Proprietario


class ProprietarioController:
    # Padrão de retorno dos métodos de escrita:
    # (resultado, erro) -> se deu certo: (objeto/True, None).
    #                       se deu errado: (None, "mensagem de erro").
    # Isso permite à view exibir o erro sem precisar de try/except.
    def criar(self, nome, tipo, cpf=None, cnpj=None):
        dados, erro = self._validar(nome, tipo, cpf, cnpj)
        if erro:
            return None, erro
        proprietario = Proprietario(**dados)
        proprietario.salvar()
        return proprietario, None

    def buscar_por_id(self, id):
        return Proprietario.buscar_por_id(id)

    def listar(self):
        return Proprietario.listar_todos()

    def atualizar(self, id, nome, tipo, cpf=None, cnpj=None):
        proprietario = Proprietario.buscar_por_id(id)
        if not proprietario:
            return None, "Proprietário não encontrado."
        dados, erro = self._validar(nome, tipo, cpf, cnpj, id_atual=proprietario.id)
        if erro:
            return None, erro
        for campo, valor in dados.items():
            setattr(proprietario, campo, valor)
        proprietario.salvar()
        return proprietario, None

    def excluir(self, id):
        proprietario = Proprietario.buscar_por_id(id)
        if not proprietario:
            return None, "Proprietário não encontrado."
        proprietario.deletar()
        return True, None

    def banco_desatualizado(self):
        return Proprietario.schema_desatualizado()

    def _validar(self, nome, tipo, cpf, cnpj, id_atual=None):
        nome = (nome or "").strip()
        if not nome:
            return None, "Nome é obrigatório."
        # Strategy: o validador é escolhido pelo tipo, sem if/elif.
        validador = VALIDADORES.get(tipo)
        if validador is None:
            return None, "Tipo deve ser PF ou PJ."
        documento = validador.normalizar(cpf if tipo == "PF" else cnpj)
        if not documento:
            return None, f"{validador.nome} é obrigatório para {tipo}."
        if not validador.valido(documento):
            return None, f"{validador.nome} inválido."
        existente = Proprietario.buscar_por_documento(tipo, documento)
        if existente and existente.id != id_atual:
            return None, f"{validador.nome} já cadastrado."
        return {
            "nome": nome,
            "tipo": tipo,
            "cpf": documento if tipo == "PF" else None,
            "cnpj": documento if tipo == "PJ" else None,
        }, None
