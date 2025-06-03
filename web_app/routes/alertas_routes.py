from flask import Blueprint, render_template
from core.db.conexion import obtener_conexion
from web_app.utils.decoradores import login_requerido

alertas_bp = Blueprint("alertas", __name__)

@alertas_bp.route('/alertas')
@login_requerido
def ver_alertas():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.id, a.archivo_id, a.tipo_alerta, a.origen_alerta,
              a.mensaje, a.fecha_creacion,
              c.documento_compras, c.texto_breve, c.valor_convertido, c.moneda
        FROM alertas_ml a
        JOIN compras c ON a.compra_id = c.id
        ORDER BY a.id DESC
    """)
    alertas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('alertas.html', alertas=alertas)

