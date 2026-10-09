import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.proprietario_controller import ProprietarioController
from database import database
from test_cadastro_apoio import BancoTemporario

CPF = "529.982.247-25"
CPF_2 = "012.345.678-90"
CNPJ = "11.222.333/0001-81"


class TestProprietarioController(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.ctrl = ProprietarioController()

    def test_cria_pf_guardando_so_digitos(self):
        p, erro = self.ctrl.criar("Ana", "PF", cpf=CPF)
        self.assertIsNone(erro)
        self.assertEqual(self.ctrl.buscar_por_id(p.id).cpf, "52998224725")
        self.assertIsNone(p.cnpj)

    def test_cpf_com_zero_a_esquerda_e_preservado(self):
        p, _ = self.ctrl.criar("Bia", "PF", cpf=CPF_2)
        self.assertEqual(self.ctrl.buscar_por_id(p.id).cpf, "01234567890")

    def test_cria_pj(self):
        p, erro = self.ctrl.criar("Fazenda SA", "PJ", cnpj=CNPJ)
        self.assertIsNone(erro)
        self.assertEqual(p.cnpj, "11222333000181")
        self.assertIsNone(p.cpf)

    def test_pf_ignora_cnpj_informado(self):
        p, erro = self.ctrl.criar("Ana", "PF", cpf=CPF, cnpj=CNPJ)
        self.assertIsNone(erro)
        self.assertIsNone(p.cnpj)

    def test_pf_sem_cpf_e_rejeitado(self):
        p, erro = self.ctrl.criar("Ana", "PF", cnpj=CNPJ)
        self.assertIsNone(p)
        self.assertEqual(erro, "CPF é obrigatório para PF.")

    def test_pj_sem_cnpj_e_rejeitado(self):
        _, erro = self.ctrl.criar("Fazenda SA", "PJ", cpf=CPF)
        self.assertEqual(erro, "CNPJ é obrigatório para PJ.")

    def test_documento_invalido_e_rejeitado(self):
        _, erro = self.ctrl.criar("Ana", "PF", cpf="111.111.111-11")
        self.assertEqual(erro, "CPF inválido.")

    def test_nome_vazio_e_tipo_invalido(self):
        self.assertEqual(self.ctrl.criar("   ", "PF", cpf=CPF)[1], "Nome é obrigatório.")
        self.assertEqual(self.ctrl.criar("Ana", "XX", cpf=CPF)[1], "Tipo deve ser PF ou PJ.")

    def test_documento_duplicado_com_mascara_diferente(self):
        self.ctrl.criar("Ana", "PF", cpf=CPF)
        _, erro = self.ctrl.criar("Outra", "PF", cpf="52998224725")
        self.assertEqual(erro, "CPF já cadastrado.")

    def test_atualizar_mantendo_o_proprio_documento(self):
        p, _ = self.ctrl.criar("Ana", "PF", cpf=CPF)
        atualizado, erro = self.ctrl.atualizar(p.id, "Ana Maria", "PF", cpf=CPF)
        self.assertIsNone(erro)
        self.assertEqual(self.ctrl.buscar_por_id(p.id).nome, "Ana Maria")

    def test_atualizar_para_documento_de_outro_e_rejeitado(self):
        self.ctrl.criar("Ana", "PF", cpf=CPF)
        b, _ = self.ctrl.criar("Bia", "PF", cpf=CPF_2)
        _, erro = self.ctrl.atualizar(b.id, "Bia", "PF", cpf=CPF)
        self.assertEqual(erro, "CPF já cadastrado.")

    def test_atualizar_de_pf_para_pj(self):
        p, _ = self.ctrl.criar("Ana", "PF", cpf=CPF)
        _, erro = self.ctrl.atualizar(p.id, "Ana ME", "PJ", cnpj=CNPJ)
        self.assertIsNone(erro)
        salvo = self.ctrl.buscar_por_id(p.id)
        self.assertEqual((salvo.tipo, salvo.cpf, salvo.cnpj), ("PJ", None, "11222333000181"))

    def test_excluir_e_listar(self):
        p, _ = self.ctrl.criar("Ana", "PF", cpf=CPF)
        self.assertEqual(len(self.ctrl.listar()), 1)
        self.assertEqual(self.ctrl.excluir(p.id), (True, None))
        self.assertEqual(self.ctrl.listar(), [])
        self.assertEqual(self.ctrl.excluir(p.id)[1], "Proprietário não encontrado.")


class TestBancoDesatualizado(BancoTemporario):
    CRIAR_TABELAS = False

    def test_detecta_tabela_da_versao_antiga(self):
        conn = sqlite3.connect(database.DB_PATH)
        conn.execute("CREATE TABLE proprietarios (id INTEGER PRIMARY KEY, nome TEXT, cpf TEXT, cnpj TEXT)")
        conn.close()
        database.init_db()
        self.assertTrue(ProprietarioController().banco_desatualizado())

    def test_banco_novo_nao_esta_desatualizado(self):
        database.init_db()
        self.assertFalse(ProprietarioController().banco_desatualizado())


if __name__ == "__main__":
    unittest.main()
