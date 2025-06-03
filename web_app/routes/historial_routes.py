from flask import Blueprint, render_template
from core.db.conexion import obtener_conexion
from web_app.utils.decoradores import login_requerido

historial_bp = Blueprint('historial', __name__)

@historial_bp.route('/historial')
@login_requerido
def ver_historial():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT ae.id,
               ae.nombre_archivo,
               ae.fecha_subida,
               ae.estado,
               ae.cantidad_registros,
               COUNT(am.id) AS total_alertas,
               CONCAT(u.nombres, ' ', u.apellidos) AS nombre_usuario
        FROM archivos_excel ae
        LEFT JOIN alertas_ml am ON ae.id = am.archivo_id
        LEFT JOIN usuarios u ON u.id = ae.usuario_id
        GROUP BY ae.id
        ORDER BY ae.fecha_subida DESC
    """)

    archivos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('historial.html', archivos=archivos)
