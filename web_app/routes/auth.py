from flask import Blueprint, render_template, request, redirect, url_for, flash, session
#from core.db.conexion import obtener_conexion
import time


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        # VALIDACIÓN MANUAL SIMPLIFICADA
        if usuario == 'admin' and contraseña == 'admin':
            session['usuario'] = 'admin'
            session['rol'] = 'admin'
            return redirect(url_for('main.inicio'))

        flash('Credenciales inválidas. Intenta nuevamente.', 'danger')
        return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
