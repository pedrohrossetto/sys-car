from database.database import get_connection


class PropriedadeRural:
    def __init__(self, nome, proprietario_id, cadastro_publico=None, id=None):
        self.id = id
        self.nome = nome
        self.cadastro_publico = cadastro_publico
        # Chave estrangeira: aponta para o proprietário dono desta propriedade.
        self.proprietario_id = proprietario_id

    def salvar(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO propriedades_rurais (nome, cadastro_publico, proprietario_id) "
                "VALUES (?, ?, ?)",
                (self.nome, self.cadastro_publico, self.proprietario_id),
            )
            # lastrowid: id gerado pelo SQLite no INSERT (usado no cadastro novo).
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE propriedades_rurais SET nome = ?, cadastro_publico = ?, proprietario_id = ? "
                "WHERE id = ?",
                (self.nome, self.cadastro_publico, self.proprietario_id, self.id),
            )
        conn.commit()
        conn.close()

    def deletar(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM propriedades_rurais WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_id(id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, cadastro_publico, proprietario_id FROM propriedades_rurais "
            "WHERE id = ?",
            (id,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            # Linha do banco vira objeto: (nome, proprietario_id, cadastro_publico, id).
            return PropriedadeRural(row[1], row[3], row[2], row[0])
        return None

    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, cadastro_publico, proprietario_id "
            "FROM propriedades_rurais ORDER BY id"
        )
        rows = cursor.fetchall()
        conn.close()
        return [PropriedadeRural(r[1], r[3], r[2], r[0]) for r in rows]