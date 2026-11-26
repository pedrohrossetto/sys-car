"""Classe Poligono (ADR-C05): validação, centroide, área, ponto dentro e sobreposição."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from model.geometria import Poligono


def quadrado(lat, lon, lado):
    """Quadrado com canto sudoeste em (lat, lon)."""
    return Poligono([(lat, lon), (lat, lon + lado), (lat + lado, lon + lado), (lat + lado, lon)])


class TestValidacao(unittest.TestCase):
    def test_menos_de_tres_vertices(self):
        with self.assertRaisesRegex(ValueError, "pelo menos 3 vértices"):
            Poligono([(0, 0), (0, 1)])

    def test_primeiro_vertice_repetido_no_fim_e_aceito(self):
        p = Poligono([(0, 0), (0, 1), (1, 1), (0, 0)])
        self.assertEqual(len(p), 3)

    def test_vertices_seguidos_iguais(self):
        with self.assertRaisesRegex(ValueError, "dois vértices seguidos iguais"):
            Poligono([(0, 0), (0, 1), (0, 1), (1, 1)])

    def test_fora_das_faixas(self):
        with self.assertRaisesRegex(ValueError, "fora das faixas"):
            Poligono([(0, 0), (0, 1), (91, 1)])

    def test_area_zero(self):
        with self.assertRaisesRegex(ValueError, "área do polígono é zero"):
            Poligono([(0, 0), (0, 1), (0, 2)])

    def test_lados_que_se_cruzam(self):
        # "Laço": os lados 1 e 3 se cruzam no meio.
        with self.assertRaisesRegex(ValueError, "não podem se cruzar"):
            Poligono([(0, 0), (1, 1), (0, 1), (1, 0)])

    def test_lado_que_volta_sobre_o_anterior(self):
        with self.assertRaisesRegex(ValueError, "não podem se cruzar"):
            Poligono([(0, 0), (0, 2), (0, 1), (1, 1)])

    def test_texto_ida_e_volta(self):
        p = Poligono.de_texto("-28.2,-52.4; -28.2,-52.39; -28.19,-52.39")
        self.assertEqual(p.vertices, [(-28.2, -52.4), (-28.2, -52.39), (-28.19, -52.39)])
        self.assertEqual(Poligono.de_texto(p.para_texto()), p)

    def test_texto_vazio(self):
        with self.assertRaisesRegex(ValueError, "pelo menos 3 vértices"):
            Poligono.de_texto("")


class TestCalculos(unittest.TestCase):
    def test_centroide_do_quadrado(self):
        lat, lon = quadrado(-28.3, -52.5, 0.02).centroide()
        self.assertAlmostEqual(lat, -28.29)
        self.assertAlmostEqual(lon, -52.49)

    def test_centroide_nao_depende_do_sentido(self):
        p = quadrado(0, 0, 2)
        invertido = Poligono(list(reversed(p.vertices)))
        self.assertEqual(tuple(round(c, 9) for c in p.centroide()),
                         tuple(round(c, 9) for c in invertido.centroide()))

    def test_area_de_quadrado_no_equador(self):
        # 0,01° x 0,01° ~ 1113,2 m x 1105,74 m ~ 123,09 ha
        self.assertAlmostEqual(quadrado(0, 0, 0.01).area_ha(), 123.09, delta=0.1)

    def test_area_diminui_com_a_latitude(self):
        # O mesmo quadrado em graus tem menos metros de largura longe do equador.
        self.assertLess(quadrado(-60, 0, 0.01).area_ha(), quadrado(0, 0, 0.01).area_ha() * 0.55)

    def test_area_de_poligono_concavo(self):
        # "L": quadrado 2x2 sem o canto 1x1 => 3/4 da área do quadrado.
        letra_l = Poligono([(0, 0), (0, 0.02), (0.01, 0.02), (0.01, 0.01), (0.02, 0.01), (0.02, 0)])
        self.assertAlmostEqual(letra_l.area_ha(), quadrado(0, 0, 0.02).area_ha() * 0.75, delta=0.5)


class TestContem(unittest.TestCase):
    def setUp(self):
        self.q = quadrado(0, 0, 1)

    def test_dentro_fora_e_borda(self):
        self.assertTrue(self.q.contem(0.5, 0.5))
        self.assertFalse(self.q.contem(1.5, 0.5))
        self.assertFalse(self.q.contem(0.5, -0.1))
        self.assertTrue(self.q.contem(0, 0.5))   # na borda
        self.assertTrue(self.q.contem(1, 1))     # no vértice

    def test_concavo(self):
        letra_l = Poligono([(0, 0), (0, 2), (1, 2), (1, 1), (2, 1), (2, 0)])
        self.assertTrue(letra_l.contem(0.5, 1.5))
        self.assertTrue(letra_l.contem(1.5, 0.5))
        self.assertFalse(letra_l.contem(1.5, 1.5))  # o canto que falta


class TestSobreposicao(unittest.TestCase):
    def test_separados(self):
        self.assertFalse(quadrado(0, 0, 1).sobrepoe(quadrado(0, 2, 1)))

    def test_encostados_num_lado_nao_sobrepoem(self):
        self.assertFalse(quadrado(0, 0, 1).sobrepoe(quadrado(0, 1, 1)))

    def test_encostados_num_vertice_nao_sobrepoem(self):
        self.assertFalse(quadrado(0, 0, 1).sobrepoe(quadrado(1, 1, 1)))

    def test_lados_que_se_cruzam(self):
        self.assertTrue(quadrado(0, 0, 1).sobrepoe(quadrado(0.5, 0.5, 1)))

    def test_um_dentro_do_outro(self):
        grande, pequeno = quadrado(0, 0, 3), quadrado(1, 1, 1)
        self.assertTrue(grande.sobrepoe(pequeno))
        self.assertTrue(pequeno.sobrepoe(grande))

    def test_iguais(self):
        self.assertTrue(quadrado(0, 0, 1).sobrepoe(quadrado(0, 0, 1)))

    def test_dentro_compartilhando_dois_lados(self):
        self.assertTrue(quadrado(0, 0, 2).sobrepoe(quadrado(0, 0, 1)))

    def test_lado_parcialmente_comum_com_interior_em_comum(self):
        a = Poligono([(0, 0), (0, 2), (1, 2), (1, 0)])
        b = Poligono([(0, 1), (0, 3), (1, 3), (1, 1)])
        self.assertTrue(a.sobrepoe(b))

    def test_cruz(self):
        # Dois retângulos em cruz: nenhum vértice de um dentro do outro.
        horizontal = Poligono([(1, 0), (1, 3), (2, 3), (2, 0)])
        vertical = Poligono([(0, 1), (0, 2), (3, 2), (3, 1)])
        self.assertTrue(horizontal.sobrepoe(vertical))


if __name__ == "__main__":
    unittest.main()
