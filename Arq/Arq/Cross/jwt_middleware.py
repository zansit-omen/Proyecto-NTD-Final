import jwt
import datetime
from functools import wraps
from flask import request, redirect, url_for, flash, jsonify

# JWT Configuration
SECRET_KEY = "SuperSecretaClaveJWT"
ALGORITHM = "HS256"
TOKEN_EXP_HOURS = 2
COOKIE_NAME = "jwt_token"


class JWTMiddleware:
    """Middleware de autenticación JWT."""

    @staticmethod
    def generar_token(user_id: int, email: str, rol: str, nombre: str) -> str:
        """
        Genera un token JWT para un usuario.

        Args:
            user_id: ID del usuario
            email: Email del usuario
            rol: Rol del usuario
            nombre: Nombre del usuario

        Returns:
            Cadena del token JWT
        """
        ahora = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": str(user_id),
            "email": email,
            "rol": rol,
            "nombre": nombre,
            "iat": int(ahora.timestamp()),
            "exp": int(
                (ahora + datetime.timedelta(hours=TOKEN_EXP_HOURS)).timestamp()
            ),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"[JWT] Token generado: {token[:30]}...")
        return token

    @staticmethod
    def obtener_payload_actual() -> dict | None:
        """
        Obtiene el payload JWT actual de las cookies.

        Returns:
            Diccionario de payload o None si es inválido
        """
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            print("[JWT] No se encontró cookie")
            return None
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"[JWT] Token válido para: {payload.get('email')}")
            return payload
        except jwt.PyJWTError as e:
            print(f"[JWT] Error al decodificar: {e}")
            return None


# ──────────────────────────────────────────────────────────────
# Funciones auxiliares para compatibilidad hacia atrás
# ──────────────────────────────────────────────────────────────


def generar_token(user_id: int, email: str, rol: str, nombre: str) -> str:
    """Genera un token JWT."""
    return JWTMiddleware.generar_token(user_id, email, rol, nombre)


def obtener_payload_actual() -> dict | None:
    """Obtiene el payload JWT actual de las cookies."""
    return JWTMiddleware.obtener_payload_actual()


# ──────────────────────────────────────────────────────────────
# Decoradores de protección
# ──────────────────────────────────────────────────────────────


def login_required(f):
    """Decorador para requerir login (cualquier usuario autenticado)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        payload = obtener_payload_actual()
        if payload is None:
            return jsonify({"error": "Token no válido o expirado"}), 401

        # Obtener ID del usuario desde el token
        user_id_from_token = int(payload.get("sub"))

        # Obtener ID del usuario desde la URL
        user_id_from_url = kwargs.get("id")

        # Verificar que el ID del token coincida con el de la URL si está presente
        if user_id_from_url:
            if user_id_from_token != user_id_from_url:
                return (
                    jsonify(
                        {"error": "No tienes permisos para acceder a este recurso"}
                    ),
                    403,
                )

        return f(payload, *args, **kwargs)

    return decorated


def delegado_required(f):
    """Decorador para requerir rol de delegado."""

    @wraps(f)
    def decorated(*args, **kwargs):
        payload = obtener_payload_actual()
        if payload is None:
            return jsonify({"error": "Token no válido o expirado"}), 401

        # Verificar que el rol sea delegado
        if payload.get("rol") != "delegado":
            return (
                jsonify({"error": "Acceso denegado: se requiere rol de delegado"}),
                403,
            )

        # Obtener ID del usuario desde el token
        user_id_from_token = int(payload.get("sub"))

        # Obtener ID del usuario desde la URL
        user_id_from_url = kwargs.get("idU") or kwargs.get("id")

        # Verificar que el ID del token coincida con el de la URL si está presente
        if user_id_from_url:
            if user_id_from_token != int(user_id_from_url):
                return (
                    jsonify(
                        {"error": "No tienes permisos para acceder a este recurso"}
                    ),
                    403,
                )

        return f(payload, *args, **kwargs)

    return decorated    
    
def candidato_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        payload = obtener_payload_actual()
        if not payload:
            return jsonify({"error": "Token no válido o expirado"}), 401
        if payload.get("rol") != "candidato":
            return jsonify({"error": "su rol no tiene acceso a esta informacion"}), 401
        
        id_token= payload.get("sub")  
        id_url = kwargs.get("idU") or kwargs.get("id")
        
        if id_token != int(id_url) and id_token and id_url:
            return jsonify({"error": "No tienes acceso a este recurso"}), 401
        
        return f(payload, *args, **kwargs)
    return decorated