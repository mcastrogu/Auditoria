from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core.db.conexion import obtener_conexion
import time


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from flask import current_app as app
    app.logger.debug("🔐 Intentando iniciar sesión")

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
                session['inicio_sesion'] = time.time()

                app.logger.debug(f"✅ Login exitoso del usuario: {usuario}")
                flash('Inicio de sesión exitoso.', 'success')

                if user['rol'] == 'admin':
                    return redirect(url_for('main.inicio'))  # cambia si tienes dashboard_admin
                else:
                    return redirect(url_for('main.inicio'))  # cambia si tienes dashboard_auditor

            else:
                app.logger.warning(f"⚠️ Credenciales inválidas para el usuario: {usuario}")
                flash('Credenciales inválidas. Intenta nuevamente.', 'danger')
                return render_template('login.html')

        except Exception as e:
            app.logger.error(f"❌ Error interno durante el login de {usuario}: {e}")
            flash("Ocurrió un error interno. Inténtalo más tarde.", "danger")
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
