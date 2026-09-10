from controller.localizacao_controller import LocalizacaoController


class LocalizacaoView:
    def __init__(self):
        self.controller = LocalizacaoController()

    def exibir_menu(self):
        while True:
            print("\n=== CRUD LOCALIZAÇÃO ===")
            print("1. Cadastrar")
            print("2. Buscar por ID")
            print("3. Buscar por propriedade")
            print("4. Atualizar")
            print("5. Excluir")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                self.cadastrar()
            elif opcao == "2":
                self.buscar_por_id()
            elif opcao == "3":
                self.buscar_por_propriedade()
            elif opcao == "4":
                self.atualizar()
            elif opcao == "5":
                self.excluir()
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")

    def _ler_float(self, rotulo, atual=""):
        valor = input(f"{rotulo} ({atual or '-'}): ").strip()
        if not valor:
            return atual
        try:
            return float(valor)
        except ValueError:
            print("Valor numérico inválido.")
            return None

    def _obter_propriedade_id(self):
        try:
            propriedade_id = int(input("ID da propriedade (0 para ver as cadastradas): ").strip())
        except ValueError:
            print("ID inválido.")
            return None
        if propriedade_id != 0:
            return propriedade_id
        from model.propriedade_rural import PropriedadeRural
        for p in PropriedadeRural.listar_todos():
            print(f"ID {p.id} | {p.nome} | Proprietário ID {p.proprietario_id}")
        return self._obter_propriedade_id()

    def cadastrar(self):
        propriedade_id = self._obter_propriedade_id()
        if propriedade_id is None:
            return
        latitude = self._ler_float("Latitude")
        if latitude is None:
            return
        longitude = self._ler_float("Longitude")
        if longitude is None:
            return
        altitude = self._ler_float("Altitude")
        if altitude is None:
            return
        poligono_geometria = input("Polígono (opcional): ").strip() or None
        localizacao, erro = self.controller.criar(
            propriedade_id, latitude, longitude, altitude, poligono_geometria
        )
        if erro:
            print(f"Erro: {erro}")
        else:
            print(f"Localização cadastrada com ID {localizacao.id}.")

    def buscar_por_id(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        l = self.controller.buscar_por_id(id)
        if not l:
            print("Localização não encontrada.")
            return
        self._mostrar(l)

    def buscar_por_propriedade(self):
        try:
            propriedade_id = int(input("ID da propriedade: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        l = self.controller.buscar_por_propriedade(propriedade_id)
        if not l:
            print("Nenhuma localização para esta propriedade.")
            return
        self._mostrar(l)

    def _mostrar(self, l):
        print(
            f"ID {l.id} | Propriedade {l.propriedade_id} | "
            f"Lat {l.latitude} | Lon {l.longitude} | Alt {l.altitude} | "
            f"Polígono {l.poligono_geometria or '-'}"
        )

    def atualizar(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        l = self.controller.buscar_por_id(id)
        if not l:
            print("Localização não encontrada.")
            return
        propriedade_id = self._obter_propriedade_id()
        if propriedade_id is None:
            propriedade_id = l.propriedade_id
        latitude = self._ler_float("Latitude", l.latitude)
        longitude = self._ler_float("Longitude", l.longitude)
        altitude = self._ler_float("Altitude", l.altitude)
        poligono_geometria = input(
            f"Polígono ({l.poligono_geometria or '-'}): "
        ).strip() or l.poligono_geometria
        localizacao, erro = self.controller.atualizar(
            id, propriedade_id, latitude, longitude, altitude, poligono_geometria
        )
        if erro:
            print(f"Erro: {erro}")
        else:
            print(f"Localização {localizacao.id} atualizada.")

    def excluir(self):
        try:
            id = int(input("ID: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        confirmacao = input(f"Deseja excluir a localização {id}? (s/N): ").strip()
        if confirmacao.lower() != "s":
            print("Exclusão cancelada.")
            return
        sucesso, erro = self.controller.excluir(id)
        if erro:
            print(f"Erro: {erro}")
        else:
            print("Localização excluída.")