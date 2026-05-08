from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from Services import delegado_service
from Cross.jwt_middleware import login_required, delegado_required

delegado_bp = Blueprint("delegado", __name__)

# ─────────────────────────────────────────────────────────────
# Rutas de Delegados
# ─────────────────────────────────────────────────────────────

@delegado_bp.route("/crear-delegado", methods=["POST"])
def crear_delegado(payload):
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    resultado, e, status = delegado_service.crear_delegado(
        data.get("usuarioId"),
        data.get("empresaId")
    )
    if e:
        return render_template("error_delegado.html", error=e)
    return redirect(url_for("login"))

@delegado_bp.route("/delegado/<int:delegado_id>", methods=["GET"])
@delegado_required
 # Eventualmente habra que cambiar el parametro de busqueda por el email o el nombre y apellido del usuario, pues cuando los usuarios de la app quieran buscar 
 # Algun delegado, no sabran su ID.
def buscar_delegado(payload, delegado_id):
    resultado, e, status = delegado_service.obtener_delegado(delegado_id)
    if e:
        return render_template("error_delegado.html", error=e)
    return render_template("perfil_delegado.html", delegado=resultado)