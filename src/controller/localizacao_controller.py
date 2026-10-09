from model.coordenadas import (
    converter_latitude, converter_longitude, converter_numero,
    converter_poligono, formatar_poligono,
)
from model.localizacao import Localizacao
from model.propriedade_rural import PropriedadeRural


class LocalizacaoController:
    # Mesmo padrão (resultado, erro) dos outros controllers.
    def criar(self, propriedade_id, latitude, longitude, altitude=None,
              poligono_geometria=None):
        dados, erro = self._validar(
            propriedade_id, latitude, longitude, altitude, poligono_geometria
        )
        if erro:
            return None, erro
        # Relacionamento 1:1 - cada propriedade admite UMA localização.
        if Localizacao.buscar_por_propriedade(dados["propriedade_id"]):
            return None, "Esta propriedade já possui uma localização."
        localizacao = Localizacao(**dados)
        localizacao.salvar()
        return localizacao, None

    def buscar_por_id(self, id):
        return Localizacao.buscar_por_id(id)

    def buscar_por_propriedade(self, propriedade_id):
        return Localizacao.buscar_por_propriedade(propriedade_id)

    def listar(self):
        return Localizacao.listar_todas()

    def atualizar(self, id, propriedade_id, latitude, longitude, altitude=None,
                  poligono_geometria=None):
        localizacao = Localizacao.buscar_por_id(id)
        if not localizacao:
            return None, "Localização não encontrada."
        dados, erro = self._validar(
            propriedade_id, latitude, longitude, altitude, poligono_geometria
        )
        if erro:
            return None, erro
        outra = Localizacao.buscar_por_propriedade(dados["propriedade_id"])
        if outra and outra.id != localizacao.id:
            return None, "Esta propriedade já possui outra localização."
        for campo, valor in dados.items():
            setattr(localizacao, campo, valor)
        localizacao.salvar()
        return localizacao, None

    def excluir(self, id):
        localizacao = Localizacao.buscar_por_id(id)
        if not localizacao:
            return None, "Localização não encontrada."
        localizacao.deletar()
        return True, None

    def _validar(self, propriedade_id, latitude, longitude, altitude, poligono):
        if propriedade_id is None or not PropriedadeRural.buscar_por_id(propriedade_id):
            return None, "Propriedade não encontrada."
        try:
            pontos = converter_poligono(poligono)
            dados = {
                "propriedade_id": int(propriedade_id),
                "latitude": converter_latitude(latitude),
                "longitude": converter_longitude(longitude),
                "altitude": converter_numero(altitude, "Altitude", obrigatorio=False),
                "poligono_geometria": formatar_poligono(pontos) if pontos else None,
            }
        except ValueError as erro:
            return None, str(erro)
        return dados, None
