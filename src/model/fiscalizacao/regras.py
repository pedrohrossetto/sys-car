"""Regras de validação usadas pelos controllers da fiscalização."""
from datetime import date


def texto_obrigatorio(valor, rotulo):
    texto = (valor or "").strip()
    if not texto:
        raise ValueError(f"Preencha o campo {rotulo}.")
    return texto


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
