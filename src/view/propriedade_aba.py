import tkinter as tk
from tkinter import ttk

from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.proprietario_controller import ProprietarioController
from view.aba_crud import AbaCrud
from view.widgets import Seletor

ORDEM = 20


class PropriedadeAba(AbaCrud):
    TITULO = "Propriedades"
    COLUNAS = ("Nome", "Proprietário", "Cadastro público")

    def __init__(self, notebook):
        self.controller = PropriedadeRuralController()
        self.proprietarios = ProprietarioController()
        self._nomes = {}
        super().__init__(notebook)

    def criar_campos(self, form):
        self.nome = tk.StringVar()
        self.cadastro = tk.StringVar()

        ttk.Label(form, text="Nome").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(form, textvariable=self.nome).grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Proprietário").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        self.seletor_dono = Seletor(form)
        self.seletor_dono.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Cadastro público (opcional)").grid(
            row=2, column=0, sticky="e", padx=4, pady=2
        )
        ttk.Entry(form, textvariable=self.cadastro).grid(row=2, column=1, sticky="ew", padx=4, pady=2)

    def atualizar_opcoes(self):
        donos = self.proprietarios.listar()
        self._nomes = {p.id: p.nome for p in donos}
        self.seletor_dono.definir_opcoes([(p.id, f"{p.nome} (#{p.id})") for p in donos])

    def limpar_campos(self):
        self.nome.set("")
        self.cadastro.set("")
        self.seletor_dono.selecionar(None)

    def preencher(self, p):
        self.nome.set(p.nome)
        self.cadastro.set(p.cadastro_publico or "")
        self.seletor_dono.selecionar(p.proprietario_id)

    def valores_linha(self, p):
        return (p.nome, self._nomes.get(p.proprietario_id, "?"), p.cadastro_publico or "-")

    def enviar(self, id):
        dados = (self.nome.get(), self.seletor_dono.id_selecionado(), self.cadastro.get())
        if id is None:
            return self.controller.criar(*dados)
        return self.controller.atualizar(id, *dados)


def registrar_abas(notebook):
    PropriedadeAba(notebook)
