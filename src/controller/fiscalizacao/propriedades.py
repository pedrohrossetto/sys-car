"""Acesso aos dados do cadastro, só pelo contrato combinado.

Usa apenas PropriedadeRural.buscar_por_id/listar_todos e os atributos
id, nome e proprietario_id. A tabela do cadastro nunca é alterada aqui.

A ficha da propriedade (issue #6) também lê o proprietário com
buscar_por_id(). A área da propriedade (ADR-C05) é lida pelas
propriedades area, centroide, area_ha e pelo método contem().
"""
from model.propriedade_rural import PropriedadeRural
from model.proprietario import Proprietario


def listar_propriedades():
    return PropriedadeRural.listar_todos()


def buscar_propriedade(propriedade_id):
    if propriedade_id is None:
        return None
    return PropriedadeRural.buscar_por_id(propriedade_id)


def nomes_das_propriedades():
    return {p.id: p.nome for p in listar_propriedades()}


def buscar_proprietario(proprietario_id):
    if proprietario_id is None:
        return None
    return Proprietario.buscar_por_id(proprietario_id)


def propriedade_no_ponto(latitude, longitude):
    """A propriedade cuja área contém o ponto, ou None (ADR-F14).

    As áreas não se sobrepõem (ADR-C05), então há no máximo uma.
    """
    for propriedade in listar_propriedades():
        if propriedade.contem(latitude, longitude):
            return propriedade
    return None


def listar_areas():
    """[(id, nome, Poligono)] das propriedades com área, para o mapa."""
    return [(p.id, p.nome, p.area) for p in listar_propriedades() if p.poligono]
