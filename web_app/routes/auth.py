from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.db.conexion import obtener_conexion
import time

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

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
            session['inicio_sesion'] = time.time()

            # Justo después de login exitoso
            session['inicio_sesion'] = time.time()
            
            flash('Inicio de sesión exitoso.', 'success')

            if user['rol'] == 'admin':
                return redirect(url_for('main.inicio'))  # o main.dashboard_admin si se tiene
            else:
                return redirect(url_for('main.inicio'))  # o main.dashboard_auditor 
        else:
            flash('Credenciales inválidas. Intenta nuevamente.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
