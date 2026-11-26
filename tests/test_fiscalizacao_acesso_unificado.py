"""Acesso a dados unificado (issue #3, aulas 09 e 10).

Garante que os models da Fiscalização usam o ModeloBase, como os do
Cadastro, e que o comportamento visto pelos controllers não mudou.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.conformidade_controller import ConformidadeController
from controller.fiscalizacao.unidade_controller import UnidadeController
from model.base import ModeloBase
from model.fiscalizacao.declaracao import Declaracao
from model.fiscalizacao.embargo import Embargo
from model.fiscalizacao.notificacao import Notificacao
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.unidade_competente import UnidadeCompetente
from model.propriedade_rural import PropriedadeRural
from test_fiscalizacao_apoio import BancoTemporario

PASTA_MODELS = Path(__file__).resolve().parent.parent / "src" / "model" / "fiscalizacao"

MODELS_PERSISTIDOS = (
    UnidadeCompetente, RegistroDesmatamento, Notificacao, Embargo, Declaracao,
)


class TestUmaSoFormaDeAcessarOBanco(unittest.TestCase):
    def test_todos_os_models_herdam_do_modelo_base(self):
        for model in MODELS_PERSISTIDOS:
            with self.subTest(model=model.__name__):
                self.assertTrue(issubclass(model, ModeloBase))

    def test_conexao_py_nao_existe_mais(self):
        self.assertFalse((PASTA_MODELS / "conexao.py").exists())

    def test_nenhum_model_abre_conexao_sozinho(self):
        # __init__.py só cria as tabelas (SCHEMA); ele não lê nem grava registros.
        for arquivo in PASTA_MODELS.glob("*.py"):
            if arquivo.name == "__init__.py":
                continue
            with self.subTest(arquivo=arquivo.name):
                codigo = arquivo.read_text(encoding="utf-8")
                self.assertNotIn("get_connection", codigo)
                self.assertNotIn("conexao", codigo)


class TestComportamentoMantido(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.unidade, _ = UnidadeController().criar("IBAMA", "Federal", "ibama@ex.gov")
        self.alertas = AlertaController()
        self.conformidade = ConformidadeController()

    def novo_alerta(self):
        registro, _ = self.alertas.criar("Corte", *self.centro_da(self.propriedade_id))
        return registro

    def test_declaracoes_listadas_da_mais_nova_para_a_mais_antiga(self):
        primeira, _ = self.conformidade.solicitar_declaracao(self.propriedade_id)
        segunda, _ = self.conformidade.solicitar_declaracao(self.propriedade_id)
        ids = [d.id for d in self.conformidade.listar_declaracoes()]
        self.assertEqual(ids, [segunda.id, primeira.id])

    def test_embargos_listados_do_mais_novo_para_o_mais_antigo(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        primeiro, _ = self.conformidade.embargar(
            self.propriedade_id, self.unidade.id, registro.id, "Motivo 1")
        self.conformidade.levantar_embargo(primeiro.id)
        segundo, _ = self.conformidade.embargar(
            self.propriedade_id, self.unidade.id, registro.id, "Motivo 2")
        ids = [e.id for e in self.conformidade.listar_embargos()]
        self.assertEqual(ids, [segundo.id, primeiro.id])

    def test_levantar_embargo_grava_ativo_zero(self):
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        embargo, _ = self.conformidade.embargar(
            self.propriedade_id, self.unidade.id, registro.id, "Motivo")
        self.conformidade.levantar_embargo(embargo.id)
        self.assertEqual(Embargo.buscar_por_id(embargo.id).ativo, 0)
        self.assertIsNone(Embargo.buscar_ativo(self.propriedade_id))

    def test_marcar_notificacao_como_lida_grava_no_banco(self):
        self.novo_alerta()
        notificacao = Notificacao.listar_todas()[0]
        UnidadeController().marcar_lida(notificacao.id)
        self.assertEqual(Notificacao.buscar_por_id(notificacao.id).status, "LIDA")

    def test_existe_da_unidade(self):
        self.assertFalse(Embargo.existe_da_unidade(self.unidade.id))
        registro = self.novo_alerta()
        self.alertas.mudar_status(registro.id, "CONFIRMADO")
        self.conformidade.embargar(self.propriedade_id, self.unidade.id, registro.id, "Motivo")
        self.assertTrue(Embargo.existe_da_unidade(self.unidade.id))

    def test_status_do_alerta_volta_do_banco_como_texto(self):
        registro = self.novo_alerta()
        self.assertEqual(RegistroDesmatamento.buscar_por_id(registro.id).status, "PENDENTE")

    def test_cadastro_continua_listando_em_ordem_crescente(self):
        # A ordem padrão do ModeloBase não mudou para os models do Cadastro.
        segunda = self.criar_propriedade("Outra")
        ids = [p.id for p in PropriedadeRural.listar_todos()]
        self.assertEqual(ids, [self.propriedade_id, segunda])

if __name__ == "__main__":
    unittest.main()
