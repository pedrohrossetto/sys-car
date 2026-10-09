"""Models da Frente 2 (Fiscalização).

Cada módulo deste pacote declara a constante SCHEMA com as próprias
tabelas. Depois da integração, o init_db() do sistema encontra esses
SCHEMA sozinho. Antes disso (testes e _demo.py), criar_tabelas() faz
o mesmo trabalho só para este pacote.
"""
import importlib
import pkgutil


def criar_tabelas():
    """Executa o SCHEMA de todos os módulos deste pacote."""
    from database.database import get_connection

    conn = get_connection()
    try:
        for info in pkgutil.iter_modules(__path__):
            if info.name.startswith("_"):
                continue
            modulo = importlib.import_module(f"{__name__}.{info.name}")
            schema = getattr(modulo, "SCHEMA", None)
            if schema:
                conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()
