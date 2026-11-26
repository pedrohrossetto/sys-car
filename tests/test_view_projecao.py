"""Projecao do mapa (ADR-002). Não precisa de Tk."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from view.projecao import CENTRO_PADRAO, ESCALA_MAXIMA, ESCALA_MINIMA, Projecao


class TestConversoes(unittest.TestCase):
    def setUp(self):
        self.p = Projecao(500, 400, centro=(-28.0, -52.0), altura_graus=1.0)

    def test_centro_fica_no_meio_da_tela(self):
        self.assertEqual(self.p.para_pixel(-28.0, -52.0), (250, 200))

    def test_norte_em_cima_e_leste_a_direita(self):
        x, y = self.p.para_pixel(-27.9, -51.9)
        self.assertGreater(x, 250)
        self.assertLess(y, 200)

    def test_ida_e_volta(self):
        for lat, lon in ((-28.3, -52.4), (-27.6, -51.7), (-28.0, -52.0)):
            x, y = self.p.para_pixel(lat, lon)
            lat2, lon2 = self.p.para_geo(x, y)
            self.assertAlmostEqual(lat, lat2)
            self.assertAlmostEqual(lon, lon2)

    def test_longitude_e_estreitada_pelo_cosseno(self):
        x1, _ = self.p.para_pixel(-28.0, -52.0)
        x2, _ = self.p.para_pixel(-28.0, -51.0)
        _, y2 = self.p.para_pixel(-27.0, -52.0)
        self.assertAlmostEqual((x2 - x1) / (200 - y2), math.cos(math.radians(28)))

    def test_limites_da_tela(self):
        lat_min, lat_max, lon_min, lon_max = self.p.limites()
        self.assertAlmostEqual(lat_max - lat_min, 1.0)
        self.assertAlmostEqual((lat_min + lat_max) / 2, -28.0)
        self.assertAlmostEqual((lon_min + lon_max) / 2, -52.0)


class TestNavegacao(unittest.TestCase):
    def setUp(self):
        self.p = Projecao(500, 400, centro=(-28.0, -52.0), altura_graus=1.0)

    def test_zoom_mantem_o_ponto_sob_o_cursor(self):
        antes = self.p.para_geo(100, 300)
        self.p.zoom(2.0, 100, 300)
        depois = self.p.para_geo(100, 300)
        self.assertAlmostEqual(antes[0], depois[0])
        self.assertAlmostEqual(antes[1], depois[1])
        self.assertAlmostEqual(self.p.escala, 800)

    def test_zoom_respeita_os_limites(self):
        for _ in range(100):
            self.p.zoom(10, 0, 0)
        self.assertEqual(self.p.escala, ESCALA_MAXIMA)
        for _ in range(100):
            self.p.zoom(0.1, 0, 0)
        self.assertEqual(self.p.escala, ESCALA_MINIMA)

    def test_mover_acompanha_o_mouse(self):
        alvo = self.p.para_geo(250, 200)
        self.p.mover(30, -20)
        x, y = self.p.para_pixel(*alvo)
        self.assertAlmostEqual(x, 280)
        self.assertAlmostEqual(y, 180)

    def test_mover_e_zoom_nao_deformam(self):
        # A razão largura/altura de um grau não muda ao mover (cosseno fixo).
        antes = self.p._escala_lon / self.p.escala
        self.p.mover(0, 5000)
        self.assertAlmostEqual(self.p._escala_lon / self.p.escala, antes)

    def test_enquadrar_mostra_todos_os_pontos(self):
        pontos = [(-28.30, -52.45), (-28.20, -52.30), (-28.25, -52.40)]
        self.p.enquadrar(pontos)
        for lat, lon in pontos:
            x, y = self.p.para_pixel(lat, lon)
            self.assertTrue(0 <= x <= 500 and 0 <= y <= 400, (lat, lon, x, y))
        self.assertAlmostEqual(self.p.centro[0], -28.25)
        self.assertAlmostEqual(self.p.centro[1], -52.375)

    def test_enquadrar_um_ponto_so_usa_tamanho_minimo(self):
        self.p.enquadrar([(-28.0, -52.0)])
        lat_min, lat_max, _, _ = self.p.limites()
        self.assertGreater(lat_max - lat_min, 0.004)

    def test_enquadrar_nada_volta_a_vista_padrao(self):
        self.p.enquadrar([])
        self.assertEqual(self.p.centro, CENTRO_PADRAO)

    def test_redimensionar(self):
        self.p.redimensionar(800, 0)
        self.assertEqual((self.p.largura, self.p.altura), (800, 1))


class TestGrade(unittest.TestCase):
    def test_passo_cresce_quando_o_zoom_diminui(self):
        perto = Projecao(500, 400, altura_graus=0.01)
        longe = Projecao(500, 400, altura_graus=5)
        self.assertLess(perto.passo_grade(), longe.passo_grade())

    def test_linhas_visiveis_e_espacadas(self):
        p = Projecao(500, 400, centro=(-28.0, -52.0), altura_graus=1.0)
        passo, lats, lons = p.linhas_grade()
        lat_min, lat_max, lon_min, lon_max = p.limites()
        self.assertTrue(all(lat_min <= v <= lat_max for v in lats))
        self.assertTrue(all(lon_min <= v <= lon_max for v in lons))
        self.assertGreaterEqual(passo * p._escala_lon, 70)

    def test_casas_decimais(self):
        casos = {10: 0, 1: 0, 0.5: 1, 0.1: 1, 0.05: 2, 0.01: 2, 0.002: 3, 0.00005: 5}
        for passo, casas in casos.items():
            with self.subTest(passo=passo):
                self.assertEqual(Projecao.casas_decimais(passo), casas)


if __name__ == "__main__":
    unittest.main()
