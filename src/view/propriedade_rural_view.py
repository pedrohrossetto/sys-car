from controller.propriedade_rural_controller import PropriedadeRuralController


class PropriedadeRuralView:
    def __init__(self):
        self.controller = PropriedadeRuralController()

    def exibir_menu(self):
        while True:
            print("\n=== CRUD PROPRIEDADE RURAL ===")
            print("1. Cadastrar")
            print("2. Buscar por ID")
            print("3. Atualizar")
            print("4. Excluir")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                self.cadastrar()
            elif opcao == "2":
                self.buscar_por_id()
            elif opcao == "3":
                self.atualizar()
            elif opcao == "4":
                self.excluir()
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")

    def _perguntar_proprietario_id(self):
        try:
            return int(input("ID do proprietário (0 para ver os cadastrados): ").strip())
        except ValueError:
            print("ID inválido.")
            return None

    def _obter_proprietario_id(self, atual=None):
        proprietario_id = self._perguntar_proprietario_id()
        if proprietario_id is None:
            return None
        if proprietario_id != 0:
            return proprietario_id
        from model.proprietario import Proprietario
        for p in Proprietario.listar_todos():
            print(f"ID {p.id} | {p.nome} | CPF {p.cpf}")
        return self._obter_proprietario_id(atual)

    def cadastrar(self):
        nome = input("Nome: ").strip()
        proprietario_id = self._obter_proprietario_id()
        if proprietario_id is None:
            return
        cadastro_publico = input("Cadastro público (opcional): ").strip() or None
        propriedade, erro = self.controller.criar(
            nome, proprietario_id, cadastro_publico
        )
        if erro:
            print(f"Erro: {erro}")
        else:
            print(f"Propriedade cadastrada com ID {propriedade.id}.")

    def buscar_por_id(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        p = self.controller.buscar_por_id(id)
        if not p:
            print("Propriedade não encontrada.")
            return
        print(
            f"ID {p.id} | {p.nome} | Cadastro {p.cadastro_publico or '-'} "
            f"| Proprietário ID {p.proprietario_id}"
        )

    def atualizar(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        p = self.controller.buscar_por_id(id)
        if not p:
            print("Propriedade não encontrada.")
            return
        nome = input(f"Nome ({p.nome}): ").strip() or p.nome
        proprietario_id = self._obter_proprietario_id(p.proprietario_id)
        if proprietario_id is None:
            proprietario_id = p.proprietario_id
        cadastro_publico = input(
            f"Cadastro público ({p.cadastro_publico or '-'}): "
        ).strip() or p.cadastro_publico
        propriedade, erro = self.controller.atualizar(
            id, nome, proprietario_id, cadastro_publico
        )
        if erro:
            print(f"Erro: {erro}")
        else:
            print(f"Propriedade {propriedade.id} atualizada.")

    def excluir(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        confirmacao = input(f"Deseja excluir a propriedade {id}? (s/N): ").strip()
        if confirmacao.lower() != "s":
            print("Exclusão cancelada.")
            return
        sucesso, erro = self.controller.excluir(id)
        if erro:
            print(f"Erro: {erro}")
        else:
            print("Propriedade excluída.")