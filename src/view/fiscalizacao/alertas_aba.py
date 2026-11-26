import tkinter as tk
from tkinter import messagebox, ttk

from controller.fiscalizacao.alerta_controller import AlertaController
from view.fiscalizacao.componentes import (
    ao_mostrar_aba, corrigir_cores_treeview, criar_tabela, id_selecionado,
    mostrar_resultado, preencher_tabela,
)
from view.mapa import MapaCanvas

ORDEM = 60


class AlertasAba:
    """CRUD dos alertas de desmatamento (ADR-F12 e ADR-F14).

    Novo alerta: clique no mapa. A propriedade é a que contém o ponto.
    Duplo clique ou Enter na lista carrega o alerta no formulário; o ponto
    dele não muda. O status muda só pelo menu do botão direito (State).
    """

    def __init__(self, notebook):
        self.alertas = AlertaController()
        self.id_carregado = None
        self.ponto_novo = None
        self._primeira_vez = True
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text="Alertas")
        corrigir_cores_treeview(self.frame)

        painel = ttk.PanedWindow(self.frame, orient="horizontal")
        painel.pack(fill="both", expand=True)
        esquerda = ttk.PanedWindow(painel, orient="vertical")
        direita = ttk.Frame(painel)
        painel.add(esquerda, weight=3)
        painel.add(direita, weight=2)

        self._montar_mapa(esquerda)
        self._montar_lista(esquerda)
        self._montar_formulario(direita)
        self._montar_detalhe(direita)
        self.status = ttk.Label(self.frame, text="Clique no mapa para marcar um novo alerta.")
        self.status.pack(fill="x")

        ao_mostrar_aba(notebook, self.frame, self.recarregar)
        self.recarregar()

    # ---------------- mapa ----------------
    def _montar_mapa(self, parent):
        caixa = ttk.LabelFrame(parent, text="Mapa", padding=4)
        self.mapa = MapaCanvas(caixa, largura=560, altura=300, ao_clicar=self._ao_clicar_mapa)
        self.mapa.pack(fill="both", expand=True)
        parent.add(caixa, weight=3)

    def _ao_clicar_mapa(self, lat, lon):
        self.ponto_novo = (round(lat, 6), round(lon, 6))
        propriedade = self.alertas.propriedade_no_ponto(*self.ponto_novo)
        self._mostrar_local(propriedade.nome if propriedade else "fora de propriedade cadastrada")
        self._desenhar_pontos()

    def _desenhar_pontos(self):
        pontos = [(r.latitude, r.longitude, r.status, f"#{r.id}") for r in self._registros]
        if self.ponto_novo and self.id_carregado is None:
            pontos.append((*self.ponto_novo, "NOVO", "novo"))
        self.mapa.definir_pontos(pontos)

    # ---------------- lista de alertas ----------------
    def _montar_lista(self, parent):
        caixa = ttk.LabelFrame(parent, text="Alertas", padding=6)
        self.mostrar_finalizados = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            caixa, text="Mostrar finalizados (resolvidos e cancelados)",
            variable=self.mostrar_finalizados, command=self.recarregar,
        ).pack(anchor="w")
        quadro, self.tabela = criar_tabela(caixa, ("ID", "Local", "Status", "Data"), altura=6)
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
        parent.add(caixa, weight=2)

    def recarregar(self):
        self._registros = self.alertas.listar(incluir_finalizados=self.mostrar_finalizados.get())
        preencher_tabela(self.tabela, [
            (r.id, (self.alertas.descrever_local(r), r.status, r.data), r.status)
            for r in self._registros
        ])
        self.mapa.definir_areas(self.alertas.listar_areas())
        self._desenhar_pontos()
        if self._primeira_vez:
            self._primeira_vez = False
            self.mapa.enquadrar_tudo()
        self._mostrar_detalhe()

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

        ttk.Label(caixa, text="Ponto").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.texto_ponto = ttk.Label(caixa, text="clique no mapa")
        self.texto_ponto.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(caixa, text="Propriedade").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        self.texto_local = ttk.Label(caixa, text="-")
        self.texto_local.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self.data = tk.StringVar()
        ttk.Label(caixa, text="Data (AAAA-MM-DD)").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        entrada = ttk.Entry(caixa, textvariable=self.data)
        entrada.grid(row=2, column=1, sticky="ew", padx=4, pady=2)
        entrada.bind("<Return>", lambda e: self._salvar())
        entrada.bind("<Escape>", lambda e: self._limpar())
        ttk.Label(caixa, text="Data vazia = hoje.", foreground="gray").grid(
            row=3, column=1, sticky="w", padx=4)

        ttk.Label(caixa, text="Descrição").grid(row=4, column=0, sticky="ne", padx=4, pady=2)
        self.descricao = tk.Text(caixa, height=4, width=30, wrap="word")
        self.descricao.grid(row=4, column=1, sticky="ew", padx=4, pady=2)
        self.descricao.bind("<Escape>", lambda e: self._limpar())

        botoes = ttk.Frame(caixa)
        botoes.grid(row=5, column=0, columnspan=2, pady=8)
        ttk.Button(botoes, text="Salvar (Enter)", command=self._salvar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir (Delete)", command=self._excluir).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar (Esc)", command=self._limpar).pack(side="left", padx=4)

    def _montar_detalhe(self, parent):
        detalhe = ttk.LabelFrame(parent, text="Alerta selecionado", padding=6)
        detalhe.pack(fill="x", pady=(6, 0))
        self.texto_detalhe = ttk.Label(detalhe, text="Nenhum alerta selecionado.", wraplength=360)
        self.texto_detalhe.pack(anchor="w")

    def _mostrar_detalhe(self):
        id = id_selecionado(self.tabela)
        registro = self.alertas.buscar_por_id(id) if id is not None else None
        if registro is None:
            self.texto_detalhe.config(text="Nenhum alerta selecionado.")
            return
        self.texto_detalhe.config(
            text=f"Alerta {registro.id} - {registro.status} - {self.alertas.descrever_local(registro)}\n"
                 f"({registro.latitude:.5f}, {registro.longitude:.5f})\n{registro.descricao}")

    def _mostrar_ponto(self, lat, lon):
        self.texto_ponto.config(text=f"{lat:.5f}, {lon:.5f}")

    def _mostrar_local(self, texto):
        self.texto_local.config(text=texto)
        if self.ponto_novo:
            self._mostrar_ponto(*self.ponto_novo)

    def _carregar_selecionado(self):
        id = id_selecionado(self.tabela)
        registro = self.alertas.buscar_por_id(id) if id is not None else None
        if registro is None:
            return
        self.id_carregado = registro.id
        self.ponto_novo = None
        # O ponto (e a propriedade que vem dele) não muda depois de criado (ADR-F14).
        self.mapa.clique_ativo = False
        self._mostrar_ponto(registro.latitude, registro.longitude)
        self.texto_local.config(text=self.alertas.descrever_local(registro))
        self.data.set(registro.data)
        self.descricao.delete("1.0", "end")
        self.descricao.insert("1.0", registro.descricao)
        self._desenhar_pontos()
        self.mapa.enquadrar([(registro.latitude, registro.longitude)])
        self.caixa_form.config(text=f"Editando o alerta {registro.id} (ponto fixo)")
        self.status.config(text=f"Editando o alerta {registro.id}. Enter salva, Esc cancela.")

    def _salvar(self):
        descricao = self.descricao.get("1.0", "end").strip()
        if self.id_carregado is not None:
            registro, erro = self.alertas.atualizar(self.id_carregado, descricao, self.data.get())
        elif self.ponto_novo is None:
            registro, erro = None, "Clique no mapa para marcar o ponto do alerta."
        else:
            registro, erro = self.alertas.criar(descricao, *self.ponto_novo, data=self.data.get())
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
        self.ponto_novo = None
        self.mapa.clique_ativo = True
        self.texto_ponto.config(text="clique no mapa")
        self.texto_local.config(text="-")
        self.data.set("")
        self.descricao.delete("1.0", "end")
        self.tabela.selection_remove(*self.tabela.selection())
        self.caixa_form.config(text="Novo alerta")
        self._desenhar_pontos()
        if not manter_status:
            self.status.config(text="Clique no mapa para marcar um novo alerta.")


def registrar_abas(notebook):
    AlertasAba(notebook)
