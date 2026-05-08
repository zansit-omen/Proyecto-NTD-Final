from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from flask import request, jsonify
import sqlite3


class chat_repositorio:
    """Repository for chat-related database operations."""

    DATABASE = "ProLink.db"
    MONGO_URI = "mongodb+srv://Admin:ProLink123@prolink.bcknvo4.mongodb.net/chats_db?appName=ProLink"

    @staticmethod
    def get_db_connection():
        """Establish connection to SQLite database."""
        conn = sqlite3.connect(chat_repositorio.DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def get_mongo_db():
        """Get MongoDB connection and chats collection."""
        client = MongoClient(chat_repositorio.MONGO_URI)
        db = client["chats_db"]
        return db["chats"]

    @staticmethod
    def ver_chats(idU):
        """Retrieve all chats for a user."""
        conn = chat_repositorio.get_db_connection()
        cursor = conn.cursor()

        nombreU = cursor.execute(
            "SELECT nombre FROM usuario WHERE Id = ?", (idU,)
        ).fetchone()
        if not nombreU:
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        chats = chat_repositorio.obtener_chats_usuario(idU)

        if not chats:
            conn.close()
            return jsonify({"error": "El usuario no tiene chats"}), 404

        resultado = []
        for chat in chats:
            candidatoId = chat.get("id_candidato")
            delegadoId = chat.get("id_delegado")

            nombreDelegado = cursor.execute(
                """
                SELECT usuario.nombre FROM usuario 
                JOIN delegado ON usuario.Id = delegado.Id 
                WHERE delegado.delegadoId = ?
                """,
                (delegadoId,),
            ).fetchone()

            nombreCandidato = cursor.execute(
                """
                SELECT usuario.nombre FROM usuario 
                JOIN candidato ON usuario.Id = candidato.Id 
                WHERE candidato.candidatoId = ?
                """,
                (candidatoId,),
            ).fetchone()

            mensajes = chat.get("mensajes", [])
            fecha = None
            for mensaje in mensajes:
                fecha1 = datetime.strptime(
                    mensaje.get("timestamp"), "%Y-%m-%dT%H:%M:%S"
                )
                if fecha1 > fecha or fecha is None:
                    fecha = fecha1

            resultado.append(
                {
                    "id_chat": chat.get("id_chat"),
                    "delegado": nombreDelegado[0] if nombreDelegado else None,
                    "candidato": nombreCandidato[0] if nombreCandidato else None,
                    "fecha": fecha.isoformat() if fecha else None,
                }
            )

        conn.close()
        return jsonify(resultado), 200

    @staticmethod
    def obtener_chats(idU, idChat):
        """Retrieve a specific chat."""
        conn = chat_repositorio.get_db_connection()
        cursor = conn.cursor()

        chats = chat_repositorio.obtener_chats_usuario(idU)
        if not chats:
            conn.close()
            return jsonify({"Error": "El usuario no tiene chats"}), 404

        chatMongo = chat_repositorio.ver_chat(idChat)
        if not chatMongo:
            conn.close()
            return jsonify({"Error": "No existe dicho chat"}), 404

        idChatB = chatMongo.get("id_chat")

        chatB = None
        for n in range(len(chats)):
            if chats[n].get("id_chat") == idChatB:
                chatB = chats[n]
                break

        if not chatB:
            conn.close()
            return jsonify({"Error": "El chat no pertenece a este usuario"}), 404

        nombreCandidato = cursor.execute(
            """
            SELECT usuario.nombre FROM usuario 
            JOIN candidato ON usuario.Id = candidato.Id 
            WHERE candidato.candidatoId = ?
            """,
            (chatB.get("id_candidato"),),
        ).fetchone()

        nombreDelegado = cursor.execute(
            """
            SELECT usuario.nombre FROM usuario 
            JOIN delegado ON usuario.Id = delegado.Id 
            WHERE delegado.delegadoId = ?
            """,
            (chatB.get("id_delegado"),),
        ).fetchone()

        mensajes = chatB.get("mensajes", [])
        conn.close()

        if not mensajes:
            return (
                jsonify(
                    {
                        "Candidato": nombreCandidato[0] if nombreCandidato else None,
                        "Delegado": nombreDelegado[0] if nombreDelegado else None,
                        "Mensajes": "No hay mensajes en este chat aun",
                    }
                ),
                200,
            )

        infoMensaje = []
        for mensaje in mensajes:
            idEmisor = mensaje.get("id_emisor")
            nombreEmisor = (
                nombreCandidato[0]
                if idEmisor == chatB.get("id_candidato")
                else nombreDelegado[0]
            )
            timestamp = mensaje.get("timestamp")
            fecha = (
                datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
                if timestamp
                else None
            )

            infoMensaje.append(
                {
                    "Enviado por": nombreEmisor,
                    "Fecha": fecha.isoformat() if fecha else None,
                    "Contenido": mensaje.get("contenido"),
                }
            )

        return (
            jsonify(
                {
                    "Candidato": nombreCandidato[0] if nombreCandidato else None,
                    "Delegado": nombreDelegado[0] if nombreDelegado else None,
                    "Mensajes": infoMensaje,
                }
            ),
            200,
        )

    @staticmethod
    def editar_mensaje(idU, idChat, idMensaje):
        """Edit a message in a chat."""
        chatss = chat_repositorio.obtener_chats_usuario(idU)
        if not chatss:
            return jsonify({"Error": "El usuario no tiene chats activos"}), 404

        chat = None
        for c in chatss:
            if c.get("id_chat") == idChat:
                chat = c
                break

        if not chat:
            return jsonify({"Error": "No se encontro el chat"}), 404

        contenido = request.get_json()
        if not contenido:
            return jsonify({"Error": "No se encontro el contenido"}), 400

        mensaje = None
        for m in chat.get("mensajes", []):
            if m.get("id_mensaje") == idMensaje:
                mensaje = m
                break

        if not mensaje:
            return jsonify({"Error": "No se encontro el mensaje"}), 404

        if mensaje.get("id_emisor") != idU:
            return jsonify(
                {
                    "Error": "No se puede editar el mensaje porque no lo envio usted"
                }
            ), 403

        mensaje["contenido"] = contenido.get("contenido")
        chats_collection = chat_repositorio.get_mongo_db()
        chats_collection.update_one(
            {"id_chat": idChat, "mensajes.id_mensaje": idMensaje},
            {"$set": {"mensajes.$.contenido": mensaje["contenido"]}},
        )

        return jsonify({"Contenido": mensaje.get("contenido")}), 200

    @staticmethod
    def enviar_mensaje_chat(id_chat):
        """Send a message to a chat."""
        data = request.get_json()

        id_usuario = data.get("id_usuario")
        mensaje_texto = data.get("mensaje")

        if not id_usuario or not mensaje_texto:
            return (
                jsonify(
                    {
                        "error": "Datos incompletos. Requiere: id_usuario, mensaje"
                    }
                ),
                400,
            )

        # Validate chat exists
        chat = chat_repositorio.ver_chat(id_chat)
        if not chat:
            return jsonify({"error": "Chat no encontrado"}), 404

        # Validate user belongs to chat
        if (
            id_usuario != chat.get("id_delegado")
            and id_usuario != chat.get("id_candidato")
        ):
            return (
                jsonify(
                    {
                        "error": "El usuario no tiene permiso para enviar mensajes en este chat"
                    }
                ),
                403,
            )

        # Send message
        resultado = chat_repositorio.enviar_mensaje(id_chat, id_usuario, mensaje_texto)

        if not resultado:
            return jsonify({"error": "Error al enviar el mensaje"}), 500

        # Get updated chat
        chat_actualizado = chat_repositorio.ver_chat(id_chat)

        return (
            jsonify(
                {
                    "message": "Mensaje enviado exitosamente",
                    "chat": chat_actualizado,
                }
            ),
            201,
        )

    @staticmethod
    def crear_chat(idU):
        """Create a new chat between a delegate and candidate."""
        conn = chat_repositorio.get_db_connection()
        cursor = conn.cursor()

        # Validate user exists
        nombreU = cursor.execute(
            "SELECT nombre FROM usuario WHERE Id = ?", (idU,)
        ).fetchone()
        if not nombreU:
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        data = request.get_json()

        id_delegado = data.get("id_delegado")
        id_candidato = data.get("id_candidato")
        mensaje_texto = data.get("mensaje")

        # Validate all data present
        if not all([id_delegado, id_candidato, mensaje_texto]):
            conn.close()
            return (
                jsonify(
                    {
                        "error": "Datos incompletos. Requiere: id_delegado, id_candidato, mensaje"
                    }
                ),
                400,
            )

        # Validate user is involved in chat
        if idU != id_delegado and idU != id_candidato:
            conn.close()
            return (
                jsonify({"error": "El usuario no está involucrado en este chat"}),
                403,
            )

        # Validate delegate exists
        delegado = cursor.execute(
            "SELECT delegadoId FROM delegado WHERE delegadoId = ?", (id_delegado,)
        ).fetchone()
        if not delegado:
            conn.close()
            return jsonify({"error": "Delegado no encontrado"}), 404

        # Validate candidate exists
        candidato = cursor.execute(
            "SELECT candidatoId FROM candidato WHERE candidatoId = ?", (id_candidato,)
        ).fetchone()
        if not candidato:
            conn.close()
            return jsonify({"error": "Candidato no encontrado"}), 404

        conn.close()

        # Create chat with first message
        nuevo_chat = chat_repositorio.crear_chat_con_mensaje(
            id_delegado, id_candidato, idU, mensaje_texto
        )

        return (
            jsonify(
                {"message": "Chat creado exitosamente", "chat": nuevo_chat}
            ),
            201,
        )

    @staticmethod
    def eliminar_mensaje(idU, id_chat, id_mensaje):
        """Delete a message from a chat."""
        conn = chat_repositorio.get_db_connection()
        cursor = conn.cursor()

        # Validate user in SQL
        usuario = cursor.execute(
            "SELECT nombre FROM usuario WHERE Id = ?", (idU,)
        ).fetchone()
        conn.close()

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Validate chat exists and belongs to user
        chat = chat_repositorio.ver_chat(id_chat)
        if not chat:
            return jsonify({"error": "Chat no encontrado"}), 404

        if chat.get("id_candidato") != idU:
            return (
                jsonify({"error": "No tienes permiso para eliminar este chat"}),
                403,
            )

        # Delete message
        exito = chat_repositorio.eliminar_chat_mensaje(id_chat, idU, id_mensaje)

        if exito:
            return jsonify({"message": "Mensaje eliminado exitosamente"}), 200
        else:
            return (
                jsonify(
                    {
                        "error": "No se pudo eliminar el mensaje. Verifica si eres el autor o si el mensaje existe."
                    }
                ),
                403,
            )

    @staticmethod
    def eliminar_chat(idU, id_chat):
        """Delete a chat."""
        conn = chat_repositorio.get_db_connection()
        cursor = conn.cursor()

        # Validate user exists
        nombreU = cursor.execute(
            "SELECT nombre FROM usuario WHERE Id = ?", (idU,)
        ).fetchone()
        if not nombreU:
            conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Validate chat exists and belongs to user
        chat = chat_repositorio.ver_chat(id_chat)
        if not chat:
            conn.close()
            return jsonify({"error": "Chat no encontrado"}), 404

        if chat.get("id_candidato") != idU:
            conn.close()
            return (
                jsonify({"error": "No tienes permiso para eliminar este chat"}),
                403,
            )

        chat_repositorio.eliminar_chat_db(id_chat)
        conn.close()

        return jsonify({"message": "Chat eliminado exitosamente"}), 200

    # Helper methods that need to be implemented
    @staticmethod
    def obtener_chats_usuario(idU):
        """Get all chats for a user from MongoDB."""
        chats_collection = chat_repositorio.get_mongo_db()
        chats = chats_collection.find(
            {"$or": [{"id_delegado": idU}, {"id_candidato": idU}]}
        )
        return list(chats)

    @staticmethod
    def ver_chat(id_chat):
        """Get a specific chat from MongoDB."""
        chats_collection = chat_repositorio.get_mongo_db()
        return chats_collection.find_one({"id_chat": id_chat})

    @staticmethod
    def enviar_mensaje(id_chat, id_usuario, contenido):
        """Send a message to a chat."""
        chats_collection = chat_repositorio.get_mongo_db()
        mensaje = {
            "id_mensaje": ObjectId(),
            "id_emisor": id_usuario,
            "contenido": contenido,
            "timestamp": datetime.now().isoformat(),
        }
        result = chats_collection.update_one(
            {"id_chat": id_chat}, {"$push": {"mensajes": mensaje}}
        )
        return result.modified_count > 0

    @staticmethod
    def crear_chat_con_mensaje(id_delegado, id_candidato, id_emisor, mensaje_texto):
        """Create a new chat with first message."""
        chats_collection = chat_repositorio.get_mongo_db()
        nuevo_chat = {
            "id_chat": ObjectId(),
            "id_delegado": id_delegado,
            "id_candidato": id_candidato,
            "mensajes": [
                {
                    "id_mensaje": ObjectId(),
                    "id_emisor": id_emisor,
                    "contenido": mensaje_texto,
                    "timestamp": datetime.now().isoformat(),
                }
            ],
        }
        result = chats_collection.insert_one(nuevo_chat)
        return nuevo_chat

    @staticmethod
    def eliminar_chat_mensaje(id_chat, id_usuario, id_mensaje):
        """Delete a message from a chat."""
        chats_collection = chat_repositorio.get_mongo_db()
        result = chats_collection.update_one(
            {"id_chat": id_chat, "mensajes.id_mensaje": id_mensaje},
            {"$pull": {"mensajes": {"id_mensaje": id_mensaje, "id_emisor": id_usuario}}},
        )
        return result.modified_count > 0

    @staticmethod
    def eliminar_chat_db(id_chat):
        """Delete a chat from MongoDB."""
        chats_collection = chat_repositorio.get_mongo_db()
        chats_collection.delete_one({"id_chat": id_chat})



