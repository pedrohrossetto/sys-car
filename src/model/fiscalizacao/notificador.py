from datetime import date

from model.fiscalizacao.notificacao import Notificacao
from model.fiscalizacao.observador import ObservadorAlerta
from model.fiscalizacao.unidade_competente import UnidadeCompetente


class NotificadorUnidades(ObservadorAlerta):
    """Observador que cria uma notificação para cada unidade competente."""

    def atualizar(self, registro, evento):
        mensagem = (
            f"Alerta {registro.id} ({evento}): status {registro.status}. "
            f"{registro.descricao[:80]}"
        )
        hoje = date.today().isoformat()
        for unidade in UnidadeCompetente.listar_todos():
            Notificacao(registro.id, unidade.id, hoje, mensagem).salvar()
