from controller.fiscalizacao.propriedades import buscar_propriedade, listar_propriedades
from model.fiscalizacao.evidencia import TIPOS_EVIDENCIA, Evidencia
from model.fiscalizacao.notificador import NotificadorUnidades
from model.fiscalizacao.observador import PublicadorAlertas
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.regras import converter_coordenada, data_iso, texto_obrigatorio
from model.fiscalizacao.satelite import Satelite
from model.fiscalizacao.status import StatusAlerta, TransicaoInvalida
from model.fiscalizacao.usuario import Usuario


class AlertaController:
    """Registro e exame de alertas de desmatamento.

    Usa o Factory Method das fontes para criar o registro, o State para
    mudar o status e o Observer (publicador) para avisar as unidades.
    """

    def __init__(self, publicador=None):
        if publicador is None:
            publicador = PublicadorAlertas()
            publicador.inscrever(NotificadorUnidades())
        self.publicador = publicador

    # ---------------- criação ----------------
    def registrar_por_satelite(self, satelite_id, propriedade_id, descricao,
                               latitude, longitude, data=None):
        satelite = Satelite.buscar_por_id(satelite_id) if satelite_id is not None else None
        if not satelite:
            return None, "Satélite não encontrado."
        return self._registrar(
            lambda dados: satelite.detectar_desmatamento(**dados),
            propriedade_id, descricao, latitude, longitude, data, evidencias=[],
        )

    def registrar_por_usuario(self, usuario_id, propriedade_id, descricao,
                              latitude, longitude, evidencias, data=None):
        """evidencias: lista de pares (tipo, link)."""
        usuario = Usuario.buscar_por_id(usuario_id) if usuario_id is not None else None
        if not usuario:
            return None, "Usuário não encontrado."
        return self._registrar(
            lambda dados: usuario.reportar_desmatamento(**dados, evidencias=evidencias),
            propriedade_id, descricao, latitude, longitude, data, evidencias,
        )

    def _registrar(self, fabricar, propriedade_id, descricao, latitude, longitude,
                   data, evidencias):
        if not buscar_propriedade(propriedade_id):
            return None, "Propriedade não encontrada."
        try:
            dados = {
                "propriedade_id": int(propriedade_id),
                "descricao": texto_obrigatorio(descricao, "Descrição"),
                "latitude": converter_coordenada(latitude, "Latitude", 90),
                "longitude": converter_coordenada(longitude, "Longitude", 180),
                "data": data_iso(data),
            }
            evidencias = [self._validar_evidencia(t, l) for t, l in evidencias]
            registro = fabricar(dados)
        except ValueError as erro:
            return None, str(erro)
        registro.salvar()
        for tipo, link in evidencias:
            Evidencia(registro.id, tipo, link, dados["data"]).salvar()
        self.publicador.notificar(registro, "novo alerta")
        return registro, None

    # ---------------- evidências ----------------
    def tipos_evidencia(self):
        return TIPOS_EVIDENCIA

    def adicionar_evidencia(self, registro_id, tipo, link):
        registro = RegistroDesmatamento.buscar_por_id(registro_id)
        if not registro:
            return None, "Alerta não encontrado."
        try:
            tipo, link = self._validar_evidencia(tipo, link)
        except ValueError as erro:
            return None, str(erro)
        evidencia = Evidencia(registro.id, tipo, link, data_iso())
        evidencia.salvar()
        return evidencia, None

    def evidencias_de(self, registro_id):
        return Evidencia.listar_por_registro(registro_id)

    @staticmethod
    def _validar_evidencia(tipo, link):
        return texto_obrigatorio(tipo, "Tipo da evidência"), texto_obrigatorio(link, "Link da evidência")

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

    # ---------------- consultas ----------------
    def buscar_por_id(self, id):
        return RegistroDesmatamento.buscar_por_id(id)

    def listar(self, incluir_finalizados=True):
        registros = RegistroDesmatamento.listar_todos()
        if incluir_finalizados:
            return registros
        return [r for r in registros if not r.estado.finalizado]

    def descrever_origem(self, registro):
        if registro.satelite_id is not None:
            satelite = Satelite.buscar_por_id(registro.satelite_id)
            return f"Satélite: {satelite.nome if satelite else registro.satelite_id}"
        usuario = Usuario.buscar_por_id(registro.usuario_id)
        return f"Usuário: {usuario.nome if usuario else registro.usuario_id}"

    def listar_propriedades(self):
        return listar_propriedades()

    def status_possiveis(self):
        return [s.value for s in StatusAlerta]
