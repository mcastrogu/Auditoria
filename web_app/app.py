from flask import Flask
from web_app.routes.auth import auth_bp
from web_app.routes.main import main_bp
from web_app.routes.excel_routes import excel_bp
from web_app.routes.alertas_routes import alertas_bp
from web_app.routes.historial_routes import historial_bp
from web_app.routes.usuarios_routes import usuarios_bp

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'aprobemostesisaunqueestamossufriendo'



# Registro de blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(excel_bp)
app.register_blueprint(alertas_bp)
app.register_blueprint(historial_bp)
app.register_blueprint(usuarios_bp)

# Ruta base para verificar que el sistema esté funcionando
@app.route('/')
def index():
    return "Sistema en línea. Ir a <a href='/login'>/login</a>"


if __name__ == '__main__':
    app.run(debug=True)