from flask import Blueprint, render_template, request, jsonify
from Services.chat_service import chat_service
from Cross.jwt_middleware import login_required

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chats/<int:idU>", methods=["GET"])
@login_required
def ver_chats(payload, idU):
    resultado, error, status = chat_service.obtener_chats_de_usuario(idU)
    if error:
        return render_template("error_chat.html", error=error, usuario=idU)
    return render_template("lista_chats.html", chats=resultado, usuario=idU)

@chat_bp.route("/chats/<int:idU>/<int:idChat>", methods=["GET"])
@login_required
def obtener_chat(payload, idU, idChat):
    resultado, e, status = chat_service.obtener_chat_detalle(idU, idChat)
    if e:
        return render_template("error.html", error = e)
    return render_template("chats.html", chats = resultado)

@chat_bp.route("/chats/<int:idU>", methods=["POST"])
@login_required
def crear_chat(payload, idU):
    if request.is_json():
        data = request.get_json()
    else:
        data = request.form.get
        
    resultado, e, status = chat_service.crear_chat(
        idU,
        data.get("id_delegado"),
        data.get("id_candidato"),
        data.get("mensaje")
    )
    if e:
        return render_template("error.html", error = e)
    return render_template("chat.html", chat = resultado.get("id_chat"))

@chat_bp.route("/chats/<int:id_chat>/mensaje", methods=["POST"])
@login_required
def enviar_mensaje(payload, id_chat):
    if request.is_json():    
        data = request.get_json()
    else:
        data = request.form()
    resultado, e, status = chat_service.enviar_mensaje(
        id_chat,
        data.get("id_usuario"),
        data.get("mensaje")
    )
    if e:
        return render_template("error.html", error = e)
    return render_template("chat.html", chat = id_chat)

@chat_bp.route("/chats/<int:idU>/<int:id_chat>/<int:id_mensaje>", methods=["DELETE"])
@login_required
def eliminar_mensaje(payload, idU, id_chat, id_mensaje):
    resultado, error, status = chat_service.eliminar_mensaje(idU, id_chat, id_mensaje)
    if error:
        return render_template("error_chat.html", error=error, usuario=idU)
    return render_template("chat_detalle.html", chat=resultado, usuario=idU)

@chat_bp.route("/chats/<int:idU>/<int:id_chat>", methods=["DELETE"])
@login_required
def eliminar_chat(payload, idU, id_chat):
    resultado, error, status = chat_service.eliminar_chat(idU, id_chat)
    if error:
        return render_template("error_chat.html", error=error, usuario=idU)
    return render_template("lista_chats.html", chats=resultado, usuario=idU)