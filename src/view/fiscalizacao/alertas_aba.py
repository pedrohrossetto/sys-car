import tkinter as tk
from tkinter import messagebox, ttk

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.propriedades import nomes_das_propriedades
from view.fiscalizacao.componentes import (
    Seletor, ao_mostrar_aba, corrigir_cores_treeview, criar_tabela, id_selecionado,
    mostrar_resultado, preencher_tabela,
)

ORDEM = 60


class AlertasAba:
    """CRUD dos alertas de desmatamento (ADR-F12).

    Duplo clique ou Enter na lista carrega o alerta no formulário.
    O status muda só pelo menu do botão direito (State).
    """

    def __init__(self, notebook):
        self.alertas = AlertaController()
        self.id_carregado = None
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text="Alertas")
        corrigir_cores_treeview(self.frame)

        painel = ttk.PanedWindow(self.frame, orient="horizontal")
        painel.pack(fill="both", expand=True)
        esquerda = ttk.Frame(painel)
        direita = ttk.Frame(painel)
        painel.add(esquerda, weight=3)
        painel.add(direita, weight=2)

        self._montar_lista(esquerda)
        self._montar_formulario(direita)
        self.status = ttk.Label(self.frame, text="Novo alerta.")
        self.status.pack(fill="x")

        ao_mostrar_aba(notebook, self.frame, self.recarregar)
        self.recarregar()

    # ---------------- lista de alertas ----------------
    def _montar_lista(self, parent):
        caixa = ttk.LabelFrame(parent, text="Alertas", padding=6)
        caixa.pack(fill="both", expand=True)
        self.mostrar_finalizados = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            caixa, text="Mostrar finalizados (resolvidos e cancelados)",
            variable=self.mostrar_finalizados, command=self.recarregar,
        ).pack(anchor="w")
        quadro, self.tabela = criar_tabela(
            caixa, ("ID", "Propriedade", "Status", "Data"), altura=10)
        quadro.pack(fill="both", expand=True)
        ttk.Label(caixa, text="Duplo clique: editar. Delete: excluir. Botão direito: mudar o status.",
                  foreground="gray").pack(anchor="w")
        self.tabela.bind("<<TreeviewSelect>>", lambda e: self._mostrar_detalhe())
        self.tabela.bind("<Double-1>", lambda e: self._carregar_selecionado())
        self.tabela.bind("<Return>", lambda e: self._carregar_selecionado())
        self.tabela.bind("<Delete>", lambda e: self._excluir())
        self.tabela.bind("<Escape>", lambda e: self._limpar())
        self.tabela.bind("<Button-3>", self._abrir_menu_status)
        self.tabela.bind("<Button-2>", self._abrir_menu_status)  # botão direito no macOS

        detalhe = ttk.LabelFrame(parent, text="Alerta selecionado", padding=6)
        detalhe.pack(fill="x", pady=(6, 0))
        self.texto_detalhe = ttk.Label(detalhe, text="Nenhum alerta selecionado.", wraplength=420)
        self.texto_detalhe.pack(anchor="w")

    def recarregar(self):
        nomes = nomes_das_propriedades()
        registros = self.alertas.listar(incluir_finalizados=self.mostrar_finalizados.get())
        preencher_tabela(self.tabela, [
            (r.id, (nomes.get(r.propriedade_id, "?"), r.status, r.data), r.status)
            for r in registros
        ])
        self.seletor_propriedade.definir_opcoes(
            [(id, f"{nome} (#{id})") for id, nome in nomes.items()])
        self._mostrar_detalhe()

    def _mostrar_detalhe(self):
        id = id_selecionado(self.tabela)
        registro = self.alertas.buscar_por_id(id) if id is not None else None
        if registro is None:
            self.texto_detalhe.config(text="Nenhum alerta selecionado.")
            return
        self.texto_detalhe.config(
            text=f"Alerta {registro.id} - {registro.status} - "
                 f"({registro.latitude}, {registro.longitude})\n{registro.descricao}")

    def _abrir_menu_status(self, evento):
        """Menu de contexto com as transições permitidas pelo estado atual (State)."""
        linha = self.tabela.identify_row(evento.y)
        if not linha:
            return
        self.tabela.selection_set(linha)
        menu = tk.Menu(self.tabela, tearoff=False)
        transicoes = self.alertas.transicoes_possiveis(int(linha))
        for status in transicoes:
            menu.add_command(label=f"Mudar para {status}",
                             command=lambda s=status: self._mudar_status(int(linha), s))
        if not transicoes:
            menu.add_command(label="Alerta finalizado", state="disabled")
        menu.tk_popup(evento.x_root, evento.y_root)

    def _mudar_status(self, registro_id, status):
        _, erro = self.alertas.mudar_status(registro_id, status)
        if mostrar_resultado(erro, self.status, f"Alerta {registro_id} agora está {status}."):
            self.recarregar()

    # ---------------- formulário (CRUD) ----------------
    def _montar_formulario(self, parent):
        self.caixa_form = ttk.LabelFrame(parent, text="Novo alerta", padding=6)
        self.caixa_form.pack(fill="both", expand=True)
        caixa = self.caixa_form
        caixa.columnconfigure(1, weight=1)

        ttk.Label(caixa, text="Propriedade").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.seletor_propriedade = Seletor(caixa)
        self.seletor_propriedade.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        self.data = tk.StringVar()
        self.latitude = tk.StringVar()
        self.longitude = tk.StringVar()
        campos = (("Data (AAAA-MM-DD)", self.data), ("Latitude", self.latitude),
                  ("Longitude", self.longitude))
        for linha, (rotulo, variavel) in enumerate(campos, start=1):
            ttk.Label(caixa, text=rotulo).grid(row=linha, column=0, sticky="e", padx=4, pady=2)
            entrada = ttk.Entry(caixa, textvariable=variavel)
            entrada.grid(row=linha, column=1, sticky="ew", padx=4, pady=2)
            entrada.bind("<Return>", lambda e: self._salvar())
            entrada.bind("<Escape>", lambda e: self._limpar())
        ttk.Label(caixa, text="Data vazia = hoje.", foreground="gray").grid(
            row=4, column=1, sticky="w", padx=4)

        ttk.Label(caixa, text="Descrição").grid(row=5, column=0, sticky="ne", padx=4, pady=2)
        self.descricao = tk.Text(caixa, height=4, width=30, wrap="word")
        self.descricao.grid(row=5, column=1, sticky="ew", padx=4, pady=2)
        self.descricao.bind("<Escape>", lambda e: self._limpar())

        botoes = ttk.Frame(caixa)
        botoes.grid(row=6, column=0, columnspan=2, pady=8)
        ttk.Button(botoes, text="Salvar (Enter)", command=self._salvar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir (Delete)", command=self._excluir).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar (Esc)", command=self._limpar).pack(side="left", padx=4)

    def _carregar_selecionado(self):
        id = id_selecionado(self.tabela)
        registro = self.alertas.buscar_por_id(id) if id is not None else None
        if registro is None:
            return
        self.id_carregado = registro.id
        self.seletor_propriedade.selecionar(registro.propriedade_id)
        # A propriedade de um alerta não muda (os embargos apontam para ele).
        self.seletor_propriedade.combo.config(state="disabled")
        self.data.set(registro.data)
        self.latitude.set(registro.latitude)
        self.longitude.set(registro.longitude)
        self.descricao.delete("1.0", "end")
        self.descricao.insert("1.0", registro.descricao)
        self.caixa_form.config(text=f"Editando o alerta {registro.id}")
        self.status.config(text=f"Editando o alerta {registro.id}. Enter salva, Esc cancela.")

    def _salvar(self):
        dados = dict(
            descricao=self.descricao.get("1.0", "end").strip(),
            latitude=self.latitude.get(),
            longitude=self.longitude.get(),
            data=self.data.get(),
        )
        if self.id_carregado is None:
            registro, erro = self.alertas.criar(self.seletor_propriedade.id_selecionado(), **dados)
        else:
            registro, erro = self.alertas.atualizar(self.id_carregado, **dados)
        if mostrar_resultado(erro, self.status, f"Alerta {registro.id if registro else ''} salvo."):
            self._limpar(manter_status=True)
            self.recarregar()

    def _excluir(self):
        id = id_selecionado(self.tabela)
        id = id if id is not None else self.id_carregado
        if id is None:
            messagebox.showwarning("Aviso", "Selecione um alerta na lista.")
            return
        if not messagebox.askyesno(
                "Confirmar",
                f"Excluir o alerta {id}?\n\nAs notificações e os embargos ligados a este "
                "alerta também serão apagados."):
            return
        _, erro = self.alertas.excluir(id)
        if mostrar_resultado(erro, self.status, f"Alerta {id} excluído."):
            self._limpar(manter_status=True)
            self.recarregar()

    def _limpar(self, manter_status=False):
        self.id_carregado = None
        self.seletor_propriedade.combo.config(state="readonly")
        for variavel in (self.data, self.latitude, self.longitude):
            variavel.set("")
        self.descricao.delete("1.0", "end")
        self.tabela.selection_remove(*self.tabela.selection())
        self.caixa_form.config(text="Novo alerta")
        if not manter_status:
            self.status.config(text="Novo alerta.")


def registrar_abas(notebook):
    AlertasAba(notebook)
