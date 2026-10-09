import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.fonte_controller import FonteController
from controller.fiscalizacao.unidade_controller import UnidadeController
from model.fiscalizacao.observador import ObservadorAlerta, PublicadorAlertas
from test_fiscalizacao_apoio import BancoTemporario


class ObservadorDeTeste(ObservadorAlerta):
    def __init__(self):
        self.eventos = []

    def atualizar(self, registro, evento):
        self.eventos.append((registro.id, evento))


class TestPublicador(unittest.TestCase):
    def test_inscrever_notificar_e_cancelar(self):
        publicador = PublicadorAlertas()
        observador = ObservadorDeTeste()
        publicador.inscrever(observador)
        publicador.inscrever(observador)  # não duplica

        class Registro:
            id = 7

        publicador.notificar(Registro(), "teste")
        self.assertEqual(observador.eventos, [(7, "teste")])
        publicador.cancelar_inscricao(observador)
        publicador.notificar(Registro(), "outro")
        self.assertEqual(len(observador.eventos), 1)


class TestAlertas(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.fontes = FonteController()
        self.alertas = AlertaController()
        self.unidades = UnidadeController()
        self.satelite, _ = self.fontes.criar_satelite("Landsat 9", "NASA")
        self.usuario, _ = self.fontes.criar_usuario("Joana", "529.982.247-25", "joana@ex.com")

    def novo_por_satelite(self, **extra):
        dados = dict(satelite_id=self.satelite.id, propriedade_id=self.propriedade_id,
                     descricao="Corte raso", latitude="-28,2", longitude="-52.4")
        dados.update(extra)
        return self.alertas.registrar_por_satelite(**dados)

    def test_satelite_cria_alerta_pendente_sem_evidencia(self):
        registro, erro = self.novo_por_satelite()
        self.assertIsNone(erro)
        salvo = self.alertas.buscar_por_id(registro.id)
        self.assertEqual((salvo.status, salvo.latitude, salvo.satelite_id, salvo.usuario_id),
                         ("PENDENTE", -28.2, self.satelite.id, None))

    def test_usuario_sem_evidencia_e_rejeitado(self):
        registro, erro = self.alertas.registrar_por_usuario(
            self.usuario.id, self.propriedade_id, "Queimada", 0, 0, evidencias=[])
        self.assertIsNone(registro)
        self.assertEqual(erro, "Denúncia de usuário exige pelo menos uma evidência.")
        self.assertEqual(self.contar("registros_desmatamento"), 0)

    def test_usuario_com_evidencia_grava_alerta_e_evidencias(self):
        registro, erro = self.alertas.registrar_por_usuario(
            self.usuario.id, self.propriedade_id, "Queimada", 0, 0,
            evidencias=[("Foto", "http://x/1.jpg"), ("Vídeo", "http://x/2.mp4")])
        self.assertIsNone(erro)
        self.assertEqual(registro.usuario_id, self.usuario.id)
        self.assertEqual([e.tipo for e in self.alertas.evidencias_de(registro.id)], ["Foto", "Vídeo"])

    def test_evidencia_com_link_vazio_e_rejeitada(self):
        _, erro = self.alertas.registrar_por_usuario(
            self.usuario.id, self.propriedade_id, "Queimada", 0, 0, evidencias=[("Foto", "  ")])
        self.assertEqual(erro, "Preencha o campo Link da evidência.")
        self.assertEqual(self.contar("registros_desmatamento"), 0)

    def test_validacoes_de_entrada(self):
        self.assertEqual(self.novo_por_satelite(latitude="91")[1], "Latitude deve estar entre -90 e 90.")
        self.assertEqual(self.novo_por_satelite(longitude="abc")[1], "Longitude deve ser um número.")
        self.assertEqual(self.novo_por_satelite(descricao="  ")[1], "Preencha o campo Descrição.")
        self.assertEqual(self.novo_por_satelite(propriedade_id=999)[1], "Propriedade não encontrada.")
        self.assertEqual(self.novo_por_satelite(propriedade_id=None)[1], "Propriedade não encontrada.")
        self.assertEqual(self.novo_por_satelite(data="31/12/2026")[1], "Data deve estar no formato AAAA-MM-DD.")
        self.assertEqual(self.novo_por_satelite(satelite_id=None)[1], "Satélite não encontrado.")
        self.assertEqual(self.contar("registros_desmatamento"), 0)

    def test_observer_notifica_cada_unidade_na_criacao_e_na_mudanca(self):
        self.unidades.criar("IBAMA")
        self.unidades.criar("FEPAM")
        registro, _ = self.novo_por_satelite()
        self.assertEqual(self.contar("notificacoes"), 2)
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.assertEqual(self.contar("notificacoes"), 4)
        self.assertIn("CONFIRMADO", self.unidades.listar_notificacoes()[0].mensagem)

    def test_observer_sem_unidades_nao_quebra(self):
        _, erro = self.novo_por_satelite()
        self.assertIsNone(erro)
        self.assertEqual(self.contar("notificacoes"), 0)

    def test_publicador_injetado_recebe_os_eventos(self):
        publicador = PublicadorAlertas()
        observador = ObservadorDeTeste()
        publicador.inscrever(observador)
        alertas = AlertaController(publicador)
        registro, _ = alertas.registrar_por_satelite(self.satelite.id, self.propriedade_id, "x", 0, 0)
        alertas.mudar_status(registro.id, "CANCELADO")
        self.assertEqual(observador.eventos, [
            (registro.id, "novo alerta"), (registro.id, "status alterado para CANCELADO")])

    def test_mudar_status_respeita_o_state(self):
        registro, _ = self.novo_por_satelite()
        self.assertEqual(self.alertas.transicoes_possiveis(registro.id), ["CONFIRMADO", "CANCELADO"])
        self.assertEqual(self.alertas.mudar_status(registro.id, "RESOLVIDO")[1],
                         "Não é possível mudar de PENDENTE para RESOLVIDO.")
        self.assertEqual(self.alertas.buscar_por_id(registro.id).status, "PENDENTE")
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.alertas.mudar_status(registro.id, "RESOLVIDO")
        self.assertEqual(self.alertas.transicoes_possiveis(registro.id), [])
        self.assertEqual(self.alertas.mudar_status(999, "CONFIRMADO")[1], "Alerta não encontrado.")

    def test_listar_sem_finalizados(self):
        a, _ = self.novo_por_satelite()
        b, _ = self.novo_por_satelite()
        self.alertas.mudar_status(b.id, "CANCELADO")
        self.assertEqual([r.id for r in self.alertas.listar(incluir_finalizados=False)], [a.id])
        self.assertEqual(len(self.alertas.listar()), 2)

    def test_adicionar_evidencia_a_alerta_existente(self):
        registro, _ = self.novo_por_satelite()
        _, erro = self.alertas.adicionar_evidencia(registro.id, "Foto", "http://x/3.jpg")
        self.assertIsNone(erro)
        self.assertEqual(len(self.alertas.evidencias_de(registro.id)), 1)
        self.assertEqual(self.alertas.adicionar_evidencia(999, "Foto", "x")[1], "Alerta não encontrado.")

    def test_descrever_origem(self):
        registro, _ = self.novo_por_satelite()
        self.assertEqual(self.alertas.descrever_origem(registro), "Satélite: Landsat 9")


class TestUnidades(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.unidades = UnidadeController()

    def test_unidade_crud(self):
        unidade, _ = self.unidades.criar("IBAMA")
        self.unidades.atualizar(unidade.id, "IBAMA RS", "Federal", "x@y.z")
        self.assertEqual(self.unidades.buscar_por_id(unidade.id).tipo_unidade_orgao, "Federal")
        self.assertEqual(self.unidades.criar(" ")[1], "Preencha o campo Nome.")
        self.assertEqual(self.unidades.excluir(unidade.id), (True, None))

    def test_marcar_notificacao_lida(self):
        self.unidades.criar("IBAMA")
        satelite, _ = FonteController().criar_satelite("Landsat")
        AlertaController().registrar_por_satelite(satelite.id, self.propriedade_id, "x", 0, 0)
        notificacao = self.unidades.listar_notificacoes()[0]
        self.assertEqual(notificacao.status, "ENVIADA")
        self.unidades.marcar_lida(notificacao.id)
        self.assertEqual(self.unidades.listar_notificacoes()[0].status, "LIDA")
        self.assertEqual(self.unidades.marcar_lida(999)[1], "Notificação não encontrada.")


if __name__ == "__main__":
    unittest.main()
