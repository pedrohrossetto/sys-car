"""Fontes de detecção de desmatamento (padrão Factory Method).

FonteDeteccao declara o método fábrica criar_registro(). Satélite e
Usuário implementam esse método, cada um preenchendo a própria origem
no registro e aplicando a própria regra antes de criá-lo.
"""
from abc import ABC, abstractmethod


class FonteDeteccao(ABC):
    @abstractmethod
    def criar_registro(self, propriedade_id, descricao, latitude, longitude, data):
        """Método fábrica: devolve um RegistroDesmatamento novo (ainda não salvo)."""
