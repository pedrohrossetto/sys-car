"""Conversão entre coordenadas geográficas e pixels do mapa (ADR-002).

Não importa tkinter: os testes rodam em máquinas sem Tk.

Projeção equirretangular: um grau de latitude tem sempre a mesma altura
em pixels; um grau de longitude é estreitado por cos(latitude de
referência), para as áreas não aparecerem esticadas. A latitude de
referência só muda ao enquadrar, então mover e dar zoom não deformam
o desenho.
"""
import math

# Vista inicial sem nada para enquadrar: Passo Fundo (RS).
CENTRO_PADRAO = (-28.26, -52.41)
ALTURA_PADRAO_GRAUS = 0.3
ESCALA_MINIMA = 2.0          # pixels por grau: o Brasil inteiro cabe
ESCALA_MAXIMA = 5_000_000.0  # ~2 cm por pixel
PASSOS_GRADE = (10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001,
                0.0005, 0.0002, 0.0001, 0.00005, 0.00002, 0.00001)


class Projecao:
    def __init__(self, largura, altura, centro=CENTRO_PADRAO, altura_graus=ALTURA_PADRAO_GRAUS):
        self.largura = max(int(largura), 1)
        self.altura = max(int(altura), 1)
        self.centro = tuple(centro)
        self.escala = self._limitar(self.altura / altura_graus)  # pixels por grau de latitude
        self._fator_lon = math.cos(math.radians(self.centro[0]))

    @staticmethod
    def _limitar(escala):
        return min(max(escala, ESCALA_MINIMA), ESCALA_MAXIMA)

    @property
    def _escala_lon(self):
        return self.escala * self._fator_lon

    # ---------------- conversões ----------------
    def para_pixel(self, lat, lon):
        x = self.largura / 2 + (lon - self.centro[1]) * self._escala_lon
        y = self.altura / 2 - (lat - self.centro[0]) * self.escala
        return x, y

    def para_geo(self, x, y):
        lat = self.centro[0] - (y - self.altura / 2) / self.escala
        lon = self.centro[1] + (x - self.largura / 2) / self._escala_lon
        return lat, lon

    def limites(self):
        """(lat_min, lat_max, lon_min, lon_max) da área visível."""
        lat_max, lon_min = self.para_geo(0, 0)
        lat_min, lon_max = self.para_geo(self.largura, self.altura)
        return lat_min, lat_max, lon_min, lon_max

    # ---------------- navegação ----------------
    def redimensionar(self, largura, altura):
        self.largura, self.altura = max(int(largura), 1), max(int(altura), 1)

    def mover(self, dx, dy):
        """Arrasta o mapa dx, dy pixels (o conteúdo acompanha o mouse)."""
        self.centro = (self.centro[0] + dy / self.escala, self.centro[1] - dx / self._escala_lon)

    def zoom(self, fator, x, y):
        """Multiplica a escala mantendo parado o ponto que está sob o pixel (x, y)."""
        lat, lon = self.para_geo(x, y)
        self.escala = self._limitar(self.escala * fator)
        self.centro = (lat + (y - self.altura / 2) / self.escala,
                       lon - (x - self.largura / 2) / self._escala_lon)

    def enquadrar(self, pontos, margem=0.1, minimo_graus=0.005):
        """Centraliza e escolhe a escala para todos os pontos (lat, lon) caberem."""
        pontos = list(pontos)
        if not pontos:  # nada para mostrar: volta à vista padrão
            self.centro = CENTRO_PADRAO
            self._fator_lon = math.cos(math.radians(CENTRO_PADRAO[0]))
            self.escala = self._limitar(self.altura / ALTURA_PADRAO_GRAUS)
            return
        lats = [lat for lat, _ in pontos]
        lons = [lon for _, lon in pontos]
        self.centro = ((min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2)
        self._fator_lon = math.cos(math.radians(self.centro[0]))
        altura_graus = max(max(lats) - min(lats), minimo_graus) * (1 + 2 * margem)
        largura_graus = max(max(lons) - min(lons), minimo_graus) * (1 + 2 * margem)
        self.escala = self._limitar(min(self.altura / altura_graus,
                                        self.largura / (largura_graus * self._fator_lon)))

    # ---------------- grade ----------------
    def passo_grade(self, minimo_pixels=70):
        """Maior passo (em graus) cujas linhas ficam a pelo menos 'minimo_pixels' umas das outras."""
        escolhido = PASSOS_GRADE[0]
        for passo in PASSOS_GRADE:
            if passo * self._escala_lon < minimo_pixels:
                break
            escolhido = passo
        return escolhido

    @staticmethod
    def casas_decimais(passo):
        """Casas decimais para escrever os rótulos da grade sem repetir valores."""
        return max(0, math.ceil(-math.log10(passo) - 1e-9))

    def linhas_grade(self):
        """(passo, latitudes, longitudes) das linhas de grade visíveis."""
        passo = self.passo_grade()
        lat_min, lat_max, lon_min, lon_max = self.limites()

        def valores(inicio, fim):
            primeiro = math.ceil(inicio / passo)
            ultimo = math.floor(fim / passo)
            return [round(i * passo, 6) for i in range(primeiro, ultimo + 1)]

        return passo, valores(lat_min, lat_max), valores(lon_min, lon_max)
