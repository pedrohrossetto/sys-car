import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_TK = True
except ImportError:
    HAS_TK = False

from database.database import init_db
from model.proprietario import Proprietario
from model.propriedade_rural import PropriedadeRural
from model.localizacao import Localizacao
from controller.proprietario_controller import ProprietarioController
from controller.propriedade_rural_controller import PropriedadeRuralController
from controller.localizacao_controller import LocalizacaoController


# Dicionário que descreve as três entidades de forma declarativa.
# A view é genérica: lê daqui os campos do formulário, as colunas da
# tabela e as funções de refresh/linha, então não repete código por entidade.
ENTIDADES = {
    "Proprietários": {
        "controller": ProprietarioController(),
        "todos": Proprietario.listar_todos,
        "campos": [("nome", "Nome"), ("cpf", "CPF"), ("cnpj", "CNPJ (opcional)")],
        "colunas": ["ID", "Nome", "CPF", "CNPJ"],
        "linha": lambda p: (p.id, p.nome, p.cpf, p.cnpj or "-"),
    },
    "Propriedades Rurais": {
        "controller": PropriedadeRuralController(),
        "todos": PropriedadeRural.listar_todos,
        "campos": [
            ("nome", "Nome"),
            ("proprietario_id", "ID do Proprietário"),
            ("cadastro_publico", "Cadastro público (opcional)"),
        ],
        "colunas": ["ID", "Nome", "Cadastro", "Prop. ID"],
        "linha": lambda p: (p.id, p.nome, p.cadastro_publico or "-", p.proprietario_id),
    },
    "Localizações": {
        "controller": LocalizacaoController(),
        "todos": Localizacao.listar_todas,
        "campos": [
            ("propriedade_id", "ID da Propriedade"),
            ("latitude", "Latitude"),
            ("longitude", "Longitude"),
            ("altitude", "Altitude"),
            ("poligono_geometria", "Polígono (opcional)"),
        ],
        "colunas": ["ID", "Prop. ID", "Lat", "Lon", "Alt", "Polígono"],
        "linha": lambda l: (
            l.id, l.propriedade_id, l.latitude, l.longitude,
            l.altitude, l.poligono_geometria or "-",
        ),
    },
}


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SYS-CAR")
        self.entradas = {}
        self.campos_atual = []

        self.combo = ttk.Combobox(
            root, values=list(ENTIDADES), state="readonly"
        )
        self.combo.pack(pady=5)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._trocar_entidade())
        self.combo.current(0)

        self.frame_form = tk.Frame(root)
        self.frame_form.pack(pady=5)

        self.frame_botoes = tk.Frame(root)
        self.frame_botoes.pack()

        tk.Button(self.frame_botoes, text="Cadastrar", command=self._cadastrar).pack(
            side="left", padx=5, pady=5
        )
        tk.Button(self.frame_botoes, text="Atualizar WIP", command=self._atualizar).pack(
            side="left", padx=5, pady=5
        )
        tk.Button(self.frame_botoes, text="Excluir WIP", command=self._excluir).pack(
            side="left", padx=5, pady=5
        )

        self.tree = ttk.Treeview(root, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", lambda e: self._carregar_selecionado())

        self.status = tk.Label(root, text="", fg="green")
        self.status.pack()

        self._trocar_entidade()

    def _trocar_entidade(self):
        # Reconstrói o formulário sempre que o usuário troca a entidade
        # no Combobox. "self.entradas" guarda os campos (StringVar) criados.
        for w in self.frame_form.winfo_children():
            w.destroy()
        self.entradas = {}
        self.campos_atual = ENTIDADES[self.combo.get()]["campos"]
        for chave, rotulo in self.campos_atual:
            tk.Label(self.frame_form, text=rotulo).grid(
                row=len(self.entradas), column=0, sticky="e", padx=5, pady=2
            )
            var = tk.StringVar()
            self.entradas[chave] = var
            tk.Entry(self.frame_form, textvariable=var).grid(
                row=len(self.entradas) - 1, column=1, sticky="ew", padx=5, pady=2
            )
        colunas = ENTIDADES[self.combo.get()]["colunas"]
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = colunas
        for c in colunas:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self._atualizar_lista()

    def _valores_form(self):
        # Lê todos os campos do formulário. Campos vazios viram None.
        dados = {k: v.get().strip() for k, v in self.entradas.items()}
        for k in dados:
            if not dados[k]:
                dados[k] = None
        return dados

    def _cadastrar(self):
        dados = self._valores_form()
        ctrl = ENTIDADES[self.combo.get()]["controller"]
        # Cada entidade tem campos e ordem diferentes, então o cadastro
        # é chamado separadamente para cada uma.
        if self.combo.get() == "Proprietários":
            _, erro = ctrl.criar(dados["nome"], dados["cpf"], dados["cnpj"])
        elif self.combo.get() == "Propriedades Rurais":
            _, erro = ctrl.criar(dados["nome"], dados["proprietario_id"], dados["cadastro_publico"])
        else:
            _, erro = ctrl.criar(
                dados["propriedade_id"], dados["latitude"], dados["longitude"],
                dados["altitude"], dados["poligono_geometria"],
            )
        self._feedback(erro, "Registro cadastrado.")
        self._limpar()

    def _carregar_selecionado(self):
        # Ao dar duplo clique numa linha, copia os valores dela para o
        # formulário, onde podem ser editados e então salvos com "Atualizar".
        sel = self.tree.selection()
        if not sel:
            return
        valores = self.tree.item(sel[0])["values"]
        chaves = list(self.entradas.keys())
        for i, chave in enumerate(chaves):
            self.entradas[chave].set(valores[i + 1] if valores[i + 1] != "-" else "")

    def _atualizar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro na lista.")
            return
        id_reg = self.tree.item(sel[0])["values"][0]
        dados = self._valores_form()
        ctrl = ENTIDADES[self.combo.get()]["controller"]
        if self.combo.get() == "Proprietários":
            _, erro = ctrl.atualizar(id_reg, dados["nome"], dados["cpf"], dados["cnpj"])
        elif self.combo.get() == "Propriedades Rurais":
            _, erro = ctrl.atualizar(
                id_reg, dados["nome"], dados["proprietario_id"], dados["cadastro_publico"]
            )
        else:
            _, erro = ctrl.atualizar(
                id_reg, dados["propriedade_id"], dados["latitude"], dados["longitude"],
                dados["altitude"], dados["poligono_geometria"],
            )
        self._feedback(erro, "Registro atualizado.")
        self._limpar()

    def _excluir(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro na lista.")
            return
        id_reg = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", f"Excluir o registro {id_reg}?"):
            return
        ctrl = ENTIDADES[self.combo.get()]["controller"]
        _, erro = ctrl.excluir(id_reg)
        self._feedback(erro, "Registro excluído.")
        self._limpar()

    def _atualizar_lista(self):
        # Reconstrói a tabela com todos os registros atuais. É chamado
        # automaticamente após cada operação, por isso não há botão "Listar".
        self.tree.delete(*self.tree.get_children())
        dados = ENTIDADES[self.combo.get()]["todos"]()
        for registro in dados:
            self.tree.insert(
                "", "end", values=ENTIDADES[self.combo.get()]["linha"](registro)
            )

    def _feedback(self, erro, ok):
        if erro:
            self.status.config(text=f"Erro: {erro}", fg="red")
            messagebox.showerror("Erro", erro)
        else:
            self.status.config(text=ok, fg="green")
            self._atualizar_lista()

    def _limpar(self):
        for v in self.entradas.values():
            v.set("")
        self.tree.selection_remove(*self.tree.selection())


def main():
    init_db()
    if not HAS_TK:
        print("Tkinter não disponível neste ambiente.")
        return
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()