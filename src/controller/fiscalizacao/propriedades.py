"""Acesso às propriedades rurais do cadastro, só pelo contrato combinado.

Usa apenas PropriedadeRural.buscar_por_id/listar_todos e os atributos
id, nome e proprietario_id. A tabela do cadastro nunca é alterada aqui.
"""
from model.propriedade_rural import PropriedadeRural


def listar_propriedades():
    return PropriedadeRural.listar_todos()


def buscar_propriedade(propriedade_id):
    if propriedade_id is None:
        return None
    return PropriedadeRural.buscar_por_id(propriedade_id)


def nomes_das_propriedades():
    return {p.id: p.nome for p in listar_propriedades()}
