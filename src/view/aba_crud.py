from tkinter import messagebox, ttk

from view.widgets import criar_tabela


class AbaCrud:
    """Aba genérica de cadastro (padrão Template Method na view).

    Esta classe monta a estrutura fixa (formulário, botões, tabela,
    barra de status, atalhos) e implementa o fluxo salvar/excluir/
    carregar/limpar. As subclasses preenchem só os ganchos:
      - criar_campos(form), limpar_campos(), preencher(objeto);
      - valores_linha(objeto) -> tupla mostrada na tabela (sem o ID);
      - enviar(id) -> (resultado, erro): cria se id for None, senão atualiza;
      - atualizar_opcoes(): recarrega Comboboxes (opcional).
    A subclasse define self.controller ANTES de chamar super().__init__().
    """

    TITULO = ""
    COLUNAS = ()

    def __init__(self, notebook):
        self.notebook = notebook
        self.id_carregado = None
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text=self.TITULO)

        self.form = ttk.LabelFrame(self.frame, text="Dados", padding=8)
        self.form.pack(fill="x")
        self.form.columnconfigure(1, weight=1)
        self.criar_campos(self.form)

        botoes = ttk.Frame(self.frame)
        botoes.pack(fill="x", pady=6)
        ttk.Button(botoes, text="Salvar (Enter)", command=self.salvar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir (Delete)", command=self.excluir).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar (Esc)", command=self.limpar).pack(side="left", padx=4)

        quadro, self.tabela = criar_tabela(self.frame, ("ID",) + tuple(self.COLUNAS))
        quadro.pack(fill="both", expand=True)

        self.status = ttk.Label(self.frame, text="Novo registro.")
        self.status.pack(fill="x", pady=(4, 0))

        self._ligar_eventos()
        self.recarregar()

    # ---------------- ganchos ----------------
    def criar_campos(self, form):
        raise NotImplementedError

    def limpar_campos(self):
        raise NotImplementedError

    def preencher(self, objeto):
        raise NotImplementedError

    def valores_linha(self, objeto):
        raise NotImplementedError

    def enviar(self, id):
        raise NotImplementedError

    def atualizar_opcoes(self):
        pass

    # ---------------- fluxo fixo ----------------
    def recarregar(self):
        self.atualizar_opcoes()
        self.tabela.delete(*self.tabela.get_children())
        for objeto in self.controller.listar():
            # iid = id do banco. O formulário é recarregado pelo controller
            # a partir desse id, nunca pelos valores exibidos na tabela
            # (o ttk converte "01234567890" em 1234567890).
            self.tabela.insert(
                "", "end", iid=str(objeto.id),
                values=(objeto.id,) + tuple(self.valores_linha(objeto)),
            )

    def salvar(self):
        _, erro = self.enviar(self.id_carregado)
        if self._mostrar(erro, "Registro salvo."):
            self.limpar()
            self.recarregar()

    def excluir(self):
        selecao = self.tabela.selection()
        id = int(selecao[0]) if selecao else self.id_carregado
        if id is None:
            messagebox.showwarning("Aviso", "Selecione um registro na lista.")
            return
        if not messagebox.askyesno("Confirmar", f"Excluir o registro {id}?"):
            return
        _, erro = self.controller.excluir(id)
        if self._mostrar(erro, "Registro excluído."):
            self.limpar()
            self.recarregar()

    def carregar_selecionado(self):
        selecao = self.tabela.selection()
        if not selecao:
            return
        objeto = self.controller.buscar_por_id(int(selecao[0]))
        if objeto is None:
            return
        self.id_carregado = objeto.id
        self.preencher(objeto)
        self.status.config(text=f"Editando o registro {objeto.id}. Enter salva, Esc cancela.")

    def limpar(self):
        self.id_carregado = None
        self.limpar_campos()
        self.tabela.selection_remove(*self.tabela.selection())
        self.status.config(text="Novo registro.")

    def _mostrar(self, erro, mensagem_ok):
        if erro:
            self.status.config(text=f"Erro: {erro}")
            messagebox.showerror("Erro", erro)
            return False
        self.status.config(text=mensagem_ok)
        return True

    def _ligar_eventos(self):
        for widget in self._descendentes(self.form):
            widget.bind("<Return>", lambda e: self.salvar())
            widget.bind("<Escape>", lambda e: self.limpar())
        self.tabela.bind("<Double-1>", lambda e: self.carregar_selecionado())
        self.tabela.bind("<Return>", lambda e: self.carregar_selecionado())
        self.tabela.bind("<Delete>", lambda e: self.excluir())
        self.tabela.bind("<Escape>", lambda e: self.limpar())
        # Ao voltar para esta aba, recarrega (outra aba pode ter mudado os dados).
        self.notebook.bind("<<NotebookTabChanged>>", self._ao_trocar_aba, add="+")

    def _ao_trocar_aba(self, _evento):
        if self.notebook.select() == str(self.frame):
            self.recarregar()

    def _descendentes(self, widget):
        for filho in widget.winfo_children():
            yield filho
            yield from self._descendentes(filho)
