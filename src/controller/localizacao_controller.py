from model.localizacao import Localizacao
from model.propriedade_rural import PropriedadeRural


class LocalizacaoController:
    # Mesmo padrão (resultado, erro) dos outros controllers.
    def criar(self, propriedade_id, latitude=None, longitude=None,
              altitude=None, poligono_geometria=None):
        if not PropriedadeRural.buscar_por_id(propriedade_id):
            return None, "Propriedade não encontrada."
        # Relacionamento 1:1 - cada propriedade admite UMA localização.
        if Localizacao.buscar_por_propriedade(propriedade_id):
            return None, "Esta propriedade já possui uma localização."
        localizacao = Localizacao(
            propriedade_id, latitude, longitude, altitude, poligono_geometria
        )
        localizacao.salvar()
        return localizacao, None

    def buscar_por_id(self, id):
        return Localizacao.buscar_por_id(id)

    def buscar_por_propriedade(self, propriedade_id):
        return Localizacao.buscar_por_propriedade(propriedade_id)

    def atualizar(self, id, propriedade_id, latitude, longitude,
                  altitude, poligono_geometria):
        localizacao = Localizacao.buscar_por_id(id)
        if not localizacao:
            return None, "Localização não encontrada."
        if not PropriedadeRural.buscar_por_id(propriedade_id):
            return None, "Propriedade não encontrada."
        outra = Localizacao.buscar_por_propriedade(propriedade_id)
        if outra and outra.id != id:
            return None, "Esta propriedade já possui outra localização."
        localizacao.propriedade_id = propriedade_id
        localizacao.latitude = latitude
        localizacao.longitude = longitude
        localizacao.altitude = altitude
        localizacao.poligono_geometria = poligono_geometria
        localizacao.salvar()
        return localizacao, None

    def excluir(self, id):
        localizacao = Localizacao.buscar_por_id(id)
        if not localizacao:
            return None, "Localização não encontrada."
        localizacao.deletar()
        return True, None