from database.database import get_connection


class Localizacao:
    def __init__(
        self, propriedade_id, latitude=None, longitude=None, altitude=None,
        poligono_geometria=None, id=None,
    ):
        self.id = id
        # Chave estrangeira: cada localização pertence a uma propriedade rural.
        self.propriedade_id = propriedade_id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.poligono_geometria = poligono_geometria

    def salvar(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO localizacoes (latitude, longitude, altitude, poligono_geometria, propriedade_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.latitude, self.longitude, self.altitude,
                 self.poligono_geometria, self.propriedade_id),
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE localizacoes SET latitude = ?, longitude = ?, altitude = ?, "
                "poligono_geometria = ?, propriedade_id = ? WHERE id = ?",
                (self.latitude, self.longitude, self.altitude,
                 self.poligono_geometria, self.propriedade_id, self.id),
            )
        conn.commit()
        conn.close()

    def deletar(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM localizacoes WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_id(id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, latitude, longitude, altitude, poligono_geometria, propriedade_id "
            "FROM localizacoes WHERE id = ?",
            (id,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return Localizacao(row[5], row[1], row[2], row[3], row[4], row[0])
        return None

    @staticmethod
    def buscar_por_propriedade(propriedade_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, latitude, longitude, altitude, poligono_geometria, propriedade_id "
            "FROM localizacoes WHERE propriedade_id = ?",
            (propriedade_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return Localizacao(row[5], row[1], row[2], row[3], row[4], row[0])
        return None

    @staticmethod
    def listar_todas():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, latitude, longitude, altitude, poligono_geometria, propriedade_id "
            "FROM localizacoes ORDER BY id"
        )
        rows = cursor.fetchall()
        conn.close()
        return [Localizacao(r[5], r[1], r[2], r[3], r[4], r[0]) for r in rows]