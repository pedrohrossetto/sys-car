"""Padrão Observer: quem quer saber dos alertas se inscreve no publicador."""
from abc import ABC, abstractmethod


class ObservadorAlerta(ABC):
    @abstractmethod
    def atualizar(self, registro, evento):
        """Chamado quando um alerta é criado ou muda de status."""


class PublicadorAlertas:
    def __init__(self):
        self._observadores = []

    def inscrever(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cancelar_inscricao(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, registro, evento):
        for observador in list(self._observadores):
            observador.atualizar(registro, evento)
