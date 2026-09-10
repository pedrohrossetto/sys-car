from model.propriedade_rural import PropriedadeRural
from model.proprietario import Proprietario


class PropriedadeRuralController:
    # Mesmo padrão (resultado, erro) dos outros controllers.
    def criar(self, nome, proprietario_id, cadastro_publico=None):
        if not nome:
            return None, "Nome é obrigatório."
        if not Proprietario.buscar_por_id(proprietario_id):
            return None, "Proprietário não encontrado."
        propriedade = PropriedadeRural(nome, proprietario_id, cadastro_publico)
        propriedade.salvar()
        return propriedade, None

    def buscar_por_id(self, id):
        return PropriedadeRural.buscar_por_id(id)

    def atualizar(self, id, nome, proprietario_id, cadastro_publico):
        propriedade = PropriedadeRural.buscar_por_id(id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        if not Proprietario.buscar_por_id(proprietario_id):
            return None, "Proprietário não encontrado."
        propriedade.nome = nome
        propriedade.proprietario_id = proprietario_id
        propriedade.cadastro_publico = cadastro_publico
        propriedade.salvar()
        return propriedade, None

    def excluir(self, id):
        propriedade = PropriedadeRural.buscar_por_id(id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        propriedade.deletar()
        return True, None