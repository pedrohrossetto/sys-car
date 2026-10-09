from database.database import init_db
from model.fiscalizacao import criar_tabelas


def preparar_banco():
    """Cria as tabelas do sistema e as da fiscalização.

    Depois da integração, init_db() já cria tudo e criar_tabelas() não
    muda nada (todos os comandos usam IF NOT EXISTS).
    """
    init_db()
    criar_tabelas()
