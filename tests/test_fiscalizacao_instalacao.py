import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.fiscalizacao.instalacao import preparar_banco
from model.fiscalizacao.regras import (
    converter_coordenada, cpf_formato_valido, data_iso, email_valido, normalizar_cpf,
    texto_obrigatorio,
)
from test_fiscalizacao_apoio import BancoTemporario


class TestInstalacao(BancoTemporario):
    def test_preparar_banco_cria_as_tabelas_do_sistema(self):
        self.assertIn("propriedades_rurais", self.tabelas())

    def test_preparar_banco_pode_rodar_duas_vezes(self):
        preparar_banco()
        self.assertIn("propriedades_rurais", self.tabelas())


class TestRegras(unittest.TestCase):
    def test_texto_obrigatorio(self):
        self.assertEqual(texto_obrigatorio("  x ", "Nome"), "x")
        with self.assertRaisesRegex(ValueError, "Preencha o campo Nome."):
            texto_obrigatorio("   ", "Nome")
        with self.assertRaisesRegex(ValueError, "Preencha o campo Nome."):
            texto_obrigatorio(None, "Nome")

    def test_cpf_por_formato(self):
        self.assertEqual(normalizar_cpf("012.345.678-90"), "01234567890")
        self.assertTrue(cpf_formato_valido("01234567890"))
        self.assertFalse(cpf_formato_valido("123"))

    def test_email(self):
        self.assertTrue(email_valido(" joana@ex.com "))
        for invalido in ("joana", "joana@", "@ex.com", "jo ana@ex.com", "", None):
            self.assertFalse(email_valido(invalido))

    def test_coordenada(self):
        self.assertEqual(converter_coordenada("-28,2", "Latitude", 90), -28.2)
        with self.assertRaisesRegex(ValueError, "entre -90 e 90"):
            converter_coordenada("91", "Latitude", 90)
        with self.assertRaisesRegex(ValueError, "deve ser um número"):
            converter_coordenada("abc", "Longitude", 180)
        with self.assertRaisesRegex(ValueError, "é obrigatória"):
            converter_coordenada(" ", "Latitude", 90)

    def test_data(self):
        self.assertEqual(data_iso("2026-01-05"), "2026-01-05")
        self.assertEqual(len(data_iso()), 10)
        with self.assertRaisesRegex(ValueError, "AAAA-MM-DD"):
            data_iso("05/01/2026")


if __name__ == "__main__":
    unittest.main()
