from tkinter import ttk

from controller.fiscalizacao.unidade_controller import UnidadeController
from view.fiscalizacao.componentes import (
    PainelCrud, ao_mostrar_aba, criar_tabela, id_selecionado, mostrar_resultado,
    preencher_tabela,
)

ORDEM = 70


class UnidadesAba:
    def __init__(self, notebook):
        self.controller = UnidadeController()
        c = self.controller
        self.frame = ttk.Frame(notebook, padding=8)
        notebook.add(self.frame, text="Unidades e Notificações")

        self.unidades = PainelCrud(
            self.frame, "Unidades competentes",
            campos=[("nome", "Nome"), ("tipo", "Tipo de unidade/órgão"), ("contato", "Contato")],
            colunas=("Nome", "Tipo", "Contato"),
            listar=c.listar,
            linha=lambda u: (u.nome, u.tipo_unidade_orgao or "-", u.contato or "-"),
            valores=lambda u: {"nome": u.nome, "tipo": u.tipo_unidade_orgao, "contato": u.contato},
            buscar=c.buscar_por_id,
            salvar=lambda id, d: (c.criar(d["nome"], d["tipo"], d["contato"]) if id is None
                                  else c.atualizar(id, d["nome"], d["tipo"], d["contato"])),
            excluir=c.excluir,
        )
        self.unidades.pack(fill="both", expand=True)

        caixa = ttk.LabelFrame(self.frame, text="Notificações recebidas", padding=6)
        caixa.pack(fill="both", expand=True, pady=(6, 0))
        quadro, self.notificacoes = criar_tabela(
            caixa, ("ID", "Alerta", "Unidade", "Data", "Situação", "Mensagem"), altura=6)
        self.notificacoes.column("Mensagem", width=360, anchor="w")
        self.notificacoes.tag_configure("ENVIADA", font=("TkDefaultFont", 9, "bold"))
        quadro.pack(fill="both", expand=True)
        ttk.Button(caixa, text="Marcar como lida (ou duplo clique)",
                   command=self._marcar_lida).pack(anchor="w", pady=4)
        self.notificacoes.bind("<Double-1>", lambda e: self._marcar_lida())

        ao_mostrar_aba(notebook, self.frame, self.recarregar)
        self.recarregar()

    def recarregar(self):
        self.unidades.recarregar()
        nomes = {u.id: u.nome for u in self.controller.listar()}
        preencher_tabela(self.notificacoes, [
            (n.id, (n.registro_id, nomes.get(n.unidade_id, "?"), n.data, n.status, n.mensagem), n.status)
            for n in self.controller.listar_notificacoes()
        ])

    def _marcar_lida(self):
        id = id_selecionado(self.notificacoes)
        if id is None:
            return
        _, erro = self.controller.marcar_lida(id)
        if mostrar_resultado(erro):
            self.recarregar()


def registrar_abas(notebook):
    UnidadesAba(notebook)
