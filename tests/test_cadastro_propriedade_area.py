"""Propriedade rural com área obrigatória (ADR-C05)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.proprietario_controller import ProprietarioController
from database import database
from model.coordenadas import converter_poligono, formatar_poligono
from model.propriedade_rural import PropriedadeRural
from test_cadastro_apoio import BancoTemporario

AREA = "-28.26,-52.41;-28.26,-52.40;-28.25,-52.40;-28.25,-52.41"
VIZINHA = "-28.26,-52.40;-28.26,-52.39;-28.25,-52.39;-28.25,-52.40"      # encosta no lado leste
SOBREPOSTA = "-28.255,-52.405;-28.255,-52.395;-28.245,-52.395;-28.245,-52.405"


class TestTextoDoPoligono(unittest.TestCase):
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


class TestPropriedade(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.dono, _ = ProprietarioController().criar("Ana", "PF", cpf="529.982.247-25")
        self.props = PropriedadeRuralController()
        self.prop, erro = self.props.criar("Sítio Boa Vista", self.dono.id, "RS-123", AREA)
        self.assertIsNone(erro)

    def test_propriedade_com_proprietario_inexistente(self):
        self.assertEqual(self.props.criar("X", 999, None, VIZINHA)[1], "Proprietário não encontrado.")
        self.assertEqual(self.props.criar("X", None, None, VIZINHA)[1], "Proprietário não encontrado.")

    def test_propriedade_nome_obrigatorio(self):
        self.assertEqual(self.props.criar("  ", self.dono.id, None, VIZINHA)[1], "Nome é obrigatório.")

    def test_propriedade_cadastro_vazio_vira_none(self):
        p, _ = self.props.criar("Outra", self.dono.id, "   ", VIZINHA)
        self.assertIsNone(self.props.buscar_por_id(p.id).cadastro_publico)

    def test_area_obrigatoria(self):
        for vazio in (None, "", "   ", []):
            with self.subTest(poligono=vazio):
                self.assertEqual(self.props.criar("Outra", self.dono.id, None, vazio)[1],
                                 "Desenhe a área da propriedade no mapa.")

    def test_area_invalida(self):
        self.assertEqual(self.props.criar("Outra", self.dono.id, None, "1,1;2,2")[1],
                         "O polígono precisa de pelo menos 3 vértices.")
        self.assertEqual(self.props.criar("Outra", self.dono.id, None, [(0, 0), (1, 1), (0, 1), (1, 0)])[1],
                         "Os lados do polígono não podem se cruzar.")
        self.assertEqual(len(self.props.listar()), 1)

    def test_area_aceita_lista_de_pares_e_grava_texto_normalizado(self):
        p, erro = self.props.criar("Outra", self.dono.id, None,
                                   [(-28.26, -52.40), (-28.26, -52.39), (-28.25, -52.39)])
        self.assertIsNone(erro)
        self.assertEqual(self.props.buscar_por_id(p.id).poligono, "-28.26,-52.4;-28.26,-52.39;-28.25,-52.39")

    def test_area_vizinha_que_so_encosta_e_aceita(self):
        self.assertIsNone(self.props.criar("Vizinha", self.dono.id, None, VIZINHA)[1])

    def test_area_sobreposta_e_rejeitada_ao_criar(self):
        self.assertEqual(self.props.criar("Outra", self.dono.id, None, SOBREPOSTA)[1],
                         f"A área se sobrepõe à da propriedade Sítio Boa Vista (#{self.prop.id}).")

    def test_area_sobreposta_e_rejeitada_ao_atualizar(self):
        vizinha, _ = self.props.criar("Vizinha", self.dono.id, None, VIZINHA)
        self.assertIn("se sobrepõe", self.props.atualizar(vizinha.id, "Vizinha", self.dono.id, None, SOBREPOSTA)[1])

    def test_atualizar_a_propria_area_nao_acusa_sobreposicao_consigo(self):
        _, erro = self.props.atualizar(self.prop.id, "Sítio", self.dono.id, None, SOBREPOSTA)
        self.assertIsNone(erro)
        self.assertEqual(self.props.buscar_por_id(self.prop.id).poligono,
                         "-28.255,-52.405;-28.255,-52.395;-28.245,-52.395;-28.245,-52.405")

    def test_centroide_e_area_calculados(self):
        salva = self.props.buscar_por_id(self.prop.id)
        lat, lon = salva.centroide
        self.assertAlmostEqual(lat, -28.255)
        self.assertAlmostEqual(lon, -52.405)
        self.assertAlmostEqual(salva.area_ha, 108.4, delta=0.5)  # 0,01° x 0,01° a 28°S
        self.assertTrue(salva.contem(-28.255, -52.405))
        self.assertFalse(salva.contem(-28.255, -52.395))

    def test_listar_areas(self):
        vizinha, _ = self.props.criar("Vizinha", self.dono.id, None, VIZINHA)
        self.assertEqual([(i, n) for i, n, _ in self.props.listar_areas()],
                         [(self.prop.id, "Sítio Boa Vista"), (vizinha.id, "Vizinha")])
        self.assertEqual([i for i, _, _ in self.props.listar_areas(exceto_id=self.prop.id)], [vizinha.id])


class TestCascade(BancoTemporario):
    def test_apagar_proprietario_apaga_propriedades(self):
        dono, _ = ProprietarioController().criar("Ana", "PF", cpf="52998224725")
        PropriedadeRuralController().criar("Sítio", dono.id, None, AREA)
        ProprietarioController().excluir(dono.id)
        self.assertEqual(PropriedadeRuralController().listar(), [])


class TestBancoAntigo(BancoTemporario):
    CRIAR_TABELAS = False

    def test_tabela_sem_poligono_e_detectada(self):
        controller = PropriedadeRuralController()
        self.assertFalse(controller.banco_desatualizado())  # tabela ainda não existe
        conn = database.get_connection()
        try:
            conn.execute("CREATE TABLE propriedades_rurais (id INTEGER PRIMARY KEY, nome TEXT, "
                         "cadastro_publico TEXT, proprietario_id INTEGER)")
            conn.commit()
        finally:
            conn.close()
        self.assertTrue(controller.banco_desatualizado())


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
        p = PropriedadeRural.listar_todos()[0]
        self.assertEqual(p.nome, "X")
        self.assertEqual((p.area, p.centroide, p.area_ha, p.contem(0, 0)), (None, None, None, False))


if __name__ == "__main__":
    unittest.main()
