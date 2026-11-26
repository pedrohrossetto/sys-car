"""Aba "Ficha da Propriedade": os dados relacionados de uma propriedade (aula 11)."""
import tkinter as tk
from tkinter import ttk

from controller.fiscalizacao.ficha_controller import COM_ALERTAS, EMBARGADA, FichaController
from view.fiscalizacao.componentes import (
    Seletor, ao_mostrar_aba, corrigir_cores_treeview, criar_tabela, mostrar_resultado,
    preencher_tabela,
)
from view.mapa import MapaCanvas
from view.proprietario_aba import formatar_documento

ORDEM = 90

CORES_SITUACAO = {EMBARGADA: "#b00020", COM_ALERTAS: "#9a6700"}
COR_REGULAR = "#1b7f3b"


class FichaAba:
    def __init__(self, notebook):
        self.controller = FichaController()
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text="Ficha da Propriedade")
        corrigir_cores_treeview(self.frame)
        self._montar_escolha()
        self._montar_resumo()
        self._montar_tabelas()
        self.status = ttk.Label(self.frame, text="Escolha uma propriedade.")
        self.status.pack(fill="x")
        ao_mostrar_aba(notebook, self.frame, self.recarregar)
        self.recarregar()

    # ---------------- montagem ----------------
    def _montar_escolha(self):
        topo = ttk.Frame(self.frame)
        topo.pack(fill="x", pady=(0, 6))
        ttk.Label(topo, text="Propriedade").grid(row=0, column=0, sticky="e", padx=4)
        self.propriedade = Seletor(topo, largura=40)
        self.propriedade.grid(row=0, column=1, sticky="w", padx=4)
        self.propriedade.combo.bind("<<ComboboxSelected>>", lambda e: self.mostrar())
        ttk.Label(topo, text="Situação:").grid(row=0, column=2, sticky="e", padx=(16, 4))
        self.situacao = ttk.Label(topo, text="-", font=("TkDefaultFont", 10, "bold"))
        self.situacao.grid(row=0, column=3, sticky="w")

    def _caixa_de_campos(self, parent, titulo, rotulos, coluna):
        """LabelFrame com pares rótulo/valor. Devolve dict rótulo -> StringVar."""
        caixa = ttk.LabelFrame(parent, text=titulo, padding=6)
        caixa.grid(row=0, column=coluna, sticky="nsew", padx=3)
        valores = {}
        for linha, rotulo in enumerate(rotulos):
            ttk.Label(caixa, text=f"{rotulo}:").grid(row=linha, column=0, sticky="ne", padx=2)
            valores[rotulo] = tk.StringVar(value="-")
            ttk.Label(caixa, textvariable=valores[rotulo], wraplength=220).grid(
                row=linha, column=1, sticky="nw", padx=2)
        return valores

    def _montar_resumo(self):
        resumo = ttk.Frame(self.frame)
        resumo.pack(fill="x")
        resumo.columnconfigure((0, 1, 2, 3), weight=1, uniform="caixa")
        self.campos_propriedade = self._caixa_de_campos(
            resumo, "Propriedade", ("Nome", "Cadastro público"), 0)
        self.campos_proprietario = self._caixa_de_campos(
            resumo, "Proprietário", ("Nome", "Tipo", "Documento"), 1)
        self.campos_area = self._caixa_de_campos(
            resumo, "Área", ("Centro (lat, lon)", "Área", "Vértices"), 2)
        self.campos_embargo = self._caixa_de_campos(
            resumo, "Embargo ativo", ("Unidade", "Data", "Motivo"), 3)

    def _montar_tabelas(self):
        baixo = ttk.PanedWindow(self.frame, orient="horizontal")
        baixo.pack(fill="both", expand=True, pady=6)
        tabelas = ttk.PanedWindow(baixo, orient="vertical")
        baixo.add(tabelas, weight=3)

        # Mapa só de leitura: a área da propriedade em verde, as vizinhas em cinza e os alertas dela.
        caixa_mapa = ttk.LabelFrame(baixo, text="Mapa", padding=4)
        self.mapa = MapaCanvas(caixa_mapa, largura=380, altura=260)
        self.mapa.pack(fill="both", expand=True)
        baixo.add(caixa_mapa, weight=2)

        caixa_alertas = ttk.LabelFrame(tabelas, text="Alertas", padding=6)
        quadro, self.tabela_alertas = criar_tabela(
            caixa_alertas, ("ID", "Data", "Status", "Descrição"), altura=5)
        self.tabela_alertas.column("Descrição", width=260, anchor="w")
        quadro.pack(fill="both", expand=True)
        tabelas.add(caixa_alertas, weight=1)

        caixa_declaracoes = ttk.LabelFrame(tabelas, text="Declarações de conformidade", padding=6)
        quadro, self.tabela_declaracoes = criar_tabela(
            caixa_declaracoes, ("ID", "Data", "Resultado", "Motivo"), altura=4)
        self.tabela_declaracoes.column("Motivo", width=320, anchor="w")
        quadro.pack(fill="both", expand=True)
        tabelas.add(caixa_declaracoes, weight=1)

    # ---------------- dados ----------------
    def recarregar(self):
        """Atualiza a lista de propriedades e a ficha aberta (ao mostrar a aba)."""
        self.propriedade.definir_opcoes(
            [(p.id, f"{p.nome} (#{p.id})") for p in self.controller.listar_propriedades()])
        self.mostrar()

    def mostrar(self):
        propriedade_id = self.propriedade.id_selecionado()
        if propriedade_id is None:
            self._limpar()
            return
        ficha, erro = self.controller.montar(propriedade_id)
        if not mostrar_resultado(erro, self.status):
            self._limpar()
            return
        self._preencher(ficha)
        self.status.config(
            text=f"{len(ficha.alertas)} alerta(s), {len(ficha.declaracoes)} declaração(ões).")

    def _preencher(self, ficha):
        p = ficha.propriedade
        self._definir(self.campos_propriedade, {
            "Nome": p.nome, "Cadastro público": getattr(p, "cadastro_publico", None)})

        dono = ficha.proprietario
        self._definir(self.campos_proprietario, {
            "Nome": dono.nome if dono else "não encontrado",
            "Tipo": dono.tipo if dono else None,
            "Documento": formatar_documento(dono) if dono else None,
        })

        centro = p.centroide
        self._definir(self.campos_area, {
            "Centro (lat, lon)": f"{centro[0]:.5f}, {centro[1]:.5f}" if centro else "sem área",
            "Área": f"{p.area_ha:.2f} ha" if p.poligono else None,
            "Vértices": len(p.area) if p.poligono else None,
        })

        embargo = ficha.embargo_ativo
        self._definir(self.campos_embargo, {
            "Unidade": ficha.unidade_do_embargo.nome if ficha.unidade_do_embargo else
                       ("nenhum" if embargo is None else embargo.unidade_id),
            "Data": embargo.data if embargo else None,
            "Motivo": embargo.motivo if embargo else None,
        })

        self.situacao.config(
            text=ficha.situacao, foreground=CORES_SITUACAO.get(ficha.situacao, COR_REGULAR))
        preencher_tabela(self.tabela_alertas, [
            (a.id, (a.data, a.status, a.descricao), a.status)
            for a in ficha.alertas
        ])
        self.mapa.definir_areas(self.controller.listar_areas(), destaque_id=p.id)
        self.mapa.definir_pontos([(a.latitude, a.longitude, a.status, f"#{a.id}") for a in ficha.alertas])
        self.mapa.enquadrar(p.area.vertices if p.poligono else
                            [(a.latitude, a.longitude) for a in ficha.alertas])
        preencher_tabela(self.tabela_declaracoes, [
            (d.id, (d.data, d.resultado, d.motivo or "-"), d.resultado)
            for d in ficha.declaracoes
        ])

    @staticmethod
    def _definir(campos, valores):
        for rotulo, valor in valores.items():
            campos[rotulo].set("-" if valor in (None, "") else str(valor))

    def _limpar(self):
        for campos in (self.campos_propriedade, self.campos_proprietario,
                       self.campos_area, self.campos_embargo):
            for variavel in campos.values():
                variavel.set("-")
        self.situacao.config(text="-", foreground="")
        preencher_tabela(self.tabela_alertas, [])
        preencher_tabela(self.tabela_declaracoes, [])
        self.mapa.definir_areas(self.controller.listar_areas())
        self.mapa.definir_pontos([])


def registrar_abas(notebook):
    FichaAba(notebook)
