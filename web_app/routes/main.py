from flask import Blueprint, render_template
from web_app.utils.decoradores import login_requerido, rol_requerido

main_bp = Blueprint('main', __name__)

@main_bp.route('/inicio')
@login_requerido
def inicio():
    return render_template('dashboard.html')


