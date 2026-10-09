import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from model.documento import VALIDADORES, ValidadorCNPJ, ValidadorCPF


class TestValidadorCPF(unittest.TestCase):
    def setUp(self):
        self.v = ValidadorCPF()

    def test_cpf_valido_com_e_sem_mascara(self):
        self.assertTrue(self.v.valido(self.v.normalizar("529.982.247-25")))
        self.assertTrue(self.v.valido(self.v.normalizar("52998224725")))

    def test_cpf_comeca_com_zero_mantem_o_zero(self):
        self.assertEqual(self.v.normalizar("012.345.678-90"), "01234567890")
        self.assertTrue(self.v.valido("01234567890"))

    def test_cpf_digito_errado(self):
        self.assertFalse(self.v.valido("52998224724"))

    def test_cpf_tamanho_errado(self):
        self.assertFalse(self.v.valido("5299822472"))
        self.assertFalse(self.v.valido(""))

    def test_cpf_todos_iguais(self):
        self.assertFalse(self.v.valido("11111111111"))


class TestValidadorCNPJ(unittest.TestCase):
    def setUp(self):
        self.v = ValidadorCNPJ()

    def test_cnpj_numerico_valido_com_e_sem_mascara(self):
        self.assertTrue(self.v.valido(self.v.normalizar("11.222.333/0001-81")))
        self.assertTrue(self.v.valido("11222333000181"))

    def test_cnpj_alfanumerico_valido(self):
        self.assertEqual(self.v.normalizar("12.abc.345/01de-35"), "12ABC34501DE35")
        self.assertTrue(self.v.valido("12ABC34501DE35"))

    def test_cnpj_digito_errado(self):
        self.assertFalse(self.v.valido("11222333000182"))

    def test_cnpj_tamanho_errado_ou_letra_no_dv(self):
        self.assertFalse(self.v.valido("1122233300018"))
        self.assertFalse(self.v.valido("12ABC34501DE3A"))

    def test_cnpj_todos_iguais(self):
        self.assertFalse(self.v.valido("00000000000000"))


class TestEscolhaDaEstrategia(unittest.TestCase):
    def test_tipo_escolhe_o_validador(self):
        self.assertIsInstance(VALIDADORES["PF"], ValidadorCPF)
        self.assertIsInstance(VALIDADORES["PJ"], ValidadorCNPJ)


if __name__ == "__main__":
    unittest.main()
