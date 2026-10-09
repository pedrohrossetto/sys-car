import tkinter as tk
from tkinter import ttk

from controller.proprietario_controller import ProprietarioController
from view.aba_crud import AbaCrud

ORDEM = 10


def _aceita_cpf(texto):
    """validatecommand: CPF aceita dígitos, ponto e hífen (máx. 14 caracteres)."""
    return len(texto) <= 14 and all(c.isdigit() or c in ".-" for c in texto)


def _aceita_cnpj(texto):
    """validatecommand: CNPJ aceita letras, dígitos, ponto, barra e hífen."""
    return len(texto) <= 18 and all(c.isalnum() or c in "./-" for c in texto)


def formatar_documento(proprietario):
    doc = proprietario.documento or ""
    if proprietario.tipo == "PF" and len(doc) == 11:
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    if proprietario.tipo == "PJ" and len(doc) == 14:
        return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    return doc


class ProprietarioAba(AbaCrud):
    TITULO = "Proprietários"
    COLUNAS = ("Nome", "Tipo", "Documento")

    def __init__(self, notebook):
        self.controller = ProprietarioController()
        super().__init__(notebook)

    def criar_campos(self, form):
        self.nome = tk.StringVar()
        self.tipo = tk.StringVar(value="PF")
        self.cpf = tk.StringVar()
        self.cnpj = tk.StringVar()

        ttk.Label(form, text="Nome").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(form, textvariable=self.nome).grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Tipo").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        tipos = ttk.Frame(form)
        tipos.grid(row=1, column=1, sticky="w")
        for valor, rotulo in (("PF", "Pessoa física"), ("PJ", "Pessoa jurídica")):
            ttk.Radiobutton(
                tipos, text=rotulo, value=valor, variable=self.tipo,
                command=self._trocar_tipo,
            ).pack(side="left", padx=4)

        ttk.Label(form, text="CPF").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        self.entrada_cpf = ttk.Entry(
            form, textvariable=self.cpf, validate="key",
            validatecommand=(form.register(_aceita_cpf), "%P"),
        )
        self.entrada_cpf.grid(row=2, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="CNPJ").grid(row=3, column=0, sticky="e", padx=4, pady=2)
        self.entrada_cnpj = ttk.Entry(
            form, textvariable=self.cnpj, validate="key",
            validatecommand=(form.register(_aceita_cnpj), "%P"),
        )
        self.entrada_cnpj.grid(row=3, column=1, sticky="ew", padx=4, pady=2)
        self._trocar_tipo()

    def _trocar_tipo(self):
        """Evento do Radiobutton: habilita só o campo do documento do tipo escolhido."""
        pessoa_fisica = self.tipo.get() == "PF"
        self.entrada_cpf.state(["!disabled"] if pessoa_fisica else ["disabled"])
        self.entrada_cnpj.state(["disabled"] if pessoa_fisica else ["!disabled"])

    def limpar_campos(self):
        for variavel in (self.nome, self.cpf, self.cnpj):
            variavel.set("")
        self.tipo.set("PF")
        self._trocar_tipo()

    def preencher(self, p):
        self.nome.set(p.nome)
        self.tipo.set(p.tipo)
        self.cpf.set(p.cpf or "")
        self.cnpj.set(p.cnpj or "")
        self._trocar_tipo()

    def valores_linha(self, p):
        return (p.nome, p.tipo, formatar_documento(p))

    def enviar(self, id):
        dados = (self.nome.get(), self.tipo.get(), self.cpf.get(), self.cnpj.get())
        if id is None:
            return self.controller.criar(*dados)
        return self.controller.atualizar(id, *dados)


def registrar_abas(notebook):
    ProprietarioAba(notebook)
