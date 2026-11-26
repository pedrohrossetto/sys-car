"""Tratamento de exceções na camada controller (ADR-003).

Os métodos de controller devolvem (resultado, None) quando dá certo e
(None, "mensagem") quando dá errado. As validações já seguem essa regra.
O decorador abaixo aplica a mesma regra às falhas do banco: um
ErroDeBanco vindo do model vira (None, "mensagem"), e a view mostra a
mensagem como mostra qualquer outro erro.
"""
import functools

from model.erros import ErroDeBanco


def devolve_erro(metodo):
    """Captura ErroDeBanco e devolve (None, mensagem) no lugar da exceção."""
    @functools.wraps(metodo)
    def envolvido(*args, **kwargs):
        try:
            return metodo(*args, **kwargs)
        except ErroDeBanco as erro:
            return None, str(erro)
    return envolvido
