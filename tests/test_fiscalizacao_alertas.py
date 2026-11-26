import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.conformidade_controller import ConformidadeController
from controller.fiscalizacao.unidade_controller import UnidadeController
from database.database import get_connection
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


class TestPublicadorSingleton(unittest.TestCase):
    def test_duas_chamadas_devolvem_o_mesmo_objeto(self):
        self.assertIs(PublicadorAlertas.instancia(), PublicadorAlertas.instancia())

    def test_construtor_continua_criando_publicador_separado(self):
        self.assertIsNot(PublicadorAlertas(), PublicadorAlertas.instancia())

    def test_controllers_sem_publicador_usam_a_instancia_unica(self):
        self.assertIs(AlertaController().publicador, PublicadorAlertas.instancia())
        self.assertIs(AlertaController().publicador, AlertaController().publicador)


class TestAlertas(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.alertas = AlertaController()
        self.unidades = UnidadeController()

    def novo(self, **extra):
        """Alerta no centro da propriedade de teste (dentro da área dela)."""
        lat, lon = self.centro_da(self.propriedade_id)
        dados = dict(descricao="Corte raso", latitude=str(lat).replace(".", ","), longitude=lon)
        dados.update(extra)
        return self.alertas.criar(**dados)

    def test_ponto_dentro_da_area_define_a_propriedade(self):
        registro, erro = self.novo(data="2026-11-01")
        self.assertIsNone(erro)
        salvo = self.alertas.buscar_por_id(registro.id)
        lat, lon = self.centro_da(self.propriedade_id)
        self.assertEqual((salvo.status, salvo.propriedade_id, salvo.data),
                         ("PENDENTE", self.propriedade_id, "2026-11-01"))
        self.assertAlmostEqual(salvo.latitude, lat)
        self.assertAlmostEqual(salvo.longitude, lon)
        self.assertEqual(self.alertas.descrever_local(salvo), "Sítio Teste")

    def test_ponto_na_area_de_outra_propriedade(self):
        outra = self.criar_propriedade("Outra")
        registro, _ = self.novo(latitude=self.centro_da(outra)[0], longitude=self.centro_da(outra)[1])
        self.assertEqual(registro.propriedade_id, outra)

    def test_ponto_fora_de_toda_area_fica_sem_propriedade(self):
        registro, erro = self.novo(latitude=-29.5, longitude=-50.0)
        self.assertIsNone(erro)
        salvo = self.alertas.buscar_por_id(registro.id)
        self.assertIsNone(salvo.propriedade_id)
        self.assertEqual(self.alertas.descrever_local(salvo), "fora de propriedade cadastrada")

    def test_propriedade_no_ponto_para_a_tela(self):
        lat, lon = self.centro_da(self.propriedade_id)
        self.assertEqual(self.alertas.propriedade_no_ponto(lat, lon).id, self.propriedade_id)
        self.assertIsNone(self.alertas.propriedade_no_ponto(-29.5, -50.0))
        self.assertEqual([i for i, _, _ in self.alertas.listar_areas()], [self.propriedade_id])

    def test_validacoes_de_entrada(self):
        self.assertEqual(self.novo(latitude="91")[1], "Latitude deve estar entre -90 e 90.")
        self.assertEqual(self.novo(longitude="abc")[1], "Longitude deve ser um número.")
        self.assertEqual(self.novo(latitude="")[1], "Latitude é obrigatória.")
        self.assertEqual(self.novo(descricao="  ")[1], "Preencha o campo Descrição.")
        self.assertEqual(self.novo(data="31/12/2026")[1], "Data deve estar no formato AAAA-MM-DD.")
        self.assertEqual(self.contar("registros_desmatamento"), 0)

    def test_atualizar_muda_descricao_e_data(self):
        registro, _ = self.novo()
        _, erro = self.alertas.atualizar(registro.id, "Corte seletivo", "2026-10-30")
        self.assertIsNone(erro)
        salvo = self.alertas.buscar_por_id(registro.id)
        self.assertEqual((salvo.descricao, salvo.data), ("Corte seletivo", "2026-10-30"))

    def test_atualizar_nao_muda_ponto_status_nem_propriedade(self):
        registro, _ = self.novo()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.alertas.atualizar(registro.id, "Outra")
        salvo = self.alertas.buscar_por_id(registro.id)
        self.assertEqual((salvo.status, salvo.propriedade_id, salvo.latitude, salvo.longitude),
                         ("CONFIRMADO", self.propriedade_id, registro.latitude, registro.longitude))

    def test_atualizar_valida_e_nao_grava_com_erro(self):
        registro, _ = self.novo()
        self.assertEqual(self.alertas.atualizar(registro.id, " ")[1], "Preencha o campo Descrição.")
        self.assertEqual(self.alertas.buscar_por_id(registro.id).descricao, "Corte raso")
        self.assertEqual(self.alertas.atualizar(999, "x")[1], "Alerta não encontrado.")
        self.assertEqual(self.alertas.atualizar(None, "x")[1], "Alerta não encontrado.")

    def test_atualizar_nao_gera_notificacao(self):
        self.unidades.criar("IBAMA")
        registro, _ = self.novo()
        self.alertas.atualizar(registro.id, "Outra")
        self.assertEqual(self.contar("notificacoes"), 1)

    def test_excluir_apaga_em_cascata_notificacoes_e_embargos(self):
        unidade, _ = self.unidades.criar("IBAMA")
        registro, _ = self.novo()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        _, erro = ConformidadeController().embargar(self.propriedade_id, unidade.id, registro.id, "Corte")
        self.assertIsNone(erro)
        self.assertEqual(self.alertas.excluir(registro.id), (True, None))
        self.assertIsNone(self.alertas.buscar_por_id(registro.id))
        for tabela in ("registros_desmatamento", "notificacoes", "embargos"):
            self.assertEqual(self.contar(tabela), 0, tabela)
        self.assertEqual(self.alertas.excluir(registro.id)[1], "Alerta não encontrado.")

    def test_observer_notifica_cada_unidade_na_criacao_e_na_mudanca(self):
        self.unidades.criar("IBAMA")
        self.unidades.criar("FEPAM")
        registro, _ = self.novo()
        self.assertEqual(self.contar("notificacoes"), 2)
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.assertEqual(self.contar("notificacoes"), 4)
        self.assertIn("CONFIRMADO", self.unidades.listar_notificacoes()[0].mensagem)

    def test_varios_controllers_nao_duplicam_notificacoes(self):
        self.unidades.criar("IBAMA")
        self.unidades.criar("FEPAM")
        AlertaController()
        AlertaController()
        self.novo()
        self.assertEqual(self.contar("notificacoes"), 2)

    def test_observer_sem_unidades_nao_quebra(self):
        _, erro = self.novo()
        self.assertIsNone(erro)
        self.assertEqual(self.contar("notificacoes"), 0)

    def test_publicador_injetado_recebe_os_eventos(self):
        publicador = PublicadorAlertas()
        observador = ObservadorDeTeste()
        publicador.inscrever(observador)
        alertas = AlertaController(publicador)
        registro, _ = alertas.criar("x", *self.centro_da(self.propriedade_id))
        alertas.mudar_status(registro.id, "CANCELADO")
        self.assertEqual(observador.eventos, [
            (registro.id, "novo alerta"), (registro.id, "status alterado para CANCELADO")])

    def test_mudar_status_respeita_o_state(self):
        registro, _ = self.novo()
        self.assertEqual(self.alertas.transicoes_possiveis(registro.id), ["CONFIRMADO", "CANCELADO"])
        self.assertEqual(self.alertas.mudar_status(registro.id, "RESOLVIDO")[1],
                         "Não é possível mudar de PENDENTE para RESOLVIDO.")
        self.assertEqual(self.alertas.buscar_por_id(registro.id).status, "PENDENTE")
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.alertas.mudar_status(registro.id, "RESOLVIDO")
        self.assertEqual(self.alertas.transicoes_possiveis(registro.id), [])
        self.assertEqual(self.alertas.mudar_status(999, "CONFIRMADO")[1], "Alerta não encontrado.")

    def test_listar_sem_finalizados(self):
        a, _ = self.novo()
        b, _ = self.novo()
        self.alertas.mudar_status(b.id, "CANCELADO")
        self.assertEqual([r.id for r in self.alertas.listar(incluir_finalizados=False)], [a.id])
        self.assertEqual(len(self.alertas.listar()), 2)


class TestBancoAntigo(BancoTemporario):
    def test_tabela_com_colunas_de_fonte_e_detectada(self):
        self.assertFalse(AlertaController().banco_desatualizado())
        conn = get_connection()
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DROP TABLE registros_desmatamento")
            conn.execute("CREATE TABLE registros_desmatamento (id INTEGER PRIMARY KEY, "
                         "descricao TEXT, satelite_id INTEGER, usuario_id INTEGER)")
            conn.commit()
        finally:
            conn.close()
        self.assertTrue(AlertaController().banco_desatualizado())


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
        AlertaController().criar("x", *self.centro_da(self.propriedade_id))
        notificacao = self.unidades.listar_notificacoes()[0]
        self.assertEqual(notificacao.status, "ENVIADA")
        self.unidades.marcar_lida(notificacao.id)
        self.assertEqual(self.unidades.listar_notificacoes()[0].status, "LIDA")
        self.assertEqual(self.unidades.marcar_lida(999)[1], "Notificação não encontrada.")


if __name__ == "__main__":
    unittest.main()
