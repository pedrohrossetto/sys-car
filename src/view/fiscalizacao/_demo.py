"""Abre só as abas da Fiscalização, para testar antes da integração.

Uso (a partir da pasta src):  python3 -m view.fiscalizacao._demo
O nome começa com "_" para a janela principal NÃO carregar este arquivo.
Para ter propriedades na lista, cadastre-as antes pelo programa principal
(python3 src/main.py), que usa o mesmo banco data/syscar.db.
"""


def main():
    import tkinter as tk
    from tkinter import ttk

    from controller.fiscalizacao.instalacao import preparar_banco
    from view.fiscalizacao import alertas_aba, conformidade_aba, fontes_aba, unidades_aba

    preparar_banco()
    root = tk.Tk()
    root.title("SYS-CAR - Fiscalização (demonstração)")
    root.geometry("1000x680")
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=6, pady=6)
    for modulo in sorted((fontes_aba, alertas_aba, unidades_aba, conformidade_aba),
                         key=lambda m: m.ORDEM):
        modulo.registrar_abas(notebook)
    root.mainloop()


if __name__ == "__main__":
    main()
