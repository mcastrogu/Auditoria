# core/procesamiento/archivo_excel.py
import os
import hashlib
import pandas as pd
from core.db.conexion import obtener_conexion

def calcular_hash_archivo(ruta_archivo):
    sha256 = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha256.update(bloque)
    return sha256.hexdigest()

def existe_archivo_excel(hash_archivo, conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM archivos_excel WHERE hash_archivo = %s", (hash_archivo,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def verificar_archivo_existente(hash_archivo, bd="sistema_auditoria_db"):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM archivos_excel WHERE hash_archivo = %s", (hash_archivo,))
        resultado = cursor.fetchone()
        return resultado["id"] if resultado else None
    except Exception as e:
        print(f"❌ Error al verificar archivo existente: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

def actualizar_estado_archivo(archivo_id, nuevo_estado, total_registros):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE archivos_excel SET estado = %s WHERE id = %s",
            (nuevo_estado, archivo_id)
        )
        conexion.commit()
        print(f"🟢 Estado del archivo {archivo_id} actualizado a '{nuevo_estado}'")
    except Exception as e:
        print(f"❌ Error al actualizar estado del archivo: {e}")
    finally:
        cursor.close()
        conexion.close()

def registrar_archivo_excel(nombre_archivo, usuario_id, ruta_archivo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    nombre_archivo = os.path.basename(ruta_archivo)
    hash_archivo = calcular_hash_archivo(ruta_archivo)

    # Leer cantidad de registros del archivo Excel
    try:
        df = pd.read_excel(ruta_archivo)
        cantidad = len(df)
    except Exception as e:
        print(f"❌ Error al leer Excel: {e}")
        return None

    try:
        cursor.execute("""
            INSERT INTO archivos_excel (nombre_archivo, usuario_id, cantidad_registros, hash_archivo)
            VALUES (%s, %s, %s, %s)
        """, (nombre_archivo, usuario_id, cantidad, hash_archivo))
        conexion.commit()
        archivo_id = cursor.lastrowid
        print(f"✅ Archivo registrado con ID: {archivo_id}")
        return archivo_id
    except Exception as e:
        print(f"❌ Error al registrar archivo: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

def obtener_datos_excel_por_id(archivo_id: int, conexion) -> pd.DataFrame:
    cursor = conexion.cursor(dictionary=True)

    # Leer directamente desde la tabla compras
    cursor.execute("""
        SELECT id, documento_compras, posicion, fecha_documento,
               proveedor, texto_breve, valor_neto, moneda,
               valor_convertido, colaborador, compania_id
        FROM compras
        WHERE archivo_id = %s
    """, (archivo_id,))

    registros = cursor.fetchall()
    cursor.close()

    return pd.DataFrame(registros)
