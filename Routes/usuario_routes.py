from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from Services import usuario_service
from Cross.jwt_middleware import login_required

usuario_bp = Blueprint("usuario", __name__)

@usuario_bp.route("/usuario/crear", methods=["GET"])
def crear_usuario_form():
    return render_template("registro.html")

@usuario_bp.route("/usuario/crear", methods=["POST"])
def crear_usuario():
    resultado, e, status = usuario_service.crear_usuario(
        request.form.get("nombre"),
        request.form.get("correo"),
        request.form.get("numero"),
        request.form.get("tipoUsuario"),
        request.form.get("password")
    )
    if e:
        return render_template("error_usuario.html", error=e)
    response = render_template("login.html", usuario=resultado)
    return response, status

@usuario_bp.route("/usuario/<int:id>", methods=["GET"])
@login_required
def obtener_usuario(payload, id):
    resultado, e, status = usuario_service.obtener_usuario(id)
    if e:
        return render_template("error_usuario.html", error=e)
    return render_template("perfil_usuario.html", usuario=resultado)

@usuario_bp.route("/actualizar-usuario/<int:id>", methods=["PUT"])
@login_required
def actualizar_usuario(payload, id):
    resultado, e, status = usuario_service.actualizar_usuario(
        id,
        request.form.get("nombre"),
        request.form.get("correo"),
        request.form.get("numero"),
        request.form.get("tipoUsuario"),
    )
    if e:
        return render_template("error_usuario.html", error=e)
    return render_template("perfil_usuario.html", usuario=resultado)

@usuario_bp.route("/actualizar-contrasena/<int:id>", methods=["PUT"])
@login_required
def actualizar_contrasena(payload, id):
    resultado, e, status = usuario_service.actualizar_contrasena(
        id,
        request.form.get("password")
    )
    if e:
        return render_template("error_usuario.html", error=e)
    return url_for('auth.login_form')

@usuario_bp.route("/borrar-usuario/<int:id>", methods=["DELETE"])
@login_required
def borrar_usuario(payload, id):
    resultado, e, status = usuario_service.eliminar_usuario(id)
    if e:
        return render_template("error_usuario.html", error=e)
    return render_template("registro.html")