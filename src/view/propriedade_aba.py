import tkinter as tk
from tkinter import ttk

from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.proprietario_controller import ProprietarioController
from view.aba_crud import AbaCrud
from view.mapa import EditorArea
from view.widgets import Seletor

ORDEM = 20


class PropriedadeAba(AbaCrud):
    """Cadastro de propriedades. A área é desenhada no mapa (ADR-C05)."""

    TITULO = "Propriedades"
    COLUNAS = ("Nome", "Proprietário", "Cadastro público", "Área (ha)")

    def __init__(self, notebook):
        self.controller = PropriedadeRuralController()
        self.proprietarios = ProprietarioController()
        self._nomes = {}
        super().__init__(notebook)

    def criar_campos(self, form):
        self.nome = tk.StringVar()
        self.cadastro = tk.StringVar()

        ttk.Label(form, text="Nome").grid(row=0, column=0, sticky="ne", padx=4, pady=2)
        ttk.Entry(form, textvariable=self.nome).grid(row=0, column=1, sticky="new", padx=4, pady=2)

        ttk.Label(form, text="Proprietário").grid(row=1, column=0, sticky="ne", padx=4, pady=2)
        self.seletor_dono = Seletor(form, largura=30)
        self.seletor_dono.grid(row=1, column=1, sticky="new", padx=4, pady=2)

        ttk.Label(form, text="Cadastro público (opcional)").grid(
            row=2, column=0, sticky="ne", padx=4, pady=2
        )
        ttk.Entry(form, textvariable=self.cadastro).grid(row=2, column=1, sticky="new", padx=4, pady=2)

        ttk.Label(
            form, text="Área: clique no mapa para marcar os vértices.\n"
                       "As outras propriedades aparecem em cinza;\nas áreas não podem se sobrepor.",
            foreground="gray", justify="left",
        ).grid(row=3, column=1, sticky="nw", padx=4, pady=(8, 0))

        self.editor = EditorArea(form, largura=480, altura=260)
        self.editor.grid(row=0, column=2, rowspan=5, sticky="nsew", padx=(12, 0))
        form.columnconfigure(2, weight=2)
        form.rowconfigure(4, weight=1)

    def atualizar_opcoes(self):
        donos = self.proprietarios.listar()
        self._nomes = {p.id: p.nome for p in donos}
        self.seletor_dono.definir_opcoes([(p.id, f"{p.nome} (#{p.id})") for p in donos])
        self.editor.definir_vizinhas(self.controller.listar_areas(exceto_id=self.id_carregado))

    def limpar_campos(self):
        self.nome.set("")
        self.cadastro.set("")
        self.seletor_dono.selecionar(None)
        self.editor.limpar()
        self.editor.definir_vizinhas(self.controller.listar_areas())

    def preencher(self, p):
        self.nome.set(p.nome)
        self.cadastro.set(p.cadastro_publico or "")
        self.seletor_dono.selecionar(p.proprietario_id)
        self.editor.definir_vizinhas(self.controller.listar_areas(exceto_id=p.id))
        self.editor.definir_vertices(p.area.vertices if p.poligono else [])

    def valores_linha(self, p):
        area = f"{p.area_ha:.2f}" if p.poligono else "-"
        return (p.nome, self._nomes.get(p.proprietario_id, "?"), p.cadastro_publico or "-", area)

    def enviar(self, id):
        dados = (self.nome.get(), self.seletor_dono.id_selecionado(), self.cadastro.get(),
                 self.editor.vertices)
        if id is None:
            return self.controller.criar(*dados)
        return self.controller.atualizar(id, *dados)


def registrar_abas(notebook):
    PropriedadeAba(notebook)
