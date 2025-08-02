from flask import Blueprint, render_template, request
import pandas as pd
from core.procesamiento.normalizar import normalizar_columnas
import time
from flask import flash
from flask import session
from core.db.conexion import obtener_conexion
from datetime import datetime
import hashlib
from flask import redirect, url_for, session
from core.procesamiento.conversion import obtener_tipo_cambio, registrar_si_no_existe
from core.procesamiento.procesar_excel import obtener_id_compania
from core.procesamiento.alertas import generar_alertas_por_modelo
from web_app.utils.decoradores import login_requerido
from core.procesar_indicadores import procesar_indicadores
from core.procesamiento.conversion import guardar_tipo_cambio_si_no_existe

excel_bp = Blueprint('excel', __name__)

ALLOWED_EXTENSIONS = {'xlsx'}   

def extension_valida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@excel_bp.route('/cargar_excel', methods=['GET', 'POST'])
@login_requerido
def cargar_excel():
    if request.method == 'POST':
        archivo = request.files.get('archivo_excel')

        if not archivo:
            flash("No se seleccionó ningún archivo.", "error")
            return render_template('cargar_excel.html')

        if not extension_valida(archivo.filename):
            flash("El archivo debe ser formato .xlsx", "error")
            return render_template('cargar_excel.html')

        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo)
            df = normalizar_columnas(df)

            columnas_relevantes = [
                "fecha_documento", "documento_compras", "posicion",
                "proveedor", "texto_breve", "valor_neto",
                "moneda", "colaborador", "compania_id"
            ]

            faltantes = [col for col in columnas_relevantes if col not in df.columns]
            if faltantes:
                flash(f" Faltan columnas requeridas: {', '.join(faltantes)}", "error")
                return render_template('cargar_excel.html')

            df_filtrado = df[columnas_relevantes]
            columnas = list(df_filtrado.columns)
            datos = df_filtrado.values.tolist()
            total_registros = len(df_filtrado)

            # Calcular hash del archivo
            contenido = archivo.read()
            archivo.seek(0)
            hash_archivo = hashlib.sha256(contenido).hexdigest()
            nombre_archivo = archivo.filename
            usuario_id = session['usuario_id']
            estado = "pendiente"

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verificar si ya existe el archivo
            cursor.execute("SELECT id FROM archivos_excel WHERE hash_archivo = %s", (hash_archivo,))
            resultado = cursor.fetchone()

            if resultado:
                archivo_id = resultado[0]
                flash("⚠️ Este archivo ya fue cargado anteriormente.", "warning")
            else:
                # Insertar temporalmente solo en memoria
                cursor.execute("""
                    INSERT INTO archivos_excel (nombre_archivo, usuario_id, fecha_subida, estado, cantidad_registros, hash_archivo)
                    VALUES (%s, %s, NOW(), %s, %s, %s)
                """, (nombre_archivo, usuario_id, estado, total_registros, hash_archivo))
                conexion.commit()
                archivo_id = cursor.lastrowid

                # Insertar en vista_previa
                for _, fila in df_filtrado.iterrows():
                    cursor.execute("""
                        INSERT INTO vista_previa (archivo_id, fecha_documento, documento_compras, posicion,
                                                  proveedor, texto_breve, valor_neto, moneda, colaborador, compania_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        archivo_id,
                        fila["fecha_documento"],
                        fila["documento_compras"],
                        fila["posicion"],
                        fila["proveedor"],
                        fila["texto_breve"],
                        fila["valor_neto"],
                        fila["moneda"],
                        fila["colaborador"],
                        fila["compania_id"]
                    ))

                conexion.commit()
                flash("✔️ Archivo cargado correctamente.", "success")

            cursor.close()
            conexion.close()

            return redirect(url_for('excel.confirmar_carga', archivo_id=archivo_id))

        except Exception as e:
            flash(f"❌ Error al leer el archivo: {str(e)}", "error")
            return render_template('cargar_excel.html')

    return render_template('cargar_excel.html')


@excel_bp.route('/confirmar_carga')
def confirmar_carga():
    archivo_id = request.args.get('archivo_id')

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener datos de la tabla vista_previa
    cursor.execute("SELECT * FROM vista_previa WHERE archivo_id = %s", (archivo_id,))
    registros = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    # Obtener nombre del archivo
    cursor.execute("SELECT nombre_archivo FROM archivos_excel WHERE id = %s", (archivo_id,))
    nombre = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    return render_template('confirmar_carga.html', datos=registros, columnas=columnas, archivo_id=archivo_id, nombre=nombre)

@excel_bp.route('/confirmar_carga', methods=['POST'])
def confirmar_carga_post():
    archivo_id = request.form.get("archivo_id")

    if not archivo_id:
        flash("No se proporcionó el archivo para confirmar.", "error")
        return redirect(url_for('excel.cargar_excel'))

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener registros de vista_previa
    cursor.execute("SELECT * FROM vista_previa WHERE archivo_id = %s", (archivo_id,))
    registros = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    
    # Obtener tipo de cambio desde la base o API para evita doble llamada
    usd_pen = guardar_tipo_cambio_si_no_existe("USD", "PEN", conexion)
    if usd_pen is None:
        flash(" No se pudo obtener el tipo de cambio USD → PEN.", "error")
        return redirect(url_for("excel.cargar_excel"))

    eur_pen = guardar_tipo_cambio_si_no_existe("EUR", "PEN", conexion)
    if eur_pen is None:
        flash(" No se pudo obtener el tipo de cambio EUR → PEN.", "error")
        return redirect(url_for("excel.cargar_excel"))

    if usd_pen is None:
        return redirect(url_for("excel.cargar_excel"))  


    insertados = 0

    for fila in registros:
        fila_dict = dict(zip(columnas, fila))
        valor_neto = float(fila_dict["valor_neto"])
        moneda = fila_dict["moneda"].strip().upper()

        # Convertir según moneda
        if moneda == "USD":
            valor_convertido = round(valor_neto * float(usd_pen), 2)
        elif moneda == "EUR":
            valor_convertido = round(valor_neto * float(eur_pen), 2)
        elif moneda == "PEN":
            valor_convertido = valor_neto
        else:
            print(f"⚠️ Moneda desconocida: {moneda}")
            continue

        # Obtener ID compañía desde nombre
        id_compania = obtener_id_compania(fila_dict["compania_id"], conexion)
        if not id_compania:
            print(f"⚠️ Compañía no encontrada: {fila_dict['compania_id']}")
            continue

        # Insertar en tabla compras
        cursor.execute("""
            INSERT INTO compras (
                archivo_id, documento_compras, posicion, fecha_documento,
                proveedor, texto_breve, valor_neto, moneda,
                valor_convertido, colaborador, compania_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            archivo_id,
            fila_dict["documento_compras"],
            fila_dict["posicion"],
            fila_dict["fecha_documento"],
            fila_dict["proveedor"],
            fila_dict["texto_breve"],
            valor_neto,
            moneda,
            valor_convertido,
            fila_dict["colaborador"],
            id_compania
        ))
        insertados += 1

    # Limpiar registros temporales y marcar archivo como procesado
    cursor.execute("DELETE FROM vista_previa WHERE archivo_id = %s", (archivo_id,))
    cursor.execute("UPDATE archivos_excel SET estado = 'procesado', cantidad_registros = %s WHERE id = %s",
                   (insertados, archivo_id))
    
    # =======================
    # Generar alertas por umbral
    # =======================
    # ✅ Volver a cargar las compras insertadas para ese archivo
    cursor.execute("SELECT * FROM compras WHERE archivo_id = %s", (archivo_id,))
    columnas = [desc[0] for desc in cursor.description]
    compras_insertadas = cursor.fetchall()
    df_compras = pd.DataFrame(compras_insertadas, columns=columnas)

    # ✅ Generar alertas por modelo ML (Isolation Forest)

    generar_alertas_por_modelo(archivo_id, conexion)

    procesar_indicadores(df_compras, archivo_id, conexion)



   # 1. Obtener inicio y calcular tiempo real
    inicio = session.get('inicio_sesion', time.time())
    fin = time.time()
    tiempo_total = round(float(fin - inicio), 2)

    # 2. Asegurar que el archivo_id sea int
    archivo_id_int = int(archivo_id)

    # 3. Ejecutar UPDATE solo si la conexión sigue activa
    if tiempo_total > 0:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE indicadores_resultado SET tiempo_deteccion_segundos = %s WHERE archivo_id = %s",
                (tiempo_total, archivo_id)
            )
            conexion.commit()
            cursor.close()
        except Exception as e:
            pass

    flash(f"✅ {insertados} registros insertados correctamente en la base de datos.", "success")
    return redirect(url_for('excel.cargar_excel'))


