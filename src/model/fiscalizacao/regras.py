"""Regras de validação usadas pelos controllers da fiscalização."""
import re
from datetime import date


def texto_obrigatorio(valor, rotulo):
    texto = (valor or "").strip()
    if not texto:
        raise ValueError(f"Preencha o campo {rotulo}.")
    return texto


def normalizar_cpf(texto):
    """Remove pontos, hífens e espaços do CPF."""
    return re.sub(r"\D", "", texto or "")


def cpf_formato_valido(cpf):
    """Confere só o formato: 11 dígitos. O dígito verificador não é conferido (ADR-F05)."""
    return len(cpf) == 11 and cpf.isdigit()


def email_valido(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", (email or "").strip()) is not None


def converter_coordenada(valor, rotulo, limite):
    """Converte latitude/longitude (aceita vírgula decimal) e confere a faixa [-limite, limite]."""
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"{rotulo} é obrigatória.")
    try:
        numero = float(str(valor).strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"{rotulo} deve ser um número.") from None
    if not -limite <= numero <= limite:
        raise ValueError(f"{rotulo} deve estar entre {-limite} e {limite}.")
    return numero


def data_iso(valor=None):
    """Devolve a data no formato AAAA-MM-DD. Vazio = hoje."""
    if valor is None or str(valor).strip() == "":
        return date.today().isoformat()
    try:
        return date.fromisoformat(str(valor).strip()).isoformat()
    except ValueError:
        raise ValueError("Data deve estar no formato AAAA-MM-DD.") from None
