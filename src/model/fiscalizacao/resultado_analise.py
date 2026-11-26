"""Resultado da análise de conformidade (padrão Factory Method, ADR-F11).

ResultadoAnalise declara o método fábrica criar_declaracao(). Cada
resultado concreto decide qual declaração nasce dele:

    SemPendencias  --> Declaracao EMITIDA
    ComPendencias  --> Declaracao NEGADA, com as pendências no motivo

O controller só chama analisar(impedimentos).criar_declaracao(...) e não
precisa de if/else. Um resultado novo (por exemplo, "emitida com
ressalvas") é uma subclasse nova.
"""
from abc import ABC, abstractmethod

from model.fiscalizacao.declaracao import Declaracao


class ResultadoAnalise(ABC):
    @abstractmethod
    def criar_declaracao(self, propriedade_id, data):
        """Método fábrica: devolve uma Declaracao nova (ainda não salva)."""


class SemPendencias(ResultadoAnalise):
    def criar_declaracao(self, propriedade_id, data):
        return Declaracao(propriedade_id, data, "EMITIDA")


class ComPendencias(ResultadoAnalise):
    def __init__(self, impedimentos):
        if not impedimentos:
            raise ValueError("ComPendencias exige pelo menos um impedimento.")
        self.impedimentos = list(impedimentos)

    def criar_declaracao(self, propriedade_id, data):
        motivo = "Pendências: " + ", ".join(self.impedimentos) + "."
        return Declaracao(propriedade_id, data, "NEGADA", motivo)


def analisar(impedimentos):
    """Escolhe o resultado concreto a partir da lista de impedimentos."""
    return ComPendencias(impedimentos) if impedimentos else SemPendencias()
