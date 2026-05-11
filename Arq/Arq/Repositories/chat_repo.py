from datetime import datetime
from Database.mongo_db import chats

class chat_repo:

    @staticmethod
    def obtener_chats_usuario(idU):
        return list(chats.find({
            "$or": [
                {"id_delegado": idU},
                {"id_candidato": idU}
            ]
        }))

    @staticmethod
    def ver_chat(id_chat):
        return chats.find_one({"id_chat": id_chat})

    @staticmethod
    def enviar_mensaje(id_chat, id_emisor, contenido):
        chat = chats.find_one({"id_chat": id_chat})
        if not chat:
            return False

        mensajes = chat.get("mensajes", [])
        id_mensaje = 1 if not mensajes else max(
            [m.get("id_mensaje", 0) for m in mensajes]
        ) + 1

        nuevo_mensaje = {
            "id_mensaje": id_mensaje,
            "id_emisor": id_emisor,
            "timestamp": datetime.now().isoformat(),
            "contenido": contenido
        }

        chats.update_one(
            {"id_chat": id_chat},
            {"$push": {"mensajes": nuevo_mensaje}}
        )
        return True

    @staticmethod
    def eliminar_chat(id_chat):
        chats.delete_one({"id_chat": id_chat})

    @staticmethod
    def eliminar_chat_mensaje(id_chat, idU, id_mensaje):
        chat = chats.find_one({"id_chat": id_chat})
        if not chat:
            return False

        mensaje_encontrado = None
        for msg in chat.get("mensajes", []):
            if msg.get("id_mensaje") == id_mensaje:
                mensaje_encontrado = msg
                break

        if not mensaje_encontrado:
            return False

        if mensaje_encontrado.get("id_emisor") != idU:
            return False

        chats.update_one(
            {"id_chat": id_chat},
            {"$pull": {"mensajes": {"id_mensaje": id_mensaje}}}
        )
        return True

    @staticmethod
    def crear_chat_con_mensaje(id_delegado, id_candidato, id_emisor, contenido):
        ultimo_chat = list(chats.find().sort("id_chat", -1).limit(1))
        id_chat = 1 if not ultimo_chat else ultimo_chat[0].get("id_chat", 0) + 1

        nuevo_chat = {
            "id_chat": id_chat,
            "id_delegado": id_delegado,
            "id_candidato": id_candidato,
            "mensajes": [
                {
                    "id_mensaje": 1,
                    "id_emisor": id_emisor,
                    "timestamp": datetime.now().isoformat(),
                    "contenido": contenido
                }
            ]
        }

        chats.insert_one(nuevo_chat)
        return nuevo_chat