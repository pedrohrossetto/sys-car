"""Descoberta automática de módulos (contrato de plugin).

Percorre um pacote recursivamente e importa os módulos encontrados.
Módulos ou pacotes cujo nome começa com "_" são ignorados, o que
permite ter scripts auxiliares (ex.: _demo.py) sem que sejam carregados.
"""
import importlib
import pkgutil


def modulos_publicos(pacote):
    """Importa e retorna os módulos do pacote (recursivo), ignorando nomes com '_'."""
    modulos = []
    for info in pkgutil.walk_packages(pacote.__path__, pacote.__name__ + "."):
        partes = info.name.split(".")
        if any(parte.startswith("_") for parte in partes):
            continue
        modulos.append(importlib.import_module(info.name))
    return modulos


def modulos_com(pacote, atributo):
    """Retorna os módulos do pacote que definem o atributo informado."""
    return [m for m in modulos_publicos(pacote) if hasattr(m, atributo)]


def ordenar_por_ordem(modulos):
    """Ordena pela constante ORDEM (padrão 100) e, no empate, pelo nome do módulo."""
    return sorted(modulos, key=lambda m: (getattr(m, "ORDEM", 100), m.__name__))
