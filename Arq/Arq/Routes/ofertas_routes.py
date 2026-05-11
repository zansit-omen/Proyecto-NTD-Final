from flask import Blueprint, request, jsonify, render_template
from Services import oferta_service
from Cross.jwt_middleware import delegado_required, candidato_required

oferta_bp = Blueprint("oferta", __name__)

@oferta_bp.route("/delegado/<int:idU>/oferta", methods=["GET"])
@delegado_required
def obtener_ofertas(payload, idU):
    resultado, e, status = oferta_service.obtener_todas()
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("lista_ofertas.html", ofertas=resultado, autor=idU)

@oferta_bp.route("/delegado/<int:idU>/oferta/<int:oferta_id>", methods=["GET"])
@delegado_required
def buscar_oferta(payload, idU, oferta_id):
    resultado, e, status = oferta_service.obtener_por_id(oferta_id)
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("oferta_detalle.html", oferta=resultado)

@oferta_bp.route("/delegado/<int:idU>/oferta/crear", methods=["POST"])
@delegado_required
def crear_oferta(payload, idU):
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    resultado, e, status = oferta_service.crear_oferta(
        idU,
        data.get("titulo"),
        data.get("descripcionOferta"),
        data.get("profesionBuscar")
    )
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("oferta_detalle.html", oferta=resultado)

@oferta_bp.route("/delegado/<int:idU>/oferta/<int:oferta_id>", methods=["PUT"])
@delegado_required
def actualizar_oferta(payload, idU, oferta_id):
    if request.is_json():
        data = request.get_json()
    else:
        data = request.form
    resultado, e, status = oferta_service.actualizar_oferta(
        oferta_id,
        data.get("titulo"),
        data.get("descripcionOferta"),
        data.get("profesionBuscar"),
        data.get("estadoOferta")
    )
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("oferta_detalle.html", oferta=resultado)

@oferta_bp.route("/delegado/<int:idU>/oferta/<int:oferta_id>", methods=["DELETE"])
@delegado_required
def eliminar_oferta(payload, idU, oferta_id):
    resultado, e, status = oferta_service.eliminar_oferta(oferta_id)
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("lista_ofertas.html", ofertas=resultado, autor=idU)

@oferta_bp.route("/candidato/<int:id>/ofertas", methods=["GET"])
def ver_ofertas_candidato(payload, id):
    resultado, e, status = oferta_service.obtener_todas()
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("lista_ofertas.html", ofertas=resultado, autor=id)

@oferta_bp.route("/candidato/<int:id>/ofertas/<int:oferta_id>/postular", methods=["POST"])
@candidato_required
def postular_oferta(payload, id, oferta_id):
    from Services import postulaciones_service
    resultado, e, status = postulaciones_service.postular(id, oferta_id)
    if e:
        return render_template("error_oferta.html", error=e)
    return render_template("postulacion_exitosa.html", postulacion=resultado)