from view.proprietario_view import ProprietarioView
from view.propriedade_rural_view import PropriedadeRuralView
from view.localizacao_view import LocalizacaoView


def main():
    while True:
        print("\n=== SYS-CAR ===")
        print("1. CRUD Proprietário")
        print("2. CRUD Propriedade Rural")
        print("3. CRUD Localização")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            ProprietarioView().exibir_menu()
        elif opcao == "2":
            PropriedadeRuralView().exibir_menu()
        elif opcao == "3":
            LocalizacaoView().exibir_menu()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")