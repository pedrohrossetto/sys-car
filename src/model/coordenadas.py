"""Regras de coordenadas geográficas (latitude, longitude e polígono)."""


def converter_numero(valor, rotulo, minimo=None, maximo=None, obrigatorio=True):
    """Converte texto/número em float e confere a faixa.

    Aceita vírgula como separador decimal. Retorna None se o valor for
    vazio e não obrigatório. Lança ValueError com mensagem amigável.
    """
    if valor is None or str(valor).strip() == "":
        if obrigatorio:
            raise ValueError(f"{rotulo} é obrigatória.")
        return None
    try:
        numero = float(str(valor).strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"{rotulo} deve ser um número.") from None
    if minimo is not None and not (minimo <= numero <= maximo):
        raise ValueError(f"{rotulo} deve estar entre {minimo} e {maximo}.")
    return numero


def converter_latitude(valor):
    return converter_numero(valor, "Latitude", -90, 90)


def converter_longitude(valor):
    return converter_numero(valor, "Longitude", -180, 180)


def converter_poligono(texto):
    """Lê 'lat,lon; lat,lon; ...' e devolve a lista de pares (lat, lon).

    Retorna lista vazia se o texto for vazio. Exige no mínimo 3 vértices.
    """
    if texto is None or str(texto).strip() == "":
        return []
    pontos = []
    for numero, parte in enumerate(str(texto).split(";"), start=1):
        if not parte.strip():
            continue
        valores = parte.split(",")
        if len(valores) != 2:
            raise ValueError(
                f"Vértice {numero} do polígono deve ter o formato 'lat,lon'."
            )
        lat = converter_numero(valores[0], f"Latitude do vértice {numero}", -90, 90)
        lon = converter_numero(valores[1], f"Longitude do vértice {numero}", -180, 180)
        pontos.append((lat, lon))
    if len(pontos) < 3:
        raise ValueError("O polígono precisa de pelo menos 3 vértices.")
    return pontos


def formatar_poligono(pontos):
    """Transforma a lista de pares no texto normalizado 'lat,lon;lat,lon;...'."""
    return ";".join(f"{lat:g},{lon:g}" for lat, lon in pontos)
