"""Componentes reutilizados pelas abas da fiscalização."""
import tkinter as tk
from tkinter import messagebox, ttk

CORES_STATUS = {
    "PENDENTE": "#fff4cc",
    "CONFIRMADO": "#ffd6d6",
    "RESOLVIDO": "#d9f2d9",
    "CANCELADO": "#e6e6e6",
    "EMITIDA": "#d9f2d9",
    "NEGADA": "#ffd6d6",
}


def corrigir_cores_treeview(widget):
    """Contorna um bug do Tk 8.6.9 em que as cores de tag do Treeview são ignoradas."""
    estilo = ttk.Style(widget)

    def sem_padrao(opcao):
        return [e for e in estilo.map("Treeview", query_opt=opcao) if e[:2] != ("!disabled", "!selected")]

    estilo.map("Treeview", foreground=sem_padrao("foreground"), background=sem_padrao("background"))


def criar_tabela(parent, colunas, altura=8):
    """Treeview com barra de rolagem e uma tag de cor por status. Retorna (quadro, treeview)."""
    quadro = ttk.Frame(parent)
    tabela = ttk.Treeview(
        quadro, columns=colunas, show="headings", height=altura, selectmode="browse"
    )
    barra = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra.set)
    for coluna in colunas:
        tabela.heading(coluna, text=coluna)
        tabela.column(coluna, width=50 if coluna == "ID" else 120, anchor="center")
    for status, cor in CORES_STATUS.items():
        tabela.tag_configure(status, background=cor)
    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return quadro, tabela


def preencher_tabela(tabela, linhas):
    """linhas: lista de (id, valores, tag ou None)."""
    tabela.delete(*tabela.get_children())
    for id, valores, tag in linhas:
        tabela.insert("", "end", iid=str(id), values=(id,) + tuple(valores),
                      tags=(tag,) if tag else ())


def id_selecionado(tabela):
    selecao = tabela.selection()
    return int(selecao[0]) if selecao else None


def mostrar_resultado(erro, status_label=None, mensagem_ok=""):
    """Mostra o erro numa caixa de diálogo. Devolve True se não houve erro."""
    if erro:
        messagebox.showerror("Erro", erro)
        if status_label is not None:
            status_label.config(text=f"Erro: {erro}")
        return False
    if status_label is not None:
        status_label.config(text=mensagem_ok)
    return True


class Seletor:
    """Combobox que mostra rótulos e devolve o id escolhido."""

    def __init__(self, parent, largura=30):
        self.combo = ttk.Combobox(parent, state="readonly", width=largura)
        self._ids = []

    def grid(self, **opcoes):
        self.combo.grid(**opcoes)

    def definir_opcoes(self, opcoes):
        atual = self.id_selecionado()
        self._ids = [id for id, _ in opcoes]
        self.combo["values"] = [rotulo for _, rotulo in opcoes]
        self.selecionar(atual)

    def id_selecionado(self):
        indice = self.combo.current()
        return self._ids[indice] if 0 <= indice < len(self._ids) else None

    def selecionar(self, id):
        if id in self._ids:
            self.combo.current(self._ids.index(id))
        else:
            self.combo.set("")


class PainelCrud(ttk.LabelFrame):
    """Formulário + tabela para cadastros simples (satélite, usuário, unidade).

    Recebe funções em vez de herdar: assim o mesmo painel serve para
    controllers com nomes de métodos diferentes.
      campos: lista de (chave, rótulo)
      listar() -> objetos;  linha(obj) -> tupla sem o id
      valores(obj) -> dict chave -> texto (para carregar o formulário)
      buscar(id) -> obj;  salvar(id ou None, dados) -> (res, erro);  excluir(id) -> (res, erro)
    """

    def __init__(self, parent, titulo, campos, colunas, listar, linha, valores,
                 buscar, salvar, excluir):
        super().__init__(parent, text=titulo, padding=6)
        self._listar, self._linha, self._valores = listar, linha, valores
        self._buscar, self._salvar, self._excluir = buscar, salvar, excluir
        self.id_carregado = None
        self.variaveis = {}
        self.entradas = {}
        formulario = ttk.Frame(self)
        formulario.pack(fill="x")
        formulario.columnconfigure(1, weight=1)
        for linha_grid, (chave, rotulo) in enumerate(campos):
            ttk.Label(formulario, text=rotulo).grid(row=linha_grid, column=0, sticky="e", padx=4, pady=2)
            variavel = tk.StringVar()
            entrada = ttk.Entry(formulario, textvariable=variavel)
            entrada.grid(row=linha_grid, column=1, sticky="ew", padx=4, pady=2)
            self.variaveis[chave] = variavel
            self.entradas[chave] = entrada
        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=4)
        ttk.Button(botoes, text="Salvar", command=self.salvar).pack(side="left", padx=2)
        ttk.Button(botoes, text="Excluir", command=self.excluir).pack(side="left", padx=2)
        ttk.Button(botoes, text="Limpar", command=self.limpar).pack(side="left", padx=2)
        quadro, self.tabela = criar_tabela(self, ("ID",) + tuple(colunas), altura=6)
        quadro.pack(fill="both", expand=True)
        self.tabela.bind("<<TreeviewSelect>>", lambda e: self.carregar())

    def recarregar(self):
        preencher_tabela(self.tabela, [(o.id, self._linha(o), None) for o in self._listar()])

    def carregar(self):
        objeto = self._buscar(id_selecionado(self.tabela)) if self.tabela.selection() else None
        if objeto is None:
            return
        self.id_carregado = objeto.id
        for chave, texto in self._valores(objeto).items():
            self.variaveis[chave].set(texto or "")

    def salvar(self):
        dados = {chave: var.get() for chave, var in self.variaveis.items()}
        _, erro = self._salvar(self.id_carregado, dados)
        if mostrar_resultado(erro):
            self.limpar()
            self.recarregar()

    def excluir(self):
        id = id_selecionado(self.tabela)
        if id is None:
            messagebox.showwarning("Aviso", "Selecione um registro na lista.")
            return
        if not messagebox.askyesno("Confirmar", f"Excluir o registro {id}?"):
            return
        _, erro = self._excluir(id)
        if mostrar_resultado(erro):
            self.limpar()
            self.recarregar()

    def limpar(self):
        self.id_carregado = None
        for variavel in self.variaveis.values():
            variavel.set("")
        self.tabela.selection_remove(*self.tabela.selection())


def ao_mostrar_aba(notebook, frame, funcao):
    """Chama funcao() sempre que a aba de 'frame' for selecionada."""
    def tratar(_evento):
        if notebook.select() == str(frame):
            funcao()
    notebook.bind("<<NotebookTabChanged>>", tratar, add="+")
