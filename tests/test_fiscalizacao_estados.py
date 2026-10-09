import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from model.fiscalizacao.status import StatusAlerta, TransicaoInvalida, estado_de


class TestEstados(unittest.TestCase):
    def test_transicoes_validas(self):
        self.assertEqual(estado_de("PENDENTE").ir_para("CONFIRMADO").STATUS, StatusAlerta.CONFIRMADO)
        self.assertEqual(estado_de("PENDENTE").ir_para("CANCELADO").STATUS, StatusAlerta.CANCELADO)
        self.assertEqual(estado_de("CONFIRMADO").ir_para("RESOLVIDO").STATUS, StatusAlerta.RESOLVIDO)

    def test_transicoes_invalidas(self):
        invalidas = [
            ("PENDENTE", "RESOLVIDO"), ("PENDENTE", "PENDENTE"),
            ("CONFIRMADO", "CANCELADO"), ("CONFIRMADO", "PENDENTE"),
        ]
        for atual, novo in invalidas:
            with self.subTest(atual=atual, novo=novo):
                with self.assertRaises(TransicaoInvalida):
                    estado_de(atual).ir_para(novo)

    def test_estados_finais_nao_mudam(self):
        for final in ("RESOLVIDO", "CANCELADO"):
            self.assertTrue(estado_de(final).finalizado)
            for novo in StatusAlerta:
                with self.assertRaises(TransicaoInvalida):
                    estado_de(final).ir_para(novo)

    def test_status_desconhecido(self):
        with self.assertRaisesRegex(TransicaoInvalida, "desconhecido"):
            estado_de("PENDENTE").ir_para("XYZ")

    def test_quem_bloqueia_conformidade(self):
        bloqueiam = {s.value for s in StatusAlerta if estado_de(s).BLOQUEIA_CONFORMIDADE}
        self.assertEqual(bloqueiam, {"PENDENTE", "CONFIRMADO"})

    def test_mensagem_de_transicao_invalida(self):
        with self.assertRaisesRegex(TransicaoInvalida, "Não é possível mudar de PENDENTE para RESOLVIDO."):
            estado_de("PENDENTE").ir_para(StatusAlerta.RESOLVIDO)


if __name__ == "__main__":
    unittest.main()
