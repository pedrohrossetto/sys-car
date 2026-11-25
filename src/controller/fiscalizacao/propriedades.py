"""Acesso aos dados do cadastro, só pelo contrato combinado.

Usa apenas PropriedadeRural.buscar_por_id/listar_todos e os atributos
id, nome e proprietario_id. A tabela do cadastro nunca é alterada aqui.

A ficha da propriedade (issue #6) também lê o proprietário e a
localização, só com buscar_por_id() e buscar_por_propriedade().
"""
from model.localizacao import Localizacao
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


def buscar_localizacao(propriedade_id):
    return Localizacao.buscar_por_propriedade(propriedade_id)
