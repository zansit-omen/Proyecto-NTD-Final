import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS

from Routes.auth_routes import auth_bp
from Routes.usuario_routes import usuario_bp
from Routes.empresas_routes import empresa_bp
from Routes.delegado_routes import delegado_bp
from Routes.candidato_routes import candidato_bp
from Routes.ofertas_routes import oferta_bp
from Routes.postulaciones_routes import postulacion_bp
from Routes.chat_routes import chat_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(empresa_bp)
app.register_blueprint(delegado_bp)
app.register_blueprint(candidato_bp)
app.register_blueprint(oferta_bp)
app.register_blueprint(postulacion_bp)
app.register_blueprint(chat_bp)

if __name__ == "__main__":
    app.run(debug=True)