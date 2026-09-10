from database.database import get_connection


class Proprietario:
    def __init__(self, nome, cpf, cnpj=None, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.cnpj = cnpj

    def salvar(self):
        conn = get_connection()
        # cursor: objeto do sqlite3 que executa o SQL. Ele também guarda,
        # em cursor.lastrowid, o id gerado automaticamente pelo INSERT.
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO proprietarios (nome, cpf, cnpj) VALUES (?, ?, ?)",
                (self.nome, self.cpf, self.cnpj),
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE proprietarios SET nome = ?, cpf = ?, cnpj = ? WHERE id = ?",
                (self.nome, self.cpf, self.cnpj, self.id),
            )
        conn.commit()
        conn.close()

    def deletar(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proprietarios WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_id(id):
        conn = get_connection()
        cursor = conn.cursor()
        # O '?' evita SQL injection: o valor é passado separadamente.
        cursor.execute(
            "SELECT id, nome, cpf, cnpj FROM proprietarios WHERE id = ?", (id,)
        )
        # fetchone() retorna UMA linha (tupla) do resultado, ou None se nada veio.
        row = cursor.fetchone()
        conn.close()
        if row:
            # Monta o objeto Python a partir da linha: (nome, cpf, cnpj, id).
            return Proprietario(row[1], row[2], row[3], row[0])
        return None

    @staticmethod
    def buscar_por_cpf(cpf):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, cpf, cnpj FROM proprietarios WHERE cpf = ?", (cpf,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return Proprietario(row[1], row[2], row[3], row[0])
        return None

    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf, cnpj FROM proprietarios ORDER BY id")
        # fetchall() retorna TODAS as linhas da consulta, numa lista de tuplas.
        rows = cursor.fetchall()
        conn.close()
        # Converte cada tupla do banco em um objeto Proprietario.
        return [Proprietario(r[1], r[2], r[3], r[0]) for r in rows]
