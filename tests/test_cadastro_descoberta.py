import tempfile
import textwrap
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from descoberta import modulos_com, ordenar_por_ordem


class TestDescobertaDeModulos(unittest.TestCase):
    """Cria um pacote falso em disco e confere o que a descoberta encontra."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        raiz = Path(self._tmp.name) / "pacote_teste_abas"
        (raiz / "sub").mkdir(parents=True)
        arquivos = {
            "__init__.py": "",
            "b.py": "ORDEM = 20\ndef registrar_abas(nb): pass\n",
            "a.py": "ORDEM = 20\ndef registrar_abas(nb): pass\n",
            "c.py": "def registrar_abas(nb): pass\n",
            "sem_aba.py": "X = 1\n",
            "_oculto.py": "raise RuntimeError('não devia ser importado')\n",
            "sub/__init__.py": "",
            "sub/d.py": "ORDEM = 5\ndef registrar_abas(nb): pass\n",
        }
        for nome, conteudo in arquivos.items():
            (raiz / nome).write_text(textwrap.dedent(conteudo), encoding="utf-8")
        sys.path.insert(0, self._tmp.name)

    def tearDown(self):
        sys.path.remove(self._tmp.name)
        for nome in [m for m in sys.modules if m.startswith("pacote_teste_abas")]:
            del sys.modules[nome]
        self._tmp.cleanup()

    def test_ordena_por_ordem_e_nome_e_ignora_underscore(self):
        import pacote_teste_abas

        modulos = modulos_com(pacote_teste_abas, "registrar_abas")
        nomes = [m.__name__ for m in ordenar_por_ordem(modulos)]
        self.assertEqual(nomes, [
            "pacote_teste_abas.sub.d",
            "pacote_teste_abas.a",
            "pacote_teste_abas.b",
            "pacote_teste_abas.c",
        ])

    def test_modulo_sem_o_atributo_fica_de_fora(self):
        import pacote_teste_abas

        nomes = [m.__name__ for m in modulos_com(pacote_teste_abas, "X")]
        self.assertEqual(nomes, ["pacote_teste_abas.sem_aba"])


if __name__ == "__main__":
    unittest.main()
