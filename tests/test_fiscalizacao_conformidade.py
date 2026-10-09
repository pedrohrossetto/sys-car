import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.conformidade_controller import ConformidadeController
from controller.fiscalizacao.fonte_controller import FonteController
from controller.fiscalizacao.unidade_controller import UnidadeController
from database import database
from test_fiscalizacao_apoio import BancoTemporario


class TestConformidade(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.alertas = AlertaController()
        self.conformidade = ConformidadeController()
        self.unidade, _ = UnidadeController().criar("IBAMA", "Federal", "ibama@ex.gov")
        self.satelite, _ = FonteController().criar_satelite("Sentinel-2")

    def novo_alerta(self, propriedade_id=None):
        registro, _ = self.alertas.registrar_por_satelite(
            self.satelite.id, propriedade_id or self.propriedade_id, "Corte", 0, 0)
        return registro

    def embargar(self, registro, propriedade_id=None):
        return self.conformidade.embargar(
            propriedade_id or self.propriedade_id, self.unidade.id, registro.id, "Desmatamento ilegal")

    def test_declaracao_emitida_sem_pendencias(self):
        declaracao, erro = self.conformidade.solicitar_declaracao(self.propriedade_id)
        self.assertIsNone(erro)
        self.assertEqual(declaracao.resultado, "EMITIDA")

    def test_declaracao_negada_com_alerta_pendente_e_confirmado(self):
        registro = self.novo_alerta()
        negada, _ = self.conformidade.solicitar_declaracao(self.propriedade_id)
        self.assertEqual(negada.resultado, "NEGADA")
        self.assertIn(f"alerta {registro.id} PENDENTE", negada.motivo)
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        negada, _ = self.conformidade.solicitar_declaracao(self.propriedade_id)
        self.assertIn(f"alerta {registro.id} CONFIRMADO", negada.motivo)

    def test_alerta_cancelado_nao_impede(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CANCELADO")
        self.assertEqual(self.conformidade.solicitar_declaracao(self.propriedade_id)[0].resultado, "EMITIDA")

    def test_alerta_de_outra_propriedade_nao_impede(self):
        outra = self.criar_propriedade("Outra")
        self.novo_alerta(outra)
        self.assertEqual(self.conformidade.solicitar_declaracao(self.propriedade_id)[0].resultado, "EMITIDA")

    def test_embargo_sem_alerta_confirmado_e_rejeitado(self):
        registro = self.novo_alerta()
        self.assertEqual(self.embargar(registro)[1],
                         "Embargo exige um alerta CONFIRMADO desta propriedade.")

    def test_embargo_com_alerta_de_outra_propriedade_e_rejeitado(self):
        outra = self.criar_propriedade("Outra")
        registro = self.novo_alerta(outra)
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.assertEqual(self.embargar(registro)[1],
                         "Embargo exige um alerta CONFIRMADO desta propriedade.")

    def test_embargo_valido_e_segundo_embargo_ativo(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        embargo, erro = self.embargar(registro)
        self.assertIsNone(erro)
        self.assertEqual(embargo.ativo, 1)
        self.assertEqual(self.embargar(registro)[1], "Esta propriedade já está embargada.")

    def test_embargo_exige_motivo_e_unidade(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.assertEqual(self.conformidade.embargar(
            self.propriedade_id, self.unidade.id, registro.id, " ")[1], "Preencha o campo Motivo.")
        self.assertEqual(self.conformidade.embargar(
            self.propriedade_id, None, registro.id, "x")[1], "Unidade não encontrada.")
        self.assertEqual(self.conformidade.embargar(
            self.propriedade_id, self.unidade.id, None, "x")[1],
            "Embargo exige um alerta CONFIRMADO desta propriedade.")

    def test_ciclo_completo_volta_a_emitir(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        embargo, _ = self.embargar(registro)
        self.alertas.mudar_status(registro.id, "RESOLVIDO")
        negada, _ = self.conformidade.solicitar_declaracao(self.propriedade_id)
        self.assertEqual(negada.resultado, "NEGADA")
        self.assertIn(f"embargo {embargo.id} ativo", negada.motivo)
        self.assertIsNone(self.conformidade.levantar_embargo(embargo.id)[1])
        self.assertEqual(self.conformidade.levantar_embargo(embargo.id)[1],
                         "Este embargo já foi levantado.")
        self.assertEqual(self.conformidade.solicitar_declaracao(self.propriedade_id)[0].resultado, "EMITIDA")
        self.assertEqual(len(self.conformidade.listar_declaracoes()), 2)

    def test_novo_embargo_depois_de_levantado(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        embargo, _ = self.embargar(registro)
        self.conformidade.levantar_embargo(embargo.id)
        self.assertIsNone(self.embargar(registro)[1])

    def test_registros_confirmados_da_propriedade(self):
        a = self.novo_alerta()
        self.novo_alerta()
        self.alertas.mudar_status(a.id, "CONFIRMADO")
        self.assertEqual([r.id for r in self.conformidade.registros_confirmados(self.propriedade_id)], [a.id])

    def test_texto_da_declaracao(self):
        declaracao, _ = self.conformidade.solicitar_declaracao(self.propriedade_id)
        texto, erro = self.conformidade.texto_declaracao(declaracao.id)
        self.assertIsNone(erro)
        self.assertIn("Propriedade: Sítio Teste", texto)
        self.assertIn("Resultado: EMITIDA", texto)
        self.assertEqual(self.conformidade.texto_declaracao(999)[1], "Declaração não encontrada.")

    def test_declaracao_de_propriedade_inexistente(self):
        self.assertEqual(self.conformidade.solicitar_declaracao(999)[1], "Propriedade não encontrada.")
        self.assertEqual(self.contar("declaracoes"), 0)


class TestExclusoesECascade(BancoTemporario):
    def test_todas_as_tabelas_da_fiscalizacao_existem(self):
        tabelas = {
            "satelites", "usuarios", "registros_desmatamento", "evidencias",
            "unidades_competentes", "notificacoes", "embargos", "declaracoes",
        }
        self.assertTrue(tabelas <= self.tabelas())

    def test_unidade_com_embargo_nao_pode_ser_excluida(self):
        unidades = UnidadeController()
        unidade, _ = unidades.criar("IBAMA")
        satelite, _ = FonteController().criar_satelite("Landsat")
        alertas = AlertaController()
        registro, _ = alertas.registrar_por_satelite(satelite.id, self.propriedade_id, "x", 0, 0)
        alertas.mudar_status(registro.id, "CONFIRMADO")
        ConformidadeController().embargar(self.propriedade_id, unidade.id, registro.id, "m")
        self.assertEqual(unidades.excluir(unidade.id)[1],
                         "Esta unidade aplicou embargos e não pode ser excluída.")
        self.assertEqual(self.contar("unidades_competentes"), 1)

    def test_apagar_propriedade_apaga_tudo_da_fiscalizacao(self):
        unidade, _ = UnidadeController().criar("IBAMA")
        fontes = FonteController()
        satelite, _ = fontes.criar_satelite("Landsat")
        usuario, _ = fontes.criar_usuario("Joana", "52998224725", "a@b.com")
        alertas = AlertaController()
        conformidade = ConformidadeController()
        registro, _ = alertas.registrar_por_satelite(satelite.id, self.propriedade_id, "x", 0, 0)
        alertas.registrar_por_usuario(usuario.id, self.propriedade_id, "y", 0, 0, [("Foto", "l")])
        alertas.mudar_status(registro.id, "CONFIRMADO")
        conformidade.embargar(self.propriedade_id, unidade.id, registro.id, "m")
        conformidade.solicitar_declaracao(self.propriedade_id)
        conn = database.get_connection()
        try:
            conn.execute("DELETE FROM propriedades_rurais WHERE id = ?", (self.propriedade_id,))
            conn.commit()
        finally:
            conn.close()
        for tabela in ("registros_desmatamento", "evidencias", "notificacoes", "embargos", "declaracoes"):
            with self.subTest(tabela=tabela):
                self.assertEqual(self.contar(tabela), 0)
        self.assertEqual((self.contar("satelites"), self.contar("usuarios")), (1, 1))


if __name__ == "__main__":
    unittest.main()
