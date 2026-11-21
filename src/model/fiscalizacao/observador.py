"""Padrão Observer: quem quer saber dos alertas se inscreve no publicador."""
from abc import ABC, abstractmethod


class ObservadorAlerta(ABC):
    @abstractmethod
    def atualizar(self, registro, evento):
        """Chamado quando um alerta é criado ou muda de status."""


class PublicadorAlertas:
    """Guarda os observadores e repassa a eles cada evento de alerta.

    Singleton: o sistema usa uma única instância, obtida por
    ``PublicadorAlertas.instancia()``. O construtor continua público
    para que os testes possam criar publicadores isolados (ver ADR-F08).
    """

    _instancia = None

    def __init__(self):
        self._observadores = []

    @classmethod
    def instancia(cls):
        """Devolve o publicador único do sistema, criando-o na primeira chamada."""
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def inscrever(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cancelar_inscricao(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, registro, evento):
        for observador in list(self._observadores):
            observador.atualizar(registro, evento)
