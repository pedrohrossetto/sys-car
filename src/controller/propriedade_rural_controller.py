from model.propriedade_rural import PropriedadeRural
from model.proprietario import Proprietario


class PropriedadeRuralController:
    # Mesmo padrão (resultado, erro) dos outros controllers.
    def criar(self, nome, proprietario_id, cadastro_publico=None):
        dados, erro = self._validar(nome, proprietario_id, cadastro_publico)
        if erro:
            return None, erro
        propriedade = PropriedadeRural(**dados)
        propriedade.salvar()
        return propriedade, None

    def buscar_por_id(self, id):
        return PropriedadeRural.buscar_por_id(id)

    def listar(self):
        return PropriedadeRural.listar_todos()

    def atualizar(self, id, nome, proprietario_id, cadastro_publico=None):
        propriedade = PropriedadeRural.buscar_por_id(id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        dados, erro = self._validar(nome, proprietario_id, cadastro_publico)
        if erro:
            return None, erro
        for campo, valor in dados.items():
            setattr(propriedade, campo, valor)
        propriedade.salvar()
        return propriedade, None

    def excluir(self, id):
        propriedade = PropriedadeRural.buscar_por_id(id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        propriedade.deletar()
        return True, None

    def _validar(self, nome, proprietario_id, cadastro_publico):
        nome = (nome or "").strip()
        if not nome:
            return None, "Nome é obrigatório."
        if proprietario_id is None or not Proprietario.buscar_por_id(proprietario_id):
            return None, "Proprietário não encontrado."
        cadastro_publico = (cadastro_publico or "").strip() or None
        return {
            "nome": nome,
            "proprietario_id": int(proprietario_id),
            "cadastro_publico": cadastro_publico,
        }, None
