"""Ficha da propriedade: todos os dados ligados a uma propriedade (aula 11).

Junta numa consulta só os relacionamentos do sistema:
  - propriedade -> proprietário (N:1) e localização (1:1), do Cadastro;
  - propriedade -> alertas, embargos e declarações (1:N), da Fiscalização.
A view recebe uma FichaPropriedade pronta e não acessa nenhum model.
"""
from dataclasses import dataclass, field

from controller.fiscalizacao.propriedades import (
    buscar_localizacao, buscar_propriedade, buscar_proprietario, listar_propriedades,
)
from model.fiscalizacao.declaracao import Declaracao
from model.fiscalizacao.embargo import Embargo
from model.fiscalizacao.registro_desmatamento import RegistroDesmatamento
from model.fiscalizacao.satelite import Satelite
from model.fiscalizacao.unidade_competente import UnidadeCompetente
from model.fiscalizacao.usuario import Usuario

EMBARGADA = "EMBARGADA"
COM_ALERTAS = "COM ALERTAS EM ABERTO"
REGULAR = "REGULAR"


@dataclass
class FichaPropriedade:
    propriedade: object
    proprietario: object = None        # None se o proprietário não existe mais
    localizacao: object = None         # None se a localização não foi cadastrada
    alertas: list = field(default_factory=list)
    embargo_ativo: object = None
    unidade_do_embargo: object = None
    declaracoes: list = field(default_factory=list)

    @property
    def alertas_em_aberto(self):
        """Alertas cujo status impede a declaração de conformidade (State)."""
        return [a for a in self.alertas if a.estado.BLOQUEIA_CONFORMIDADE]

    @property
    def situacao(self):
        if self.embargo_ativo is not None:
            return EMBARGADA
        if self.alertas_em_aberto:
            return COM_ALERTAS
        return REGULAR


class FichaController:
    def listar_propriedades(self):
        return listar_propriedades()

    def montar(self, propriedade_id):
        """Devolve (FichaPropriedade, None) ou (None, "mensagem")."""
        propriedade = buscar_propriedade(propriedade_id)
        if not propriedade:
            return None, "Propriedade não encontrada."
        embargo = Embargo.buscar_ativo(propriedade.id)
        ficha = FichaPropriedade(
            propriedade=propriedade,
            proprietario=buscar_proprietario(propriedade.proprietario_id),
            localizacao=buscar_localizacao(propriedade.id),
            alertas=RegistroDesmatamento.listar_por_propriedade(propriedade.id),
            embargo_ativo=embargo,
            unidade_do_embargo=UnidadeCompetente.buscar_por_id(embargo.unidade_id) if embargo else None,
            declaracoes=Declaracao.listar_por_propriedade(propriedade.id),
        )
        return ficha, None

    def descrever_origem(self, alerta):
        """Texto curto com a fonte do alerta: satélite ou usuário denunciante."""
        if alerta.satelite_id is not None:
            satelite = Satelite.buscar_por_id(alerta.satelite_id)
            return f"Satélite: {satelite.nome if satelite else alerta.satelite_id}"
        usuario = Usuario.buscar_por_id(alerta.usuario_id)
        return f"Usuário: {usuario.nome if usuario else alerta.usuario_id}"
