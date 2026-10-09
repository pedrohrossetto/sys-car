import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from controller.fiscalizacao.conformidade_controller import ConformidadeController
from controller.fiscalizacao.unidade_controller import UnidadeController
from view.fiscalizacao.componentes import (
    Seletor, ao_mostrar_aba, corrigir_cores_treeview, criar_tabela, id_selecionado,
    mostrar_resultado, preencher_tabela,
)

ORDEM = 80


class ConformidadeAba:
    def __init__(self, notebook):
        self.controller = ConformidadeController()
        self.unidades = UnidadeController()
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text="Embargos e Declarações")
        corrigir_cores_treeview(self.frame)
        self._montar_embargos()
        self._montar_declaracoes()
        self.status = ttk.Label(self.frame, text="")
        self.status.pack(fill="x")
        ao_mostrar_aba(notebook, self.frame, self.recarregar)
        self.recarregar()

    # ---------------- embargos ----------------
    def _montar_embargos(self):
        caixa = ttk.LabelFrame(self.frame, text="Embargos", padding=6)
        caixa.pack(fill="both", expand=True)
        formulario = ttk.Frame(caixa)
        formulario.pack(fill="x")
        formulario.columnconfigure((1, 3), weight=1)

        ttk.Label(formulario, text="Propriedade").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.prop_embargo = Seletor(formulario)
        self.prop_embargo.grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        # Ao escolher a propriedade, a lista de alertas confirmados é filtrada.
        self.prop_embargo.combo.bind("<<ComboboxSelected>>", lambda e: self._atualizar_alertas())

        ttk.Label(formulario, text="Alerta confirmado").grid(row=0, column=2, sticky="e", padx=4, pady=2)
        self.alerta_embargo = Seletor(formulario)
        self.alerta_embargo.grid(row=0, column=3, sticky="ew", padx=4, pady=2)

        ttk.Label(formulario, text="Unidade").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        self.unidade_embargo = Seletor(formulario)
        self.unidade_embargo.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(formulario, text="Motivo").grid(row=1, column=2, sticky="e", padx=4, pady=2)
        self.motivo = tk.StringVar()
        ttk.Entry(formulario, textvariable=self.motivo).grid(row=1, column=3, sticky="ew", padx=4, pady=2)

        botoes = ttk.Frame(caixa)
        botoes.pack(fill="x", pady=4)
        ttk.Button(botoes, text="Embargar", command=self._embargar).pack(side="left", padx=2)
        ttk.Button(botoes, text="Levantar embargo selecionado",
                   command=self._levantar).pack(side="left", padx=2)

        quadro, self.tabela_embargos = criar_tabela(
            caixa, ("ID", "Propriedade", "Unidade", "Alerta", "Data", "Motivo", "Situação"), altura=5)
        quadro.pack(fill="both", expand=True)

    def _atualizar_alertas(self):
        propriedade_id = self.prop_embargo.id_selecionado()
        registros = self.controller.registros_confirmados(propriedade_id) if propriedade_id else []
        self.alerta_embargo.definir_opcoes(
            [(r.id, f"Alerta {r.id} - {r.data} - {r.descricao[:30]}") for r in registros])

    def _embargar(self):
        _, erro = self.controller.embargar(
            self.prop_embargo.id_selecionado(), self.unidade_embargo.id_selecionado(),
            self.alerta_embargo.id_selecionado(), self.motivo.get())
        if mostrar_resultado(erro, self.status, "Propriedade embargada."):
            self.motivo.set("")
            self.recarregar()

    def _levantar(self):
        id = id_selecionado(self.tabela_embargos)
        if id is None:
            messagebox.showwarning("Aviso", "Selecione um embargo na lista.")
            return
        _, erro = self.controller.levantar_embargo(id)
        if mostrar_resultado(erro, self.status, f"Embargo {id} levantado."):
            self.recarregar()

    # ---------------- declarações ----------------
    def _montar_declaracoes(self):
        caixa = ttk.LabelFrame(self.frame, text="Declarações de conformidade", padding=6)
        caixa.pack(fill="both", expand=True, pady=(6, 0))
        linha = ttk.Frame(caixa)
        linha.pack(fill="x")
        ttk.Label(linha, text="Propriedade").pack(side="left", padx=4)
        self.prop_declaracao = Seletor(linha)
        self.prop_declaracao.combo.pack(side="left", padx=4)
        ttk.Button(linha, text="Solicitar declaração", command=self._solicitar).pack(side="left", padx=4)
        ttk.Button(linha, text="Salvar selecionada em .txt...", command=self._salvar_txt).pack(
            side="left", padx=4)
        quadro, self.tabela_declaracoes = criar_tabela(
            caixa, ("ID", "Propriedade", "Data", "Resultado", "Motivo"), altura=5)
        self.tabela_declaracoes.column("Motivo", width=320, anchor="w")
        quadro.pack(fill="both", expand=True)

    def _solicitar(self):
        declaracao, erro = self.controller.solicitar_declaracao(self.prop_declaracao.id_selecionado())
        if mostrar_resultado(erro, self.status, ""):
            if declaracao.emitida:
                self.status.config(text=f"Declaração {declaracao.id} EMITIDA.")
            else:
                self.status.config(text=f"Declaração {declaracao.id} NEGADA. {declaracao.motivo}")
            self.recarregar()

    def _salvar_txt(self):
        id = id_selecionado(self.tabela_declaracoes)
        if id is None:
            messagebox.showwarning("Aviso", "Selecione uma declaração na lista.")
            return
        texto, erro = self.controller.texto_declaracao(id)
        if not mostrar_resultado(erro):
            return
        caminho = filedialog.asksaveasfilename(
            parent=self.frame, title="Salvar declaração", defaultextension=".txt",
            initialfile=f"declaracao-{id}.txt", filetypes=[("Texto", "*.txt")])
        if caminho:
            Path(caminho).write_text(texto, encoding="utf-8")
            self.status.config(text=f"Declaração salva em {caminho}.")

    # ---------------- comum ----------------
    def recarregar(self):
        propriedades = {p.id: p.nome for p in self.controller.listar_propriedades()}
        opcoes = [(id, f"{nome} (#{id})") for id, nome in propriedades.items()]
        self.prop_embargo.definir_opcoes(opcoes)
        self.prop_declaracao.definir_opcoes(opcoes)
        unidades = self.unidades.listar()
        self.unidade_embargo.definir_opcoes([(u.id, u.nome) for u in unidades])
        self._atualizar_alertas()
        nomes_unidades = {u.id: u.nome for u in unidades}
        preencher_tabela(self.tabela_embargos, [
            (e.id, (propriedades.get(e.propriedade_id, "?"), nomes_unidades.get(e.unidade_id, "?"),
                    e.registro_id, e.data, e.motivo, "ATIVO" if e.ativo else "LEVANTADO"),
             "NEGADA" if e.ativo else None)
            for e in self.controller.listar_embargos()
        ])
        preencher_tabela(self.tabela_declaracoes, [
            (d.id, (propriedades.get(d.propriedade_id, "?"), d.data, d.resultado, d.motivo or "-"),
             d.resultado)
            for d in self.controller.listar_declaracoes()
        ])


def registrar_abas(notebook):
    ConformidadeAba(notebook)
