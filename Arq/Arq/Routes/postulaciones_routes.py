from flask import Blueprint, render_template, request, jsonify
from Services import postulaciones_service
from Cross.jwt_middleware import delegado_required, login_required, candidato_required

postulacion_bp = Blueprint("postulacion", __name__)

@postulacion_bp.route("/delegado/<int:idU>/oferta/<int:oferta_id>/postulacion", methods=["GET"])
@delegado_required
def ver_postulaciones(payload, idU, oferta_id):
    resultado, e, status = postulaciones_service.obtener_por_oferta(oferta_id)
    if e:
        return render_template("error_postulacion.html", error=e)
    return render_template("lista_postulaciones.html", postulaciones=resultado, oferta=oferta_id)

@postulacion_bp.route("/delegado/<int:idU>/oferta/<int:oferta_id>/postulacion/<int:postulacion_id>/aceptar", methods=["PUT"])
@delegado_required
def aceptar_postulacion(payload, idU, oferta_id, postulacion_id):
    resultado, e, status = postulaciones_service.aceptar(postulacion_id)
    if e:
        return render_template("error_postulacion.html", error=e)
    return render_template("postulacion_aceptada.html", postulacion=resultado)

@postulacion_bp.route("/delegado/<int:idU>/oferta/<int:oferta_id>/postulacion/<int:postulacion_id>/rechazar", methods=["PUT"])
@delegado_required
def rechazar_postulacion(payload, idU, oferta_id, postulacion_id):
    resultado, e, status = postulaciones_service.rechazar(postulacion_id)
    if e:
        return render_template("error_postulacion.html", error=e)
    return render_template("postulacion_rechazada.html", postulacion=resultado)

@postulacion_bp.route("/postulacion/<int:postulacion_id>", methods=["GET"])
@login_required
def obtener_postulacion(payload, postulacion_id):
    resultado, e, status = postulaciones_service.obtener_postulacion(postulacion_id)
    if e:
        return render_template("error_postulacion.html", error=e)
    return render_template("postulacion_detalle.html", postulacion=resultado)

@postulacion_bp.route("/postulacion/<int:postulacion_id>", methods=["DELETE"])
@candidato_required
def cancelar_postulacion(payload, postulacion_id):
    resultado, e, status = postulaciones_service.cancelar(postulacion_id)
    if e:
        return render_template("error_postulacion.html", error=e)
    return render_template("perfil_candidato.html")