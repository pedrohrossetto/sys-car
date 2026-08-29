from controller.proprietario_controller import ProprietarioController


class ProprietarioView:
    def __init__(self):
        self.controller = ProprietarioController()

    def exibir_menu(self):
        while True:
            print("\n=== CRUD PROPRIETÁRIO ===")
            print("1. Cadastrar")
            print("2. Listar")
            print("3. Buscar por ID")
            print("4. Atualizar")
            print("5. Excluir")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                self.cadastrar()
            elif opcao == "2":
                self.listar()
            elif opcao == "3":
                self.buscar_por_id()
            elif opcao == "4":
                self.atualizar()
            elif opcao == "5":
                self.excluir()
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")

    def cadastrar(self):
        nome = input("Nome: ").strip()
        cpf = input("CPF: ").strip()
        cnpj = input("CNPJ (opcional): ").strip() or None
        proprietario, erro = self.controller.criar(nome, cpf, cnpj)
        if erro:
            print(f"Erro: {erro}")
        else:
            print(f"Proprietário cadastrado com ID {proprietario.id}.")

    def listar(self):
        proprietarios = self.controller.listar()
        if not proprietarios:
            print("Nenhum proprietário cadastrado.")
            return
        print("\n--- PROPRIETÁRIOS ---")
        for p in proprietarios:
            print(f"ID {p.id} | {p.nome} | CPF {p.cpf} | CNPJ {p.cnpj or '-'}")

    def buscar_por_id(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        p = self.controller.buscar_por_id(id)
        if not p:
            print("Proprietário não encontrado.")
            return
        print(f"ID {p.id} | {p.nome} | CPF {p.cpf} | CNPJ {p.cnpj or '-'}")

    def atualizar(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        p = self.controller.buscar_por_id(id)
        if not p:
            print("Proprietário não encontrado.")
            return
        nome = input(f"Nome ({p.nome}): ").strip() or p.nome
        cpf = input(f"CPF ({p.cpf}): ").strip() or p.cpf
        cnpj = input(f"CNPJ ({p.cnpj or '-'}): ").strip() or p.cnpj
        proprietario, erro = self.controller.atualizar(id, nome, cpf, cnpj)
        if erro:
            print(f"Erro: {erro}")
        else:
            print(f"Proprietário {proprietario.id} atualizado.")

    def excluir(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        confirmacao = input(f"Deseja excluir o proprietário {id}? (s/N): ").strip()
        if confirmacao.lower() != "s":
            print("Exclusão cancelada.")
            return
        sucesso, erro = self.controller.excluir(id)
        if erro:
            print(f"Erro: {erro}")
        else:
            print("Proprietário excluído.")
