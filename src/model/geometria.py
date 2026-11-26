"""Geometria da área de uma propriedade (ADR-C05).

Poligono é um objeto de valor: não tem tabela. A propriedade guarda o
polígono como texto 'lat,lon;lat,lon;...' (model/coordenadas.py) e cria
um Poligono quando precisa calcular algo.

Convenção: cada vértice é um par (lat, lon). Nos cálculos planos, x é a
longitude e y é a latitude.
"""
import math

from model.coordenadas import converter_poligono, formatar_poligono

# Metros por grau de latitude e por grau de longitude no equador.
METROS_POR_GRAU_LAT = 110_574.0
METROS_POR_GRAU_LON = 111_320.0
_EPS = 1e-12


def _orientacao(a, b, c):
    """> 0: a->b->c gira à esquerda; < 0: à direita; 0: colineares. Pontos (x, y)."""
    valor = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if abs(valor) < _EPS:
        return 0
    return 1 if valor > 0 else -1


def _no_segmento(p, a, b):
    """True se p está sobre o segmento a-b (incluindo as pontas)."""
    return (_orientacao(a, b, p) == 0
            and min(a[0], b[0]) - _EPS <= p[0] <= max(a[0], b[0]) + _EPS
            and min(a[1], b[1]) - _EPS <= p[1] <= max(a[1], b[1]) + _EPS)


def _segmentos_cruzam(a, b, c, d):
    """True se os segmentos a-b e c-d têm algum ponto em comum."""
    o1, o2 = _orientacao(a, b, c), _orientacao(a, b, d)
    o3, o4 = _orientacao(c, d, a), _orientacao(c, d, b)
    if o1 != o2 and o3 != o4 and 0 not in (o1, o2, o3, o4):
        return True
    return (_no_segmento(c, a, b) or _no_segmento(d, a, b)
            or _no_segmento(a, c, d) or _no_segmento(b, c, d))


def _cruzam_propriamente(a, b, c, d):
    """True se a-b e c-d se cruzam num ponto interior aos dois (encostar não conta)."""
    o1, o2 = _orientacao(a, b, c), _orientacao(a, b, d)
    o3, o4 = _orientacao(c, d, a), _orientacao(c, d, b)
    return 0 not in (o1, o2, o3, o4) and o1 != o2 and o3 != o4


class Poligono:
    """Área fechada definida por vértices (lat, lon), em ordem."""

    def __init__(self, vertices):
        pontos = [(float(lat), float(lon)) for lat, lon in vertices]
        if len(pontos) > 1 and pontos[0] == pontos[-1]:
            pontos.pop()  # aceita o primeiro vértice repetido no fim
        if len(pontos) < 3:
            raise ValueError("O polígono precisa de pelo menos 3 vértices.")
        for numero, (lat, lon) in enumerate(pontos, start=1):
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError(f"O vértice {numero} está fora das faixas de latitude e longitude.")
        for i in range(len(pontos)):
            if pontos[i] == pontos[(i + 1) % len(pontos)]:
                raise ValueError("O polígono tem dois vértices seguidos iguais.")
        self._vertices = tuple(pontos)
        xy = self._xy()
        if all(_orientacao(xy[0], xy[1], p) == 0 for p in xy[2:]):
            raise ValueError("A área do polígono é zero.")  # todos os vértices numa reta
        if self._auto_intersecta():
            raise ValueError("Os lados do polígono não podem se cruzar.")
        if abs(self._area_graus()) < _EPS:
            raise ValueError("A área do polígono é zero.")

    # ---------------- texto ----------------
    @classmethod
    def de_texto(cls, texto):
        """Lê 'lat,lon;lat,lon;...' (ver model/coordenadas.py)."""
        return cls(converter_poligono(texto))

    def para_texto(self):
        return formatar_poligono(self._vertices)

    # ---------------- dados ----------------
    @property
    def vertices(self):
        return list(self._vertices)

    def __len__(self):
        return len(self._vertices)

    def __eq__(self, outro):
        return isinstance(outro, Poligono) and self._vertices == outro._vertices

    def __repr__(self):
        return f"Poligono({self.para_texto()!r})"

    def _xy(self):
        """Vértices como (x, y) = (lon, lat)."""
        return [(lon, lat) for lat, lon in self._vertices]

    def _lados(self):
        xy = self._xy()
        return [(xy[i], xy[(i + 1) % len(xy)]) for i in range(len(xy))]

    # ---------------- cálculos ----------------
    def _area_graus(self):
        """Área com sinal (fórmula do shoelace), em graus quadrados."""
        return sum(a[0] * b[1] - b[0] * a[1] for a, b in self._lados()) / 2

    def centroide(self):
        """Centro de massa da área, como (lat, lon)."""
        area = self._area_graus()
        cx = cy = 0.0
        for a, b in self._lados():
            fator = a[0] * b[1] - b[0] * a[1]
            cx += (a[0] + b[0]) * fator
            cy += (a[1] + b[1]) * fator
        return (cy / (6 * area), cx / (6 * area))

    def area_ha(self):
        """Área em hectares, projetando os vértices em metros em torno da latitude média."""
        lat0 = math.radians(sum(lat for lat, _ in self._vertices) / len(self._vertices))
        metros = [(lon * METROS_POR_GRAU_LON * math.cos(lat0), lat * METROS_POR_GRAU_LAT)
                  for lat, lon in self._vertices]
        soma = sum(metros[i][0] * metros[(i + 1) % len(metros)][1]
                   - metros[(i + 1) % len(metros)][0] * metros[i][1]
                   for i in range(len(metros)))
        return abs(soma) / 2 / 10_000

    # ---------------- relações com pontos ----------------
    def na_borda(self, lat, lon):
        p = (lon, lat)
        return any(_no_segmento(p, a, b) for a, b in self._lados())

    def _dentro_estrito(self, lat, lon):
        """Ray casting: True se o ponto está no interior (a borda não conta)."""
        if self.na_borda(lat, lon):
            return False
        x, y = lon, lat
        dentro = False
        for (x1, y1), (x2, y2) in self._lados():
            if (y1 > y) != (y2 > y):
                x_cruzamento = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if x < x_cruzamento:
                    dentro = not dentro
        return dentro

    def contem(self, lat, lon):
        """True se o ponto está dentro da área. Um ponto na borda conta como dentro."""
        return self.na_borda(lat, lon) or self._dentro_estrito(lat, lon)

    # ---------------- relações com outro polígono ----------------
    def _pontos_de_teste(self):
        """Vértices, pontos médios dos lados e o centroide (se ele estiver dentro)."""
        pontos = list(self._vertices)
        pontos += [((a[1] + b[1]) / 2, (a[0] + b[0]) / 2) for a, b in self._lados()]
        centro = self.centroide()
        if self._dentro_estrito(*centro):
            pontos.append(centro)
        return pontos

    def sobrepoe(self, outro):
        """True se as duas áreas têm interior em comum. Encostar num lado ou num vértice não conta."""
        for a, b in self._lados():
            for c, d in outro._lados():
                if _cruzam_propriamente(a, b, c, d):
                    return True
        return (any(outro._dentro_estrito(*p) for p in self._pontos_de_teste())
                or any(self._dentro_estrito(*p) for p in outro._pontos_de_teste()))

    def _auto_intersecta(self):
        lados = self._lados()
        n = len(lados)
        for i in range(n):
            for j in range(i + 1, n):
                vizinhos = j == i + 1 or (i == 0 and j == n - 1)
                a, b = lados[i]
                c, d = lados[j]
                if not vizinhos:
                    if _segmentos_cruzam(a, b, c, d):
                        return True
                    continue
                # Lados vizinhos só podem ter o vértice comum: não podem voltar sobre si mesmos.
                comum = b if b == c else a
                p = a if comum == b else b
                q = d if comum == c else c
                volta = (p[0] - comum[0]) * (q[0] - comum[0]) + (p[1] - comum[1]) * (q[1] - comum[1])
                if _orientacao(p, comum, q) == 0 and volta > 0:
                    return True
        return False
