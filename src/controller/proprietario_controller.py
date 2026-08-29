from model.proprietario import Proprietario


class ProprietarioController:
    def criar(self, nome, cpf, cnpj=None):
        if not nome or not cpf:
            return None, "Nome e CPF são obrigatórios."
        if Proprietario.buscar_por_cpf(cpf):
            return None, "CPF já cadastrado."
        proprietario = Proprietario(nome, cpf, cnpj)
        proprietario.salvar()
        return proprietario, None

    def listar(self):
        return Proprietario.listar_todos()

    def buscar_por_id(self, id):
        return Proprietario.buscar_por_id(id)

    def buscar_por_cpf(self, cpf):
        return Proprietario.buscar_por_cpf(cpf)

    def atualizar(self, id, nome, cpf, cnpj):
        proprietario = Proprietario.buscar_por_id(id)
        if not proprietario:
            return None, "Proprietário não encontrado."
        outro = Proprietario.buscar_por_cpf(cpf)
        if outro and outro.id != id:
            return None, "CPF já cadastrado para outro proprietário."
        proprietario.nome = nome
        proprietario.cpf = cpf
        proprietario.cnpj = cnpj
        proprietario.salvar()
        return proprietario, None

    def excluir(self, id):
        proprietario = Proprietario.buscar_por_id(id)
        if not proprietario:
            return None, "Proprietário não encontrado."
        proprietario.deletar()
        return True, None
