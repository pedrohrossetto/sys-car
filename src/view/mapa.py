"""Mapa em Canvas, sem dependência externa (ADR-002).

MapaCanvas desenha uma grade de latitude/longitude, as áreas das
propriedades (polígonos) e os alertas (pontos). Roda do mouse: zoom.
Arrastar com o botão esquerdo: mover. Clicar sem arrastar: chama
ao_clicar(lat, lon).

EditorArea usa o MapaCanvas para desenhar a área de uma propriedade:
cada clique é um vértice.

Este módulo não define registrar_abas: ele não vira aba.
"""
import tkinter as tk
from tkinter import ttk

from model.geometria import Poligono
from view.projecao import Projecao

COR_FUNDO = "#eef3e8"
COR_GRADE = "#d3dccb"
COR_TEXTO_GRADE = "#7a8873"
COR_AREA = "#2e7d32"        # área em destaque (a da propriedade aberta)
COR_VIZINHA = "#8d9a87"     # demais áreas
COR_EDICAO = "#1565c0"
CORES_PONTO = {
    "PENDENTE": "#e0a800",
    "CONFIRMADO": "#c62828",
    "RESOLVIDO": "#2e7d32",
    "CANCELADO": "#757575",
    "NOVO": "#1565c0",       # ponto ainda não salvo
}
RAIO_PONTO = 6
LIMIAR_ARRASTO = 4  # pixels: abaixo disso, o gesto é um clique


class MapaCanvas(ttk.Frame):
    def __init__(self, parent, largura=520, altura=360, ao_clicar=None):
        super().__init__(parent)
        self.ao_clicar = ao_clicar
        self.clique_ativo = ao_clicar is not None
        self.projecao = Projecao(largura, altura)
        self.areas = []    # dicts: pontos, rotulo, destaque
        self.pontos = []   # dicts: lat, lon, status, rotulo
        self.edicao = []   # vértices da área em edição
        self._inicio = None
        self._arrastou = False

        self.canvas = tk.Canvas(self, width=largura, height=altura, background=COR_FUNDO,
                                highlightthickness=1, highlightbackground="#b5bfae",
                                cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        self.coordenadas = ttk.Label(barra, text="", foreground="gray")
        self.coordenadas.pack(side="left")
        ttk.Button(barra, text="Enquadrar tudo", command=self.enquadrar_tudo).pack(side="right")
        ttk.Label(barra, text="Roda: zoom · Arrastar: mover", foreground="gray").pack(side="right", padx=8)

        self.canvas.bind("<Configure>", self._ao_redimensionar)
        self.canvas.bind("<ButtonPress-1>", self._ao_pressionar)
        self.canvas.bind("<B1-Motion>", self._ao_arrastar)
        self.canvas.bind("<ButtonRelease-1>", self._ao_soltar)
        self.canvas.bind("<MouseWheel>", self._ao_rodar)                    # Windows e macOS
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.25, e.x, e.y))  # Linux
        self.canvas.bind("<Button-5>", lambda e: self._zoom(0.8, e.x, e.y))
        self.canvas.bind("<Motion>", self._ao_mover_mouse)
        self.canvas.bind("<Leave>", lambda e: self.coordenadas.config(text=""))

    # ---------------- dados ----------------
    def definir_areas(self, areas, destaque_id=None):
        """areas: [(id, nome, Poligono)]. A de destaque_id aparece em verde."""
        self.areas = [{"pontos": area.vertices, "rotulo": nome, "destaque": id == destaque_id}
                      for id, nome, area in areas if area is not None]
        self.redesenhar()

    def definir_pontos(self, pontos):
        """pontos: [(lat, lon, status, rótulo)]."""
        self.pontos = [{"lat": lat, "lon": lon, "status": status, "rotulo": rotulo}
                       for lat, lon, status, rotulo in pontos]
        self.redesenhar()

    def definir_edicao(self, vertices):
        self.edicao = list(vertices)
        self.redesenhar()

    def enquadrar(self, pontos):
        self.projecao.enquadrar(pontos)
        self.redesenhar()

    def enquadrar_tudo(self):
        pontos = [p for a in self.areas for p in a["pontos"]] + list(self.edicao)
        pontos += [(p["lat"], p["lon"]) for p in self.pontos]
        self.enquadrar(pontos)

    # ---------------- desenho ----------------
    def redesenhar(self):
        c = self.canvas
        c.delete("all")
        self._desenhar_grade()
        for area in sorted(self.areas, key=lambda a: a["destaque"]):
            self._desenhar_area(area)
        self._desenhar_edicao()
        for ponto in self.pontos:
            self._desenhar_ponto(ponto)

    def _desenhar_grade(self):
        p, c = self.projecao, self.canvas
        passo, lats, lons = p.linhas_grade()
        casas = p.casas_decimais(passo)
        for lat in lats:
            _, y = p.para_pixel(lat, p.centro[1])
            c.create_line(0, y, p.largura, y, fill=COR_GRADE)
            c.create_text(4, y - 2, text=f"{lat:.{casas}f}°", anchor="sw", fill=COR_TEXTO_GRADE,
                          font=("TkDefaultFont", 8))
        for lon in lons:
            x, _ = p.para_pixel(p.centro[0], lon)
            c.create_line(x, 0, x, p.altura, fill=COR_GRADE)
            c.create_text(x + 2, p.altura - 2, text=f"{lon:.{casas}f}°", anchor="sw",
                          fill=COR_TEXTO_GRADE, font=("TkDefaultFont", 8))

    def _coords(self, pontos):
        return [v for lat, lon in pontos for v in self.projecao.para_pixel(lat, lon)]

    def _desenhar_area(self, area):
        cor = COR_AREA if area["destaque"] else COR_VIZINHA
        # stipple deixa o preenchimento "transparente" (no macOS o Tk ignora e pinta sólido).
        self.canvas.create_polygon(self._coords(area["pontos"]), fill=cor, stipple="gray25",
                                   outline=cor, width=2)
        try:
            lat, lon = Poligono(area["pontos"]).centroide()
            x, y = self.projecao.para_pixel(lat, lon)
            # Um pouco acima do centroide, para um alerta no centro não cobrir o nome.
            self.canvas.create_text(x, y - 14, text=area["rotulo"], fill="#1b3a1d",
                                    font=("TkDefaultFont", 9, "bold"))
        except ValueError:
            pass

    def _desenhar_edicao(self):
        if not self.edicao:
            return
        coords = self._coords(self.edicao)
        if len(self.edicao) >= 3:
            self.canvas.create_polygon(coords, fill=COR_EDICAO, stipple="gray25",
                                       outline=COR_EDICAO, width=2, dash=(4, 2))
        elif len(self.edicao) == 2:
            self.canvas.create_line(coords, fill=COR_EDICAO, width=2, dash=(4, 2))
        for numero, (lat, lon) in enumerate(self.edicao, start=1):
            x, y = self.projecao.para_pixel(lat, lon)
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", outline=COR_EDICAO, width=2)
            self.canvas.create_text(x + 7, y - 7, text=str(numero), fill=COR_EDICAO,
                                    font=("TkDefaultFont", 8))

    def _desenhar_ponto(self, ponto):
        x, y = self.projecao.para_pixel(ponto["lat"], ponto["lon"])
        cor = CORES_PONTO.get(ponto["status"], CORES_PONTO["NOVO"])
        r = RAIO_PONTO
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline="white", width=2)
        if ponto["rotulo"]:
            self.canvas.create_text(x + r + 3, y, text=ponto["rotulo"], anchor="w",
                                    font=("TkDefaultFont", 8))

    # ---------------- eventos ----------------
    def _ao_redimensionar(self, evento):
        self.projecao.redimensionar(evento.width, evento.height)
        self.redesenhar()

    def _ao_pressionar(self, evento):
        self._inicio = (evento.x, evento.y)
        self._ultimo = (evento.x, evento.y)
        self._arrastou = False

    def _ao_arrastar(self, evento):
        if self._inicio is None:
            return
        dx, dy = evento.x - self._inicio[0], evento.y - self._inicio[1]
        if not self._arrastou and abs(dx) < LIMIAR_ARRASTO and abs(dy) < LIMIAR_ARRASTO:
            return
        self._arrastou = True
        self.canvas.config(cursor="fleur")
        self.projecao.mover(evento.x - self._ultimo[0], evento.y - self._ultimo[1])
        self._ultimo = (evento.x, evento.y)
        self.redesenhar()

    def _ao_soltar(self, evento):
        clicou = self._inicio is not None and not self._arrastou
        self._inicio = None
        self.canvas.config(cursor="crosshair")
        if clicou and self.clique_ativo and self.ao_clicar:
            self.ao_clicar(*self.projecao.para_geo(evento.x, evento.y))

    def _ao_rodar(self, evento):
        self._zoom(1.25 if evento.delta > 0 else 0.8, evento.x, evento.y)

    def _zoom(self, fator, x, y):
        self.projecao.zoom(fator, x, y)
        self.redesenhar()

    def _ao_mover_mouse(self, evento):
        lat, lon = self.projecao.para_geo(evento.x, evento.y)
        self.coordenadas.config(text=f"{lat:.5f}, {lon:.5f}")


class EditorArea(ttk.Frame):
    """Desenho da área de uma propriedade: cada clique no mapa é um vértice."""

    def __init__(self, parent, largura=520, altura=340, ao_mudar=None):
        super().__init__(parent)
        self.ao_mudar = ao_mudar
        self._vertices = []
        self.mapa = MapaCanvas(self, largura, altura, ao_clicar=self._adicionar)
        self.mapa.pack(fill="both", expand=True)
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(4, 0))
        ttk.Button(barra, text="Desfazer vértice", command=self.desfazer).pack(side="left")
        ttk.Button(barra, text="Limpar área", command=self.limpar).pack(side="left", padx=4)
        self.info = ttk.Label(barra, text="", wraplength=360)
        self.info.pack(side="left", padx=8)
        self._atualizar()

    @property
    def vertices(self):
        return list(self._vertices)

    def definir_vertices(self, vertices, enquadrar=True):
        self._vertices = list(vertices)
        self._atualizar()
        if enquadrar and self._vertices:
            self.mapa.enquadrar(self._vertices)

    def definir_vizinhas(self, areas):
        """areas: [(id, nome, Poligono)] das outras propriedades, em cinza."""
        self.mapa.definir_areas(areas)

    def desfazer(self):
        if self._vertices:
            self._vertices.pop()
            self._atualizar()

    def limpar(self):
        self._vertices = []
        self._atualizar()

    def _adicionar(self, lat, lon):
        self._vertices.append((round(lat, 6), round(lon, 6)))
        self._atualizar()

    def _atualizar(self):
        self.mapa.definir_edicao(self._vertices)
        if len(self._vertices) < 3:
            faltam = 3 - len(self._vertices)
            self.info.config(text=f"Clique no mapa para marcar os vértices (faltam {faltam}).",
                             foreground="gray")
        else:
            try:
                area = Poligono(self._vertices)
            except ValueError as erro:
                self.info.config(text=str(erro), foreground="#b00020")
            else:
                lat, lon = area.centroide()
                self.info.config(
                    text=f"{len(area)} vértices · {area.area_ha():.2f} ha · centro {lat:.5f}, {lon:.5f}",
                    foreground="#1b7f3b")
        if self.ao_mudar:
            self.ao_mudar(self.vertices)
