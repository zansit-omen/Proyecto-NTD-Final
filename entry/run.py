import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_cors import CORS
import webbrowser
from threading import Timer

load_dotenv()

from Routes.auth_routes import auth_bp
from Routes.usuario_routes import usuario_bp
from Routes.empresas_routes import empresa_bp
from Routes.delegado_routes import delegado_bp
from Routes.candidato_routes import candidato_bp
from Routes.ofertas_routes import oferta_bp
from Routes.postulaciones_routes import postulacion_bp
from Routes.chat_routes import chat_bp
from Services import oferta_service

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG')

CORS(app)

@app.route('/')
def index():
    datos_ofertas, error, status = oferta_service.obtener_todas()
    print(f"DEBUG: Datos de ofertas -> {datos_ofertas}") 
    return render_template('index.html', ofertas=datos_ofertas if datos_ofertas else [])

app.register_blueprint(auth_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(empresa_bp)
app.register_blueprint(delegado_bp)
app.register_blueprint(candidato_bp)
app.register_blueprint(oferta_bp)
app.register_blueprint(postulacion_bp)
app.register_blueprint(chat_bp)

def abrir_navegador(url):
    webbrowser.open(url)

if __name__ == "__main__":
    api_host = os.getenv('API_HOST', '0.0.0.0')
    api_port = int(os.getenv('API_PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    url = f'http://127.0.0.1:{api_port}'
    
    timer = Timer(1, abrir_navegador, args=[url])
    timer.daemon = True
    timer.start()
    
    app.run(host=api_host, port=api_port, debug=True)