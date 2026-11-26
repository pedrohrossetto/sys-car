"""Exceções próprias do model (estratégia de exceções: ADR-003).

Regra do sistema:
  - a exceção NASCE no model (validação ou banco);
  - o controller CAPTURA e devolve (None, "mensagem");
  - a view MOSTRA a mensagem ao usuário.

ErroDeBanco esconde o sqlite3.Error das outras camadas. O controller e a
view não importam sqlite3: eles só conhecem esta exceção. A exceção
original continua disponível em __cause__ (raise ... from erro).
"""
import sqlite3

# Trecho da mensagem do SQLite -> texto para o usuário.
_RESTRICOES = (
    ("UNIQUE", "Já existe um registro com este valor."),
    ("FOREIGN KEY", "O registro está ligado a outro registro que não existe ou que ainda o usa."),
    ("CHECK", "Um dos valores não é aceito pelo banco de dados."),
    ("NOT NULL", "Um campo obrigatório ficou vazio."),
)


class ErroDeBanco(Exception):
    """Falha do banco de dados, com mensagem pronta para a tela."""

    @classmethod
    def de(cls, erro):
        """Cria um ErroDeBanco a partir de um sqlite3.Error."""
        texto = str(erro)
        if isinstance(erro, sqlite3.IntegrityError):
            for trecho, mensagem in _RESTRICOES:
                if trecho in texto:
                    return cls(mensagem)
            return cls("Os dados violam uma regra do banco de dados.")
        return cls(f"Não foi possível acessar o banco de dados ({texto}).")
