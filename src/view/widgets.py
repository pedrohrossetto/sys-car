"""Componentes reutilizados pelas abas do cadastro."""
from tkinter import ttk


class Seletor:
    """Combobox que mostra rótulos (nomes) e devolve o id escolhido."""

    def __init__(self, parent, largura=40):
        self.combo = ttk.Combobox(parent, state="readonly", width=largura)
        self._ids = []

    def grid(self, **opcoes):
        self.combo.grid(**opcoes)

    def definir_opcoes(self, opcoes):
        """opcoes: lista de (id, rótulo). Mantém a seleção atual se ela ainda existir."""
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


def criar_tabela(parent, colunas, altura=12):
    """Cria um Treeview com barra de rolagem vertical. Retorna (quadro, treeview)."""
    quadro = ttk.Frame(parent)
    tabela = ttk.Treeview(
        quadro, columns=colunas, show="headings", height=altura, selectmode="browse"
    )
    barra = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra.set)
    for coluna in colunas:
        tabela.heading(coluna, text=coluna)
        tabela.column(coluna, width=60 if coluna == "ID" else 140, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return quadro, tabela
