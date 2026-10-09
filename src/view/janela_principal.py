import tkinter as tk
from tkinter import messagebox, ttk

import view
from descoberta import modulos_com, ordenar_por_ordem

SOBRE = (
    "SYS-CAR - Sistema de Cadastro Ambiental Rural\n"
    "IFSul Passo Fundo - Linguagem de Programação Orientada a Objetos"
)


class JanelaPrincipal:
    """Janela com barra de menu e um Notebook.

    As abas não são listadas aqui: todo módulo do pacote 'view' que
    define registrar_abas(notebook) é descoberto e chamado, na ordem da
    constante ORDEM (contrato de plugin, veja docs/decisoes/ADR-001).
    """

    def __init__(self, root):
        self.root = root
        root.title("SYS-CAR")
        root.geometry("960x640")
        root.minsize(720, 480)
        self._criar_menu()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)
        for modulo in ordenar_por_ordem(modulos_com(view, "registrar_abas")):
            modulo.registrar_abas(self.notebook)

    def _criar_menu(self):
        barra = tk.Menu(self.root)
        arquivo = tk.Menu(barra, tearoff=False)
        arquivo.add_command(label="Sair", accelerator="Ctrl+Q", command=self.root.destroy)
        barra.add_cascade(label="Arquivo", menu=arquivo)
        ajuda = tk.Menu(barra, tearoff=False)
        ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", SOBRE))
        barra.add_cascade(label="Ajuda", menu=ajuda)
        self.root.config(menu=barra)
        self.root.bind_all("<Control-q>", lambda e: self.root.destroy())


def main():
    root = tk.Tk()
    JanelaPrincipal(root)
    root.mainloop()
