from model.fiscalizacao.embargo import Embargo
from model.fiscalizacao.notificacao import Notificacao
from model.fiscalizacao.regras import texto_obrigatorio
from model.fiscalizacao.unidade_competente import UnidadeCompetente


class UnidadeController:
    """Cadastro de unidades competentes e leitura das notificações."""

    def criar(self, nome, tipo_unidade_orgao=None, contato=None):
        try:
            nome = texto_obrigatorio(nome, "Nome")
        except ValueError as erro:
            return None, str(erro)
        unidade = UnidadeCompetente(
            nome, (tipo_unidade_orgao or "").strip() or None, (contato or "").strip() or None
        )
        unidade.salvar()
        return unidade, None

    def atualizar(self, id, nome, tipo_unidade_orgao=None, contato=None):
        unidade = UnidadeCompetente.buscar_por_id(id)
        if not unidade:
            return None, "Unidade não encontrada."
        try:
            unidade.nome = texto_obrigatorio(nome, "Nome")
        except ValueError as erro:
            return None, str(erro)
        unidade.tipo_unidade_orgao = (tipo_unidade_orgao or "").strip() or None
        unidade.contato = (contato or "").strip() or None
        unidade.salvar()
        return unidade, None

    def excluir(self, id):
        unidade = UnidadeCompetente.buscar_por_id(id)
        if not unidade:
            return None, "Unidade não encontrada."
        if Embargo.existe_da_unidade(id):
            return None, "Esta unidade aplicou embargos e não pode ser excluída."
        unidade.deletar()
        return True, None

    def buscar_por_id(self, id):
        return UnidadeCompetente.buscar_por_id(id)

    def listar(self):
        return UnidadeCompetente.listar_todos()

    def listar_notificacoes(self):
        return Notificacao.listar_todas()

    def marcar_lida(self, notificacao_id):
        notificacao = Notificacao.buscar_por_id(notificacao_id)
        if not notificacao:
            return None, "Notificação não encontrada."
        notificacao.status = "LIDA"
        notificacao.salvar()
        return notificacao, None
