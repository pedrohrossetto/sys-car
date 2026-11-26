"""Estratégia de exceções (issue #19, ADR-003).

O model lança, o controller captura e devolve (None, "mensagem"), a view mostra.
Estes testes provocam erros reais do SQLite: nenhum erro é simulado.
"""
import inspect
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import controller
from controller.erros import devolve_erro
from controller.fiscalizacao.unidade_controller import UnidadeController
from controller.proprietario_controller import ProprietarioController
from database import database
from descoberta import modulos_com
from model.erros import ErroDeBanco
from model.fiscalizacao.embargo import Embargo
from model.fiscalizacao.status import TransicaoInvalida
from model.fiscalizacao.unidade_competente import UnidadeCompetente
from model.proprietario import Proprietario
from test_fiscalizacao_apoio import BancoTemporario


def apagar_tabela(nome):
    conn = database.get_connection()
    try:
        conn.execute(f"DROP TABLE {nome}")
        conn.commit()
    finally:
        conn.close()


class TestErroDeBancoNoModel(BancoTemporario):
    """A exceção nasce no model: todo sqlite3.Error sai como ErroDeBanco."""

    def test_unique(self):
        Proprietario("Ana", "PF", cpf="52998224725").salvar()
        with self.assertRaises(ErroDeBanco) as contexto:
            Proprietario("Bia", "PF", cpf="52998224725").salvar()
        self.assertEqual(str(contexto.exception), "Já existe um registro com este valor.")

    def test_check(self):
        with self.assertRaises(ErroDeBanco) as contexto:
            Proprietario("Ana", "XX", cpf="52998224725").salvar()
        self.assertEqual(str(contexto.exception), "Um dos valores não é aceito pelo banco de dados.")

    def test_not_null(self):
        with self.assertRaises(ErroDeBanco) as contexto:
            UnidadeCompetente(None).salvar()
        self.assertEqual(str(contexto.exception), "Um campo obrigatório ficou vazio.")

    def test_foreign_key(self):
        embargo = Embargo(self.propriedade_id, unidade_id=999, registro_id=999,
                          data="2026-11-25", motivo="x")
        with self.assertRaises(ErroDeBanco) as contexto:
            embargo.salvar()
        self.assertIn("ligado a outro registro", str(contexto.exception))

    def test_a_excecao_original_fica_em_cause(self):
        with self.assertRaises(ErroDeBanco) as contexto:
            Proprietario("Ana", "XX", cpf="52998224725").salvar()
        self.assertIsInstance(contexto.exception.__cause__, sqlite3.IntegrityError)

    def test_insert_que_falha_nao_deixa_id_no_objeto(self):
        proprietario = Proprietario("Ana", "XX", cpf="52998224725")
        with self.assertRaises(ErroDeBanco):
            proprietario.salvar()
        self.assertIsNone(proprietario.id)
        self.assertEqual(self.contar("proprietarios"), 0)

    def test_leitura_tambem_vira_erro_de_banco(self):
        apagar_tabela("unidades_competentes")
        with self.assertRaises(ErroDeBanco) as contexto:
            UnidadeCompetente.listar_todos()
        self.assertIn("Não foi possível acessar o banco de dados", str(contexto.exception))


class TestTraducaoDasMensagens(unittest.TestCase):
    def test_restricao_desconhecida_tem_mensagem_generica(self):
        erro = ErroDeBanco.de(sqlite3.IntegrityError("constraint failed"))
        self.assertEqual(str(erro), "Os dados violam uma regra do banco de dados.")

    def test_erro_que_nao_e_de_integridade(self):
        erro = ErroDeBanco.de(sqlite3.OperationalError("database is locked"))
        self.assertEqual(str(erro), "Não foi possível acessar o banco de dados (database is locked).")


class TestControllerDevolveOErro(BancoTemporario):
    """O controller captura: o erro do banco chega como (None, "mensagem")."""

    def test_erro_do_banco_vira_tupla(self):
        apagar_tabela("unidades_competentes")
        resultado, erro = UnidadeController().criar("IBAMA")
        self.assertIsNone(resultado)
        self.assertIn("Não foi possível acessar o banco de dados", erro)

    def test_validacao_continua_igual(self):
        self.assertEqual(ProprietarioController().criar("Ana", "PF", cpf="111")[1], "CPF inválido.")

    def test_decorador_nao_esconde_outros_erros(self):
        # Só ErroDeBanco vira mensagem. Um defeito de programação continua visível.
        @devolve_erro
        def com_defeito():
            raise TypeError("defeito")
        with self.assertRaises(TypeError):
            com_defeito()

    def test_transicao_invalida_e_um_value_error(self):
        self.assertTrue(issubclass(TransicaoInvalida, ValueError))


class TestRegraDoDecorador(unittest.TestCase):
    """Todo método de controller que devolve (resultado, erro) usa @devolve_erro."""

    def test_todos_os_metodos_com_tupla_usam_o_decorador(self):
        faltando = []
        for modulo in modulos_com(controller, "__name__"):
            for _, classe in inspect.getmembers(modulo, inspect.isclass):
                if classe.__module__ != modulo.__name__:
                    continue
                for nome, metodo in inspect.getmembers(classe, inspect.isfunction):
                    if nome.startswith("_"):
                        continue
                    codigo = inspect.getsource(inspect.unwrap(metodo))
                    devolve_tupla = "return None," in codigo or ", None" in codigo
                    if devolve_tupla and not hasattr(metodo, "__wrapped__"):
                        faltando.append(f"{classe.__name__}.{nome}")
        self.assertEqual(faltando, [])


if __name__ == "__main__":
    unittest.main()
