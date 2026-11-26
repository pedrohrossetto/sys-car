"""Ficha da propriedade (issue #6, aula 11: relacionamentos)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.conformidade_controller import ConformidadeController
from controller.fiscalizacao.ficha_controller import (
    COM_ALERTAS, EMBARGADA, REGULAR, FichaController,
)
from controller.fiscalizacao.unidade_controller import UnidadeController
from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.proprietario_controller import ProprietarioController
from database import database
from test_fiscalizacao_apoio import BancoTemporario, area_de_teste


class TestFichaDaPropriedade(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.fichas = FichaController()
        self.alertas = AlertaController()
        self.conformidade = ConformidadeController()
        self.unidade, _ = UnidadeController().criar("IBAMA", "Federal", "ibama@ex.gov")
        # Propriedade completa, criada pelos controllers do Cadastro.
        self.dono, _ = ProprietarioController().criar("Ana", "PF", cpf="529.982.247-25")
        self.prop, _ = PropriedadeRuralController().criar(
            "Sítio Boa Vista", self.dono.id, "RS-123", area_de_teste(9))

    def novo_alerta(self, propriedade_id=None):
        registro, _ = self.alertas.criar(propriedade_id or self.prop.id, "Corte raso", -28.2, -52.4)
        return registro

    def test_propriedade_inexistente(self):
        self.assertEqual(self.fichas.montar(999), (None, "Propriedade não encontrada."))
        self.assertEqual(self.fichas.montar(None)[1], "Propriedade não encontrada.")

    def test_ficha_traz_proprietario_e_area_do_cadastro(self):
        ficha, erro = self.fichas.montar(self.prop.id)
        self.assertIsNone(erro)
        self.assertEqual(ficha.propriedade.nome, "Sítio Boa Vista")
        self.assertEqual(ficha.proprietario.nome, "Ana")
        self.assertEqual(len(ficha.propriedade.area), 4)
        self.assertAlmostEqual(ficha.propriedade.area_ha, 108.4, delta=0.5)

    def test_ficha_sem_fiscalizacao(self):
        ficha, _ = self.fichas.montar(self.prop.id)
        self.assertEqual((ficha.alertas, ficha.declaracoes), ([], []))
        self.assertIsNone(ficha.embargo_ativo)
        self.assertEqual(ficha.situacao, REGULAR)

    def test_proprietario_que_nao_existe_vira_none(self):
        # Propriedade gravada com as FKs desligadas, apontando para um proprietário inexistente.
        conn = database.get_connection()
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            orfa = conn.execute(
                "INSERT INTO propriedades_rurais (nome, proprietario_id) VALUES ('Órfã', 999)"
            ).lastrowid
            conn.commit()
        finally:
            conn.close()
        ficha, erro = self.fichas.montar(orfa)
        self.assertIsNone(erro)
        self.assertIsNone(ficha.proprietario)

    def test_so_aparecem_dados_da_propria_propriedade(self):
        meu = self.novo_alerta()
        self.novo_alerta(self.propriedade_id)
        minha_declaracao, _ = self.conformidade.solicitar_declaracao(self.prop.id)
        self.conformidade.solicitar_declaracao(self.propriedade_id)
        ficha, _ = self.fichas.montar(self.prop.id)
        self.assertEqual([a.id for a in ficha.alertas], [meu.id])
        self.assertEqual([d.id for d in ficha.declaracoes], [minha_declaracao.id])

    def test_declaracoes_da_mais_nova_para_a_mais_antiga(self):
        primeira, _ = self.conformidade.solicitar_declaracao(self.prop.id)
        segunda, _ = self.conformidade.solicitar_declaracao(self.prop.id)
        ficha, _ = self.fichas.montar(self.prop.id)
        self.assertEqual([d.id for d in ficha.declaracoes], [segunda.id, primeira.id])

    def test_situacao_com_alerta_pendente(self):
        self.novo_alerta()
        ficha, _ = self.fichas.montar(self.prop.id)
        self.assertEqual(ficha.situacao, COM_ALERTAS)
        self.assertEqual(len(ficha.alertas_em_aberto), 1)

    def test_situacao_embargada_mostra_a_unidade(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        embargo, _ = self.conformidade.embargar(
            self.prop.id, self.unidade.id, registro.id, "Desmatamento ilegal")
        ficha, _ = self.fichas.montar(self.prop.id)
        self.assertEqual(ficha.situacao, EMBARGADA)
        self.assertEqual(ficha.embargo_ativo.id, embargo.id)
        self.assertEqual(ficha.unidade_do_embargo.nome, "IBAMA")

    def test_volta_a_regular_depois_de_resolver_e_levantar(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        embargo, _ = self.conformidade.embargar(
            self.prop.id, self.unidade.id, registro.id, "Desmatamento ilegal")
        self.alertas.mudar_status(registro.id, "RESOLVIDO")
        self.conformidade.levantar_embargo(embargo.id)
        ficha, _ = self.fichas.montar(self.prop.id)
        self.assertEqual(ficha.situacao, REGULAR)
        self.assertEqual(len(ficha.alertas), 1)


if __name__ == "__main__":
    unittest.main()
