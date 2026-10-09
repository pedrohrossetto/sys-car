import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import database
from model.localizacao import Localizacao
from model.propriedade_rural import PropriedadeRural
from model.proprietario import Proprietario
from test_cadastro_apoio import BancoTemporario

RAIZ = Path(__file__).resolve().parent.parent


class TestDescobertaDeSchema(BancoTemporario):
    def test_init_db_cria_as_tabelas_do_cadastro(self):
        self.assertTrue({"proprietarios", "propriedades_rurais", "localizacoes"} <= self.tabelas())

    def test_database_py_nao_cita_nenhuma_tabela(self):
        codigo = (RAIZ / "src" / "database" / "database.py").read_text(encoding="utf-8")
        for tabela in ("proprietarios", "propriedades_rurais", "localizacoes"):
            self.assertNotIn(tabela, codigo)

    def test_init_db_pode_rodar_duas_vezes(self):
        database.init_db()
        self.assertIn("proprietarios", self.tabelas())


class TestModeloBase(BancoTemporario):
    def test_ida_e_volta_crud(self):
        dono = Proprietario("Ana", "PF", cpf="52998224725")
        dono.salvar()
        p = PropriedadeRural("Sítio", dono.id)
        p.salvar()
        self.assertIsNotNone(p.id)
        p.nome = "Sítio Novo"
        p.salvar()
        self.assertEqual(PropriedadeRural.buscar_por_id(p.id).nome, "Sítio Novo")
        p.deletar()
        self.assertIsNone(PropriedadeRural.buscar_por_id(p.id))

    def test_buscas_especificas(self):
        dono = Proprietario("Ana", "PF", cpf="52998224725")
        dono.salvar()
        empresa = Proprietario("Fazenda SA", "PJ", cnpj="11222333000181")
        empresa.salvar()
        self.assertEqual(Proprietario.buscar_por_documento("PF", "52998224725").id, dono.id)
        self.assertEqual(Proprietario.buscar_por_documento("PJ", "11222333000181").id, empresa.id)
        self.assertEqual(empresa.documento, "11222333000181")
        prop = PropriedadeRural("Sítio", dono.id)
        prop.salvar()
        loc = Localizacao(prop.id, 1.0, 2.0)
        loc.salvar()
        self.assertEqual(Localizacao.buscar_por_propriedade(prop.id).id, loc.id)
        self.assertEqual([l.id for l in Localizacao.listar_todas()], [loc.id])

    def test_check_do_banco_impede_pf_sem_cpf(self):
        import sqlite3

        with self.assertRaises(sqlite3.IntegrityError):
            Proprietario("Ana", "PF", cnpj="11222333000181").salvar()


if __name__ == "__main__":
    unittest.main()
