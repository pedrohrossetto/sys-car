import tkinter as tk
from tkinter import ttk

from controller.localizacao_controller import LocalizacaoController
from controller.propriedade_rural_controller import PropriedadeRuralController
from view.aba_crud import AbaCrud
from view.widgets import Seletor

ORDEM = 30


def _texto(valor):
    return "-" if valor is None else valor


def _campo(valor):
    return "" if valor is None else str(valor)


class LocalizacaoAba(AbaCrud):
    TITULO = "Localizações"
    COLUNAS = ("Propriedade", "Latitude", "Longitude", "Altitude", "Polígono")

    def __init__(self, notebook):
        self.controller = LocalizacaoController()
        self.propriedades = PropriedadeRuralController()
        self._nomes = {}
        super().__init__(notebook)

    def criar_campos(self, form):
        self.latitude = tk.StringVar()
        self.longitude = tk.StringVar()
        self.altitude = tk.StringVar()
        self.poligono = tk.StringVar()

        ttk.Label(form, text="Propriedade").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.seletor_propriedade = Seletor(form)
        self.seletor_propriedade.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        campos = (
            ("Latitude (-90 a 90)", self.latitude),
            ("Longitude (-180 a 180)", self.longitude),
            ("Altitude (opcional)", self.altitude),
            ("Polígono (opcional)", self.poligono),
        )
        for linha, (rotulo, variavel) in enumerate(campos, start=1):
            ttk.Label(form, text=rotulo).grid(row=linha, column=0, sticky="e", padx=4, pady=2)
            ttk.Entry(form, textvariable=variavel).grid(
                row=linha, column=1, sticky="ew", padx=4, pady=2
            )
        ttk.Label(
            form, text="Formato do polígono: lat,lon; lat,lon; lat,lon (mínimo 3 vértices)",
            foreground="gray",
        ).grid(row=5, column=1, sticky="w", padx=4)

    def atualizar_opcoes(self):
        propriedades = self.propriedades.listar()
        self._nomes = {p.id: p.nome for p in propriedades}
        self.seletor_propriedade.definir_opcoes(
            [(p.id, f"{p.nome} (#{p.id})") for p in propriedades]
        )

    def limpar_campos(self):
        for variavel in (self.latitude, self.longitude, self.altitude, self.poligono):
            variavel.set("")
        self.seletor_propriedade.selecionar(None)

    def preencher(self, l):
        self.seletor_propriedade.selecionar(l.propriedade_id)
        self.latitude.set(_campo(l.latitude))
        self.longitude.set(_campo(l.longitude))
        self.altitude.set(_campo(l.altitude))
        self.poligono.set(_campo(l.poligono_geometria))

    def valores_linha(self, l):
        return (
            self._nomes.get(l.propriedade_id, "?"), _texto(l.latitude),
            _texto(l.longitude), _texto(l.altitude), _texto(l.poligono_geometria),
        )

    def enviar(self, id):
        dados = (
            self.seletor_propriedade.id_selecionado(), self.latitude.get(),
            self.longitude.get(), self.altitude.get(), self.poligono.get(),
        )
        if id is None:
            return self.controller.criar(*dados)
        return self.controller.atualizar(id, *dados)


def registrar_abas(notebook):
    LocalizacaoAba(notebook)
