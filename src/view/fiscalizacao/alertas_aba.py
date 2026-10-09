import tkinter as tk
from tkinter import messagebox, ttk

from controller.fiscalizacao.alerta_controller import AlertaController
from controller.fiscalizacao.fonte_controller import FonteController
from controller.fiscalizacao.propriedades import nomes_das_propriedades
from view.fiscalizacao.componentes import (
    Seletor, ao_mostrar_aba, corrigir_cores_treeview, criar_tabela, id_selecionado,
    mostrar_resultado, preencher_tabela,
)

ORDEM = 60


def pedir_evidencia(parent, tipos):
    """Diálogo modal (Toplevel). Devolve (tipo, link) ou None se cancelar."""
    janela = tk.Toplevel(parent)
    janela.title("Adicionar evidência")
    janela.transient(parent.winfo_toplevel())
    janela.resizable(False, False)
    resultado = {}
    tipo = tk.StringVar(value=tipos[0])
    link = tk.StringVar()
    ttk.Label(janela, text="Tipo").grid(row=0, column=0, sticky="e", padx=6, pady=4)
    ttk.Combobox(janela, textvariable=tipo, values=tipos, state="readonly").grid(
        row=0, column=1, padx=6, pady=4)
    ttk.Label(janela, text="Link ou caminho").grid(row=1, column=0, sticky="e", padx=6, pady=4)
    entrada = ttk.Entry(janela, textvariable=link, width=40)
    entrada.grid(row=1, column=1, padx=6, pady=4)

    def confirmar(_evento=None):
        resultado["valor"] = (tipo.get(), link.get())
        janela.destroy()

    botoes = ttk.Frame(janela)
    botoes.grid(row=2, column=0, columnspan=2, pady=6)
    ttk.Button(botoes, text="OK", command=confirmar).pack(side="left", padx=4)
    ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(side="left", padx=4)
    janela.bind("<Return>", confirmar)
    janela.bind("<Escape>", lambda e: janela.destroy())
    entrada.focus_set()
    janela.grab_set()
    parent.wait_window(janela)
    return resultado.get("valor")


class AlertasAba:
    def __init__(self, notebook):
        self.alertas = AlertaController()
        self.fontes = FonteController()
        self.evidencias_novas = []
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
        self.status = ttk.Label(self.frame, text="")
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
            caixa, ("ID", "Propriedade", "Origem", "Status", "Data"), altura=10)
        quadro.pack(fill="both", expand=True)
        ttk.Label(caixa, text="Botão direito em um alerta: mudar o status.",
                  foreground="gray").pack(anchor="w")
        self.tabela.bind("<<TreeviewSelect>>", lambda e: self._mostrar_detalhe())
        self.tabela.bind("<Button-3>", self._abrir_menu_status)
        self.tabela.bind("<Button-2>", self._abrir_menu_status)  # botão direito no macOS

        detalhe = ttk.LabelFrame(parent, text="Alerta selecionado", padding=6)
        detalhe.pack(fill="x", pady=(6, 0))
        self.texto_detalhe = ttk.Label(detalhe, text="Nenhum alerta selecionado.", wraplength=420)
        self.texto_detalhe.pack(anchor="w")
        self.lista_evidencias = tk.Listbox(detalhe, height=4)
        self.lista_evidencias.pack(fill="x", pady=4)
        ttk.Button(detalhe, text="Adicionar evidência ao alerta...",
                   command=self._evidencia_no_selecionado).pack(anchor="w")

    def recarregar(self):
        nomes = nomes_das_propriedades()
        registros = self.alertas.listar(incluir_finalizados=self.mostrar_finalizados.get())
        preencher_tabela(self.tabela, [
            (r.id, (nomes.get(r.propriedade_id, "?"), self.alertas.descrever_origem(r),
                    r.status, r.data), r.status)
            for r in registros
        ])
        self._atualizar_opcoes()
        self._mostrar_detalhe()

    def _mostrar_detalhe(self):
        self.lista_evidencias.delete(0, "end")
        id = id_selecionado(self.tabela)
        registro = self.alertas.buscar_por_id(id) if id is not None else None
        if registro is None:
            self.texto_detalhe.config(text="Nenhum alerta selecionado.")
            return
        self.texto_detalhe.config(
            text=f"Alerta {registro.id} - {registro.status} - "
                 f"({registro.latitude}, {registro.longitude})\n{registro.descricao}")
        for evidencia in self.alertas.evidencias_de(registro.id):
            self.lista_evidencias.insert("end", f"{evidencia.tipo}: {evidencia.link}")

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

    def _evidencia_no_selecionado(self):
        id = id_selecionado(self.tabela)
        if id is None:
            messagebox.showwarning("Aviso", "Selecione um alerta na lista.")
            return
        valor = pedir_evidencia(self.frame, self.alertas.tipos_evidencia())
        if valor is None:
            return
        _, erro = self.alertas.adicionar_evidencia(id, *valor)
        if mostrar_resultado(erro, self.status, "Evidência adicionada."):
            self._mostrar_detalhe()

    # ---------------- novo alerta ----------------
    def _montar_formulario(self, parent):
        caixa = ttk.LabelFrame(parent, text="Novo alerta", padding=6)
        caixa.pack(fill="both", expand=True)
        caixa.columnconfigure(1, weight=1)

        self.origem = tk.StringVar(value="satelite")
        origens = ttk.Frame(caixa)
        origens.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(origens, text="Origem:").pack(side="left")
        for valor, rotulo in (("satelite", "Satélite"), ("usuario", "Usuário")):
            ttk.Radiobutton(origens, text=rotulo, value=valor, variable=self.origem,
                            command=self._trocar_origem).pack(side="left", padx=4)

        self.rotulo_fonte = ttk.Label(caixa, text="Satélite")
        self.rotulo_fonte.grid(row=1, column=0, sticky="e", padx=4, pady=2)
        self.seletor_fonte = Seletor(caixa)
        self.seletor_fonte.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(caixa, text="Propriedade").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        self.seletor_propriedade = Seletor(caixa)
        self.seletor_propriedade.grid(row=2, column=1, sticky="ew", padx=4, pady=2)

        self.latitude = tk.StringVar()
        self.longitude = tk.StringVar()
        for linha, (rotulo, variavel) in enumerate(
                (("Latitude", self.latitude), ("Longitude", self.longitude)), start=3):
            ttk.Label(caixa, text=rotulo).grid(row=linha, column=0, sticky="e", padx=4, pady=2)
            ttk.Entry(caixa, textvariable=variavel).grid(row=linha, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(caixa, text="Descrição").grid(row=5, column=0, sticky="ne", padx=4, pady=2)
        self.descricao = tk.Text(caixa, height=4, width=30, wrap="word")
        self.descricao.grid(row=5, column=1, sticky="ew", padx=4, pady=2)

        self.rotulo_evidencias = ttk.Label(caixa, text="Evidências (opcional)")
        self.rotulo_evidencias.grid(row=6, column=0, sticky="ne", padx=4, pady=2)
        self.lista_novas = tk.Listbox(caixa, height=3)
        self.lista_novas.grid(row=6, column=1, sticky="ew", padx=4, pady=2)
        botoes_ev = ttk.Frame(caixa)
        botoes_ev.grid(row=7, column=1, sticky="w")
        ttk.Button(botoes_ev, text="Adicionar...", command=self._adicionar_nova_evidencia).pack(side="left")
        ttk.Button(botoes_ev, text="Remover", command=self._remover_nova_evidencia).pack(side="left", padx=4)

        ttk.Button(caixa, text="Registrar alerta", command=self._registrar).grid(
            row=8, column=0, columnspan=2, pady=8)

    def _atualizar_opcoes(self):
        self.seletor_propriedade.definir_opcoes(
            [(id, f"{nome} (#{id})") for id, nome in nomes_das_propriedades().items()])
        self._trocar_origem()

    def _trocar_origem(self):
        """Evento do Radiobutton: troca a lista de fontes e a regra de evidência."""
        if self.origem.get() == "satelite":
            self.rotulo_fonte.config(text="Satélite")
            self.rotulo_evidencias.config(text="Evidências (opcional)")
            fontes = [(s.id, s.nome) for s in self.fontes.listar_satelites()]
        else:
            self.rotulo_fonte.config(text="Usuário")
            self.rotulo_evidencias.config(text="Evidências (mínimo 1)")
            fontes = [(u.id, u.nome) for u in self.fontes.listar_usuarios()]
        self.seletor_fonte.definir_opcoes(fontes)

    def _adicionar_nova_evidencia(self):
        valor = pedir_evidencia(self.frame, self.alertas.tipos_evidencia())
        if valor and valor[1].strip():
            self.evidencias_novas.append(valor)
            self.lista_novas.insert("end", f"{valor[0]}: {valor[1]}")

    def _remover_nova_evidencia(self):
        for indice in reversed(self.lista_novas.curselection()):
            self.lista_novas.delete(indice)
            del self.evidencias_novas[indice]

    def _registrar(self):
        dados = dict(
            propriedade_id=self.seletor_propriedade.id_selecionado(),
            descricao=self.descricao.get("1.0", "end").strip(),
            latitude=self.latitude.get(),
            longitude=self.longitude.get(),
        )
        fonte_id = self.seletor_fonte.id_selecionado()
        if self.origem.get() == "satelite":
            registro, erro = self.alertas.registrar_por_satelite(fonte_id, **dados)
        else:
            registro, erro = self.alertas.registrar_por_usuario(
                fonte_id, evidencias=list(self.evidencias_novas), **dados)
        if mostrar_resultado(erro, self.status, f"Alerta {registro.id if registro else ''} registrado."):
            self.latitude.set("")
            self.longitude.set("")
            self.descricao.delete("1.0", "end")
            self.evidencias_novas.clear()
            self.lista_novas.delete(0, "end")
            self.recarregar()


def registrar_abas(notebook):
    AlertasAba(notebook)
