import sqlite3
from Database.config import get_sqlite_connection, close_sqlite_connection
from flask import request, jsonify
from Cross.jwt_middleware import JWTMiddleware


class usuarios_repo:

    @staticmethod
    def get_db_connection():
        return get_sqlite_connection()


    @staticmethod
    def crear_user(nombre, correo, numero, tipo, password):
        conn = usuarios_repo.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO usuario (nombre, correo, numero, tipoUsuario, password)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nombre, correo, numero, tipo, password),
        )
        user_id = cursor.lastrowid
        conn.commit()
        new_user = cursor.execute(
            "SELECT Id, nombre, correo, numero, tipoUsuario FROM usuario WHERE Id = ?",
            (user_id,),
        ).fetchone()
        conn.close()
        return jsonify(dict(new_user)), 201

    @staticmethod
    def actualizar_user(id, nombre, correo, numero, tipo, password):  
        conn = usuarios_repo.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE usuario SET nombre = ?, correo = ?, numero = ?, tipoUsuario = ?, password = ?
            WHERE Id = ?
            """,
            (nombre, correo, numero, tipo, password, id),
        )
        updated = cursor.execute(
            "SELECT Id, nombre, correo, numero, tipoUsuario FROM usuario WHERE Id = ?",
            (id,),
        ).fetchone()
        conn.commit()
        conn.close()
        return jsonify(dict(updated)), 200

    @staticmethod
    def actualizar_contra(id, password):
        conn = usuarios_repo.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuario SET password = ? WHERE Id = ?", (password, id))
        conn.commit()
        user = cursor.execute("SELECT Id, nombre, correo, numero, tipoUsuario FROM usuario WHERE Id = ?",(id,),).fetchone()
        conn.close()
        return jsonify(dict(user)), 200

    @staticmethod
    def borrar_user(id):
        conn = usuarios_repo.get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute("SELECT Id, nombre, correo, numero, tipoUsuario FROM usuario WHERE Id = ?",(id,),).fetchone()
        user_dict = dict(user)
        cursor.execute("DELETE FROM usuario WHERE Id = ?", (id,))
        conn.commit()
        conn.close()

        return jsonify(user_dict), 200

    @staticmethod
    def Obtener_user(id):
        conn = usuarios_repo.get_db_connection()
        cursor = conn.cursor()
        usuario = cursor.execute("SELECT Id, nombre, correo, numero, tipoUsuario FROM usuario WHERE Id = ?",(id,),).fetchone()
        conn.close()
        return jsonify(dict(usuario)), 200
    
    @staticmethod
    def buscar_por_correo(correo):
        conn = usuarios_repo.get_db_connection()
        cursor = conn.cursor()
        usuario = cursor.execute(
            "SELECT Id, nombre, correo, numero, tipoUsuario, password FROM usuario WHERE correo = ?",
            (correo,)
        ).fetchone()
        conn.close()
        return dict(usuario) if usuario else None
     
  

    @staticmethod
    def buscar_delegado_por_id(delegado_id):
            conn = usuarios_repo.get_db_connection()
            row = conn.execute(
                "SELECT delegadoId FROM delegado WHERE delegadoId = ?", (delegado_id,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None

    @staticmethod
    def buscar_candidato_por_id(candidato_id):
            conn = usuarios_repo.get_db_connection()
            row = conn.execute(
                "SELECT candidatoId FROM candidato WHERE candidatoId = ?", (candidato_id,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None
