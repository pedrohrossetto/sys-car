"""Dados de exemplo da demonstração (issue #11): src/dados_exemplo.py."""
import io
import sys
from contextlib import redirect_stdout
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import dados_exemplo
from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.ficha_controller import FichaController
from database import database


class TestDadosExemplo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._originais = (database.DATA_DIR, database.DB_PATH)
        database.DATA_DIR = Path(self._tmp.name)
        database.DB_PATH = database.DATA_DIR / "exemplo.db"
        database.init_db()

    def tearDown(self):
        database.DATA_DIR, database.DB_PATH = self._originais
        self._tmp.cleanup()

    def test_mostra_as_tres_situacoes(self):
        dados_exemplo.popular()
        ficha = FichaController()
        situacoes = {}
        for propriedade in ficha.listar_propriedades():
            resultado, erro = ficha.montar(propriedade.id)
            self.assertIsNone(erro)
            situacoes[propriedade.nome] = resultado.situacao
        self.assertEqual(situacoes, {
            "Sítio Boa Vista": "COM ALERTAS EM ABERTO",
            "Fazenda Planalto": "EMBARGADA",
            "Chácara Santa Rita": "REGULAR",
        })

    def test_um_alerta_fica_fora_das_areas(self):
        dados_exemplo.popular()
        sem_propriedade = [a for a in AlertaController().listar() if a.propriedade_id is None]
        self.assertEqual(len(sem_propriedade), 1)

    def test_nao_grava_em_banco_com_dados(self):
        dados_exemplo.popular()
        self.assertFalse(dados_exemplo.banco_vazio())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(dados_exemplo.main(), 1)


if __name__ == "__main__":
    unittest.main()
