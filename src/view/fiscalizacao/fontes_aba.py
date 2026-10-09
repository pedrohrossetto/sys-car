from tkinter import ttk

from controller.fiscalizacao.fonte_controller import FonteController
from view.fiscalizacao.componentes import PainelCrud, ao_mostrar_aba

ORDEM = 50


class FontesAba:
    """Cadastro das fontes de detecção: satélites e usuários denunciantes."""

    def __init__(self, notebook):
        self.controller = FonteController()
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text="Fontes")
        self.frame.columnconfigure((0, 1), weight=1, uniform="metade")
        self.frame.rowconfigure(0, weight=1)
        c = self.controller

        self.satelites = PainelCrud(
            self.frame, "Satélites",
            campos=[("nome", "Nome"), ("entidade", "Entidade responsável")],
            colunas=("Nome", "Entidade"),
            listar=c.listar_satelites,
            linha=lambda s: (s.nome, s.entidade_responsavel or "-"),
            valores=lambda s: {"nome": s.nome, "entidade": s.entidade_responsavel},
            buscar=c.buscar_satelite,
            salvar=lambda id, d: (c.criar_satelite(d["nome"], d["entidade"]) if id is None
                                  else c.atualizar_satelite(id, d["nome"], d["entidade"])),
            excluir=c.excluir_satelite,
        )
        self.satelites.grid(row=0, column=0, sticky="nsew", padx=4)

        self.usuarios = PainelCrud(
            self.frame, "Usuários (denunciantes)",
            campos=[("nome", "Nome"), ("cpf", "CPF"), ("email", "E-mail")],
            colunas=("Nome", "CPF", "E-mail"),
            listar=c.listar_usuarios,
            linha=lambda u: (u.nome, u.cpf, u.email),
            valores=lambda u: {"nome": u.nome, "cpf": u.cpf, "email": u.email},
            buscar=c.buscar_usuario,
            salvar=lambda id, d: (c.criar_usuario(d["nome"], d["cpf"], d["email"]) if id is None
                                  else c.atualizar_usuario(id, d["nome"], d["cpf"], d["email"])),
            excluir=c.excluir_usuario,
        )
        self.usuarios.grid(row=0, column=1, sticky="nsew", padx=4)

        # Validação no evento <FocusOut>: avisa assim que o usuário sai do campo.
        self.aviso_email = ttk.Label(self.usuarios, text="", foreground="red")
        self.aviso_email.pack(before=self.usuarios.winfo_children()[1], anchor="w")
        self.usuarios.entradas["email"].bind("<FocusOut>", self._conferir_email)

        ao_mostrar_aba(notebook, self.frame, self.recarregar)
        self.recarregar()

    def _conferir_email(self, _evento=None):
        email = self.usuarios.variaveis["email"].get()
        invalido = bool(email.strip()) and not self.controller.email_valido(email)
        self.aviso_email.config(text="E-mail inválido." if invalido else "")

    def recarregar(self):
        self.satelites.recarregar()
        self.usuarios.recarregar()


def registrar_abas(notebook):
    FontesAba(notebook)
