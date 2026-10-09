"""Validação de CPF e CNPJ (padrão Strategy).

Cada estratégia sabe normalizar e validar um tipo de documento.
O controller escolhe a estratégia pelo tipo de pessoa (PF ou PJ)
através do dicionário VALIDADORES, sem if/elif.
"""
import re
from abc import ABC, abstractmethod


class ValidadorDocumento(ABC):
    nome = ""

    @abstractmethod
    def normalizar(self, texto):
        """Remove a máscara e devolve só os caracteres que contam."""

    @abstractmethod
    def valido(self, documento):
        """Recebe o documento já normalizado e diz se ele é válido."""


class ValidadorCPF(ValidadorDocumento):
    nome = "CPF"

    def normalizar(self, texto):
        return re.sub(r"\D", "", texto or "")

    def valido(self, documento):
        if len(documento) != 11 or not documento.isdigit():
            return False
        if documento == documento[0] * 11:
            return False
        for tamanho in (9, 10):
            soma = sum(
                int(documento[i]) * (tamanho + 1 - i) for i in range(tamanho)
            )
            digito = (soma * 10) % 11 % 10
            if digito != int(documento[tamanho]):
                return False
        return True


class ValidadorCNPJ(ValidadorDocumento):
    """Aceita o CNPJ numérico e o alfanumérico (Receita Federal, a partir de 2026).

    No cálculo do dígito verificador, cada caractere vale ord(c) - 48:
    os dígitos continuam valendo 0..9 e as letras A..Z valem 17..42.
    """

    nome = "CNPJ"
    PESOS_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    PESOS_2 = (6,) + PESOS_1

    def normalizar(self, texto):
        return re.sub(r"[^0-9A-Za-z]", "", texto or "").upper()

    def valido(self, documento):
        if not re.fullmatch(r"[0-9A-Z]{12}[0-9]{2}", documento):
            return False
        if documento == documento[0] * 14:
            return False
        for pesos in (self.PESOS_1, self.PESOS_2):
            soma = sum((ord(documento[i]) - 48) * peso for i, peso in enumerate(pesos))
            resto = soma % 11
            digito = 0 if resto < 2 else 11 - resto
            if digito != int(documento[len(pesos)]):
                return False
        return True


VALIDADORES = {"PF": ValidadorCPF(), "PJ": ValidadorCNPJ()}
