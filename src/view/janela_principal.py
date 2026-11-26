import tkinter as tk
import traceback
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
        # Última defesa (ADR-003): um erro não tratado num evento vira uma caixa de erro.
        root.report_callback_exception = self._erro_inesperado
        root.title("SYS-CAR")
        root.geometry("1180x800")
        root.minsize(960, 640)
        self._criar_menu()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)
        for modulo in ordenar_por_ordem(modulos_com(view, "registrar_abas")):
            modulo.registrar_abas(self.notebook)

    def _erro_inesperado(self, tipo, valor, rastro):
        """Mostra o erro ao usuário e escreve o rastro completo no terminal."""
        traceback.print_exception(tipo, valor, rastro)
        messagebox.showerror(
            "Erro inesperado",
            f"A ação não foi concluída.\n\n{tipo.__name__}: {valor}",
            parent=self.root,
        )

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
