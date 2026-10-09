import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.localizacao_controller import LocalizacaoController
from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.proprietario_controller import ProprietarioController
from database import database
from model.coordenadas import converter_poligono, formatar_poligono
from model.propriedade_rural import PropriedadeRural
from test_cadastro_apoio import BancoTemporario


class TestPoligono(unittest.TestCase):
    def test_normaliza_espacos_e_virgula_decimal(self):
        pontos = converter_poligono(" -28.1 , -52.3 ;-28.2,-52.3; -28.2,-52.4 ")
        self.assertEqual(formatar_poligono(pontos), "-28.1,-52.3;-28.2,-52.3;-28.2,-52.4")

    def test_vazio_vira_lista_vazia(self):
        self.assertEqual(converter_poligono("  "), [])

    def test_menos_de_tres_vertices(self):
        with self.assertRaisesRegex(ValueError, "pelo menos 3"):
            converter_poligono("1,1;2,2")

    def test_vertice_mal_formado(self):
        with self.assertRaisesRegex(ValueError, "Vértice 2"):
            converter_poligono("1,1;2;3,3")

    def test_vertice_fora_da_faixa(self):
        with self.assertRaisesRegex(ValueError, "Latitude do vértice 3"):
            converter_poligono("1,1;2,2;91,3")


class TestPropriedadeELocalizacao(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.dono, _ = ProprietarioController().criar("Ana", "PF", cpf="529.982.247-25")
        self.props = PropriedadeRuralController()
        self.locs = LocalizacaoController()
        self.prop, _ = self.props.criar("Sítio Boa Vista", self.dono.id, "RS-123")

    def test_propriedade_com_proprietario_inexistente(self):
        self.assertEqual(self.props.criar("X", 999)[1], "Proprietário não encontrado.")
        self.assertEqual(self.props.criar("X", None)[1], "Proprietário não encontrado.")

    def test_propriedade_nome_obrigatorio(self):
        self.assertEqual(self.props.criar("  ", self.dono.id)[1], "Nome é obrigatório.")

    def test_propriedade_cadastro_vazio_vira_none(self):
        p, _ = self.props.criar("Outra", self.dono.id, "   ")
        self.assertIsNone(self.props.buscar_por_id(p.id).cadastro_publico)

    def test_localizacao_valida_com_poligono(self):
        loc, erro = self.locs.criar(self.prop.id, "-28,26", "-52.4", "", "1,1;1,2;2,2")
        self.assertIsNone(erro)
        salva = self.locs.buscar_por_id(loc.id)
        self.assertEqual((salva.latitude, salva.longitude, salva.altitude), (-28.26, -52.4, None))
        self.assertEqual(salva.poligono_geometria, "1,1;1,2;2,2")

    def test_latitude_e_longitude_fora_da_faixa(self):
        self.assertEqual(self.locs.criar(self.prop.id, 91, 0)[1],
                         "Latitude deve estar entre -90 e 90.")
        self.assertEqual(self.locs.criar(self.prop.id, 0, -181)[1],
                         "Longitude deve estar entre -180 e 180.")

    def test_texto_nao_numerico_nao_chega_ao_banco(self):
        self.assertEqual(self.locs.criar(self.prop.id, "abc", 0)[1],
                         "Latitude deve ser um número.")
        self.assertEqual(self.locs.criar(self.prop.id, 0, 0, "alto")[1],
                         "Altitude deve ser um número.")
        self.assertEqual(self.locs.listar(), [])

    def test_latitude_obrigatoria(self):
        self.assertEqual(self.locs.criar(self.prop.id, "", 0)[1], "Latitude é obrigatória.")

    def test_segunda_localizacao_da_mesma_propriedade(self):
        self.locs.criar(self.prop.id, 0, 0)
        self.assertEqual(self.locs.criar(self.prop.id, 1, 1)[1],
                         "Esta propriedade já possui uma localização.")

    def test_atualizar_localizacao(self):
        loc, _ = self.locs.criar(self.prop.id, 0, 0)
        _, erro = self.locs.atualizar(loc.id, self.prop.id, 10, 20, 300)
        self.assertIsNone(erro)
        self.assertEqual(self.locs.buscar_por_id(loc.id).altitude, 300.0)

    def test_localizacao_de_propriedade_inexistente(self):
        self.assertEqual(self.locs.criar(999, 0, 0)[1], "Propriedade não encontrada.")


class TestCascade(BancoTemporario):
    def test_apagar_proprietario_apaga_propriedades_e_localizacoes(self):
        dono, _ = ProprietarioController().criar("Ana", "PF", cpf="52998224725")
        prop, _ = PropriedadeRuralController().criar("Sítio", dono.id)
        LocalizacaoController().criar(prop.id, 0, 0)
        ProprietarioController().excluir(dono.id)
        self.assertEqual(PropriedadeRuralController().listar(), [])
        self.assertEqual(LocalizacaoController().listar(), [])


class TestContratoComFiscalizacao(BancoTemporario):
    """Itens do contrato congelado que a Frente 2 usa. NÃO remova estes testes."""

    def test_metodos_e_atributos_de_propriedade(self):
        dono, _ = ProprietarioController().criar("Ana", "PF", cpf="52998224725")
        PropriedadeRural("Sítio", dono.id).salvar()
        p = PropriedadeRural.listar_todos()[0]
        self.assertEqual((p.nome, p.proprietario_id), ("Sítio", dono.id))
        self.assertEqual(PropriedadeRural.buscar_por_id(p.id).id, p.id)
        self.assertIsNone(PropriedadeRural.buscar_por_id(999))

    def test_insert_so_com_nome_e_proprietario_funciona(self):
        conn = database.get_connection()
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("INSERT INTO propriedades_rurais (nome, proprietario_id) VALUES ('X', 999)")
            conn.commit()
        finally:
            conn.close()
        self.assertEqual(PropriedadeRural.listar_todos()[0].nome, "X")


if __name__ == "__main__":
    unittest.main()
