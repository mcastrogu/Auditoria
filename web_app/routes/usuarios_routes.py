from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.db.conexion import obtener_conexion
from web_app.utils.decoradores import login_requerido, rol_requerido
from flask import session

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['GET', 'POST'])
@login_requerido
@rol_requerido('admin')
def gestionar_usuarios():
    print("SESIÓN ACTUAL:", dict(session))
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':
        modo = request.form.get('modo')
        nombre_usuario = request.form.get('nombre_usuario')
        dni = request.form.get('dni')
        password = request.form.get('password') or ''
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        correo = request.form.get('correo')
        rol = request.form.get('rol')

        # Evitar inserción sin contraseña
        if modo == 'registro' and not password.strip():
            flash('La contraseña es obligatoria para registrar un nuevo usuario.', 'danger')
            return redirect(url_for('usuarios.gestionar_usuarios'))


        if modo == 'registro':
            cursor.execute("""
                INSERT INTO usuarios (dni, nombre_usuario, password_hash, nombres, apellidos, correo, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (dni, nombre_usuario, password, nombres, apellidos, correo, rol))
            flash('Usuario registrado correctamente.', 'success')

        elif modo == 'editar':
            id_usuario = request.form['id']
            if password:
                # Si se ingresó una nueva contraseña, actualiza todo
                cursor.execute("""
                    UPDATE usuarios
                    SET dni=%s, nombre_usuario=%s, password_hash=%s, nombres=%s, apellidos=%s, correo=%s, rol=%s
                    WHERE id=%s
                """, (dni, nombre_usuario, password, nombres, apellidos, correo, rol, id_usuario))
            else:
                # Si no se ingresó contraseña, se omite ese campo
                cursor.execute("""
                    UPDATE usuarios
                    SET dni=%s, nombre_usuario=%s, nombres=%s, apellidos=%s, correo=%s, rol=%s
                    WHERE id=%s
                """, (dni, nombre_usuario, nombres, apellidos, correo, rol, id_usuario))

            flash('Cambios guardados correctamente.', 'success')

        conexion.commit()

    # Siempre cargar la tabla actualizada
    cursor.execute("SELECT id, dni, nombre_usuario, nombres, apellidos, correo, rol FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()

    print("Usuarios cargados desde DB:", usuarios)
    return render_template('usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/eliminar_usuario/<int:id>', methods=['GET'])
@login_requerido
@rol_requerido('admin')
def eliminar_usuario(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuarios.gestionar_usuarios'))
