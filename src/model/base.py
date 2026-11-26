import sqlite3
from contextlib import contextmanager

from database.database import get_connection
from model.erros import ErroDeBanco


@contextmanager
def _conexao():
    """Abre a conexão, converte sqlite3.Error em ErroDeBanco e sempre fecha.

    Este é o único ponto do sistema que trata erros do banco (ADR-003).
    Sem commit, o SQLite desfaz a operação que falhou.
    """
    conn = get_connection()
    try:
        yield conn
    except sqlite3.Error as erro:
        raise ErroDeBanco.de(erro) from erro
    finally:
        conn.close()


class ModeloBase:
    """Persistência genérica (padrão Template Method).

    Os métodos salvar/deletar/buscar_por_id/listar_todos definem o
    algoritmo fixo. Cada subclasse preenche as partes variáveis:
      - TABELA: nome da tabela;
      - COLUNAS: colunas além do id, na mesma ordem dos atributos;
      - _valores() e _de_linha(): ganchos de conversão objeto <-> linha.
    As buscas específicas usam os auxiliares _buscar_um(), _buscar_varios()
    e _existe(). _buscar_varios() aceita a ordem da listagem (padrão: id).
    Toda falha do banco sai como ErroDeBanco (model/erros.py).
    colunas_no_banco() ajuda a detectar um banco de versão antiga.
    O construtor da subclasse precisa aceitar as COLUNAS e 'id' como
    argumentos nomeados.
    """

    TABELA = ""
    COLUNAS = ()

    # ---- ganchos (podem ser sobrescritos) ----
    def _valores(self):
        return tuple(getattr(self, coluna) for coluna in self.COLUNAS)

    @classmethod
    def _de_linha(cls, linha):
        dados = dict(zip(("id",) + tuple(cls.COLUNAS), linha))
        return cls(**dados)

    # ---- algoritmo fixo ----
    def salvar(self):
        with _conexao() as conn:
            if self.id is None:
                colunas = ", ".join(self.COLUNAS)
                marcadores = ", ".join("?" for _ in self.COLUNAS)
                cursor = conn.execute(
                    f"INSERT INTO {self.TABELA} ({colunas}) VALUES ({marcadores})",
                    self._valores(),
                )
                conn.commit()
                # O id só é guardado depois do commit: se o INSERT falha, o objeto continua novo.
                self.id = cursor.lastrowid
            else:
                atribuicoes = ", ".join(f"{c} = ?" for c in self.COLUNAS)
                conn.execute(
                    f"UPDATE {self.TABELA} SET {atribuicoes} WHERE id = ?",
                    self._valores() + (self.id,),
                )
                conn.commit()

    def deletar(self):
        with _conexao() as conn:
            conn.execute(f"DELETE FROM {self.TABELA} WHERE id = ?", (self.id,))
            conn.commit()

    @classmethod
    def buscar_por_id(cls, id):
        return cls._buscar_um("id = ?", (id,))

    @classmethod
    def listar_todos(cls):
        return cls._buscar_varios("1 = 1", ())

    @classmethod
    def colunas_no_banco(cls):
        """Nomes das colunas que a tabela tem no banco (vazio se ela não existe)."""
        with _conexao() as conn:
            return [linha[1] for linha in conn.execute(f"PRAGMA table_info({cls.TABELA})")]

    @classmethod
    def _select(cls):
        colunas = ", ".join(("id",) + tuple(cls.COLUNAS))
        return f"SELECT {colunas} FROM {cls.TABELA}"

    @classmethod
    def _buscar_um(cls, condicao, parametros):
        with _conexao() as conn:
            linha = conn.execute(
                f"{cls._select()} WHERE {condicao}", parametros
            ).fetchone()
        return cls._de_linha(linha) if linha else None

    @classmethod
    def _buscar_varios(cls, condicao, parametros, ordem="id"):
        with _conexao() as conn:
            linhas = conn.execute(
                f"{cls._select()} WHERE {condicao} ORDER BY {ordem}", parametros
            ).fetchall()
        return [cls._de_linha(linha) for linha in linhas]

    @classmethod
    def _existe(cls, condicao, parametros):
        with _conexao() as conn:
            linha = conn.execute(
                f"SELECT 1 FROM {cls.TABELA} WHERE {condicao} LIMIT 1", parametros
            ).fetchone()
        return linha is not None
