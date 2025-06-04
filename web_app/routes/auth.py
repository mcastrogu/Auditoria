from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.db.conexion import obtener_conexion
import time


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s AND password_hash = %s", (usuario, contraseña))
            user = cursor.fetchone()
            cursor.close()
            conexion.close()

            if user:
                session['usuario_id'] = user['id']
                session['usuario'] = user['nombre_usuario']
                session['rol'] = user['rol']
                session['nombre_completo'] = user['nombres'] + ' ' + user['apellidos']
                return redirect(url_for('main.inicio'))

            flash('Credenciales inválidas. Intenta nuevamente.', 'danger')

        except Exception as e:
            print(f"[ERROR] Durante login: {e}")
            flash('Error interno. Intenta más tarde.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
