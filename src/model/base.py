from database.database import get_connection


class ModeloBase:
    """Persistência genérica (padrão Template Method).

    Os métodos salvar/deletar/buscar_por_id/listar_todos definem o
    algoritmo fixo. Cada subclasse preenche as partes variáveis:
      - TABELA: nome da tabela;
      - COLUNAS: colunas além do id, na mesma ordem dos atributos;
      - _valores() e _de_linha(): ganchos de conversão objeto <-> linha.
    As buscas específicas usam os auxiliares _buscar_um(), _buscar_varios()
    e _existe(). _buscar_varios() aceita a ordem da listagem (padrão: id).
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
        conn = get_connection()
        try:
            if self.id is None:
                colunas = ", ".join(self.COLUNAS)
                marcadores = ", ".join("?" for _ in self.COLUNAS)
                cursor = conn.execute(
                    f"INSERT INTO {self.TABELA} ({colunas}) VALUES ({marcadores})",
                    self._valores(),
                )
                self.id = cursor.lastrowid
            else:
                atribuicoes = ", ".join(f"{c} = ?" for c in self.COLUNAS)
                conn.execute(
                    f"UPDATE {self.TABELA} SET {atribuicoes} WHERE id = ?",
                    self._valores() + (self.id,),
                )
            conn.commit()
        finally:
            conn.close()

    def deletar(self):
        conn = get_connection()
        try:
            conn.execute(f"DELETE FROM {self.TABELA} WHERE id = ?", (self.id,))
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def buscar_por_id(cls, id):
        return cls._buscar_um("id = ?", (id,))

    @classmethod
    def listar_todos(cls):
        return cls._buscar_varios("1 = 1", ())

    @classmethod
    def colunas_no_banco(cls):
        """Nomes das colunas que a tabela tem no banco (vazio se ela não existe)."""
        conn = get_connection()
        try:
            return [linha[1] for linha in conn.execute(f"PRAGMA table_info({cls.TABELA})")]
        finally:
            conn.close()

    @classmethod
    def _select(cls):
        colunas = ", ".join(("id",) + tuple(cls.COLUNAS))
        return f"SELECT {colunas} FROM {cls.TABELA}"

    @classmethod
    def _buscar_um(cls, condicao, parametros):
        conn = get_connection()
        try:
            linha = conn.execute(
                f"{cls._select()} WHERE {condicao}", parametros
            ).fetchone()
        finally:
            conn.close()
        return cls._de_linha(linha) if linha else None

    @classmethod
    def _buscar_varios(cls, condicao, parametros, ordem="id"):
        conn = get_connection()
        try:
            linhas = conn.execute(
                f"{cls._select()} WHERE {condicao} ORDER BY {ordem}", parametros
            ).fetchall()
        finally:
            conn.close()
        return [cls._de_linha(linha) for linha in linhas]

    @classmethod
    def _existe(cls, condicao, parametros):
        conn = get_connection()
        try:
            linha = conn.execute(
                f"SELECT 1 FROM {cls.TABELA} WHERE {condicao} LIMIT 1", parametros
            ).fetchone()
        finally:
            conn.close()
        return linha is not None
