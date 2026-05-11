from Database.config import get_sqlite_connection

class postulacion_repo:

    @staticmethod
    def get_db_connection():
        return get_sqlite_connection()

    @staticmethod
    def buscar_por_id(postulacion_id):
        conn = postulacion_repo.get_db_connection()
        row = conn.execute(
            "SELECT * FROM postulacion WHERE postulacionId = ?", (postulacion_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def buscar_por_oferta(oferta_id):
        conn = postulacion_repo.get_db_connection()
        rows = conn.execute(
                '''
                SELECT usuario.nombre, candidato.profesion, oferta.titulo
                FROM usuario
                JOIN candidato ON usuario.Id = candidato.Id
                JOIN postulacion ON candidato.candidatoId = postulacion.candidatoId
                JOIN oferta ON postulacion.ofertaId = oferta.ofertaId
                WHERE oferta.ofertaId = ?
                ''', (oferta_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def buscar_por_candidato_y_oferta(candidato_id, oferta_id):
        conn = postulacion_repo.get_db_connection()
        row = conn.execute(
            "SELECT postulacionId FROM postulacion WHERE candidatoId = ? AND ofertaId = ?",
            (candidato_id, oferta_id)
        ).fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def insertar(candidato_id, oferta_id):
        conn = postulacion_repo.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO postulacion (candidatoId, ofertaId, estadoPostulacion)
            VALUES (?, ?, 2)
        """, (candidato_id, oferta_id))
        postulacion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return postulacion_id

    @staticmethod
    def actualizar_estado(postulacion_id, estado):
        conn = postulacion_repo.get_db_connection()
        conn.execute(
            "UPDATE postulacion SET estadoPostulacion = ? WHERE postulacionId = ?",
            (estado, postulacion_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(postulacion_id):
        conn = postulacion_repo.get_db_connection()
        conn.execute(
            "DELETE FROM postulacion WHERE postulacionId = ?", (postulacion_id,)
        )
        conn.commit()
        conn.close()