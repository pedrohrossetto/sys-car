from controller.fiscalizacao.propriedades import (
    buscar_propriedade, listar_areas, listar_propriedades, propriedade_no_ponto,
)
from model.fiscalizacao.notificador import NotificadorUnidades
from model.fiscalizacao.observador import PublicadorAlertas
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.regras import converter_coordenada, data_iso, texto_obrigatorio
from model.fiscalizacao.status import StatusAlerta, TransicaoInvalida

# Um só notificador para o publicador único. Como inscrever() ignora
# observador repetido, criar vários controllers não duplica os avisos.
_NOTIFICADOR_UNIDADES = NotificadorUnidades()


class AlertaController:
    """CRUD e exame de alertas de desmatamento (ADR-F12 e ADR-F14).

    O alerta é um ponto clicado no mapa. A propriedade é a que contém o
    ponto (ou nenhuma). Depois de criado, o ponto não muda.

    Usa o State para mudar o status e o Observer (publicador) para avisar
    as unidades. Sem publicador no construtor, usa o Singleton
    ``PublicadorAlertas.instancia()``.
    """

    def __init__(self, publicador=None):
        if publicador is None:
            publicador = PublicadorAlertas.instancia()
            publicador.inscrever(_NOTIFICADOR_UNIDADES)
        self.publicador = publicador

    # ---------------- CRUD ----------------
    def criar(self, descricao, latitude, longitude, data=None):
        """O ponto define a propriedade (ADR-F14). Fora de toda área: alerta sem propriedade."""
        try:
            dados = self._validar(descricao, data)
            lat = converter_coordenada(latitude, "Latitude", 90)
            lon = converter_coordenada(longitude, "Longitude", 180)
        except ValueError as erro:
            return None, str(erro)
        propriedade = propriedade_no_ponto(lat, lon)
        registro = RegistroDesmatamento(
            propriedade.id if propriedade else None, latitude=lat, longitude=lon, **dados)
        registro.salvar()
        self.publicador.notificar(registro, "novo alerta")
        return registro, None

    def atualizar(self, id, descricao, data=None):
        """Altera descrição e data. Ponto, propriedade e status (State) não mudam."""
        registro = RegistroDesmatamento.buscar_por_id(id) if id is not None else None
        if not registro:
            return None, "Alerta não encontrado."
        try:
            dados = self._validar(descricao, data)
        except ValueError as erro:
            return None, str(erro)
        for campo, valor in dados.items():
            setattr(registro, campo, valor)
        registro.salvar()
        return registro, None

    def excluir(self, id):
        """Apaga o alerta. O banco apaga em cascata as notificações e os embargos dele."""
        registro = RegistroDesmatamento.buscar_por_id(id) if id is not None else None
        if not registro:
            return None, "Alerta não encontrado."
        registro.deletar()
        return True, None

    def buscar_por_id(self, id):
        return RegistroDesmatamento.buscar_por_id(id)

    def listar(self, incluir_finalizados=True):
        registros = RegistroDesmatamento.listar_todos()
        if incluir_finalizados:
            return registros
        return [r for r in registros if not r.estado.finalizado]

    @staticmethod
    def _validar(descricao, data):
        return {"descricao": texto_obrigatorio(descricao, "Descrição"), "data": data_iso(data)}

    # ---------------- exame (State) ----------------
    def mudar_status(self, registro_id, novo_status):
        registro = RegistroDesmatamento.buscar_por_id(registro_id)
        if not registro:
            return None, "Alerta não encontrado."
        try:
            registro.mudar_status(novo_status)
        except TransicaoInvalida as erro:
            return None, str(erro)
        registro.salvar()
        self.publicador.notificar(registro, f"status alterado para {registro.status}")
        return registro, None

    def transicoes_possiveis(self, registro_id):
        registro = RegistroDesmatamento.buscar_por_id(registro_id)
        if not registro:
            return []
        return [status.value for status in registro.estado.PROXIMOS]

    # ---------------- apoio ----------------
    def listar_propriedades(self):
        return listar_propriedades()

    def listar_areas(self):
        return listar_areas()

    def propriedade_no_ponto(self, latitude, longitude):
        """Para a tela mostrar, antes de salvar, onde o ponto caiu."""
        return propriedade_no_ponto(latitude, longitude)

    def descrever_local(self, registro):
        propriedade = buscar_propriedade(registro.propriedade_id)
        return propriedade.nome if propriedade else "fora de propriedade cadastrada"

    def status_possiveis(self):
        return [s.value for s in StatusAlerta]

    def banco_desatualizado(self):
        return RegistroDesmatamento.schema_desatualizado()
