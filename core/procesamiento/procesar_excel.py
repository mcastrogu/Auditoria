# core/procesamiento/procesar_excel.py
import pandas as pd
from core.procesamiento.normalizar import normalizar_columnas
from core.procesamiento.conversion import obtener_tipo_cambio, guardar_tipo_cambio_si_no_existe


# Columnas requeridas mínimas
COLUMNAS_REQUERIDAS = [
    'documento_compras',
    'posicion',
    'fecha_documento',
    'proveedor',
    'texto_breve',
    'valor_neto',
    'moneda',
    'colaborador',
    'compania_id'
]

def leer_excel_y_validar(path_excel):
    try:
        df = pd.read_excel(path_excel)
        df.columns = df.columns.str.strip()
        df = normalizar_columnas(df)
        print("✅ Columnas normalizadas correctamente.")

        # Validar columnas mínimas
        faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
        if faltantes:
            raise ValueError(f"❌ Faltan columnas requeridas: {faltantes}")

        return df

    except Exception as e:
        raise RuntimeError(f"❌ Error al leer o validar el Excel: {str(e)}")

def obtener_id_compania(nombre_compania, conexion):
    cursor = conexion.cursor()
    query = "SELECT id FROM companias WHERE nombre LIKE %s LIMIT 1"
    cursor.execute(query, (nombre_compania.strip(),))
    resultado = cursor.fetchone()
    cursor.close()
    if resultado:
        return resultado[0]
    else:
        return None

def insertar_compras(df, archivo_id, conexion):

    print(f"🛠️ Insertando archivo_id: {archivo_id}")
    print(f"📄 Total de filas a insertar: {len(df)}")

    cursor = conexion.cursor()

    # Obtener tipo de cambio
    usd_pen = obtener_tipo_cambio("USD", "PEN")
    eur_pen = obtener_tipo_cambio("EUR", "PEN")

    df["archivo_id"] = archivo_id  # Para asegurar que cada fila tenga el archivo_id

    insertados = 0

    print("📋 Preview de las primeras filas para insertar:")
    print(df.head())
    print("🟦 Columnas:", df.columns.tolist())
    print("🟦 Total de filas:", len(df))
    
    for _, fila in df.iterrows():
        print("🔍 Analizando fila:", fila.to_dict())
        try:

            # Validar que todos los campos estén presentes
            requeridos = ["documento_compras", "posicion", "fecha_documento", "proveedor", "texto_breve", "colaborador"]
            faltantes = [campo for campo in requeridos if pd.isna(fila.get(campo))]

            if faltantes:
                print(f"⚠️ Fila omitida por campos vacíos: {faltantes}")
                continue

            # Para depurar si todo viene bien
            print("🔄 Procesando fila:", fila.to_dict())

            valor_neto = float(fila["valor_neto"])
            moneda = str(fila["moneda"]).strip().upper()

            # Convertir el valor a PEN según moneda
            if moneda == "USD":
                tipo_cambio = usd_pen or guardar_tipo_cambio_si_no_existe("USD", "PEN", conexion)
                if tipo_cambio is None:
                    print(f"⚠️ Tipo de cambio USD>PEN no disponible. Fila omitida.")
                    continue
                valor_convertido = round(valor_neto * float(tipo_cambio), 2)

            elif moneda == "EUR":
                tipo_cambio = eur_pen or guardar_tipo_cambio_si_no_existe("EUR", "PEN", conexion)
                if tipo_cambio is None:
                    print(f"⚠️ Tipo de cambio EUR>PEN no disponible. Fila omitida.")
                    continue
                valor_convertido = round(valor_neto * float(tipo_cambio), 2)

            elif moneda == "PEN":
                valor_convertido = valor_neto

            else:
                print(f"⚠️ Moneda desconocida: {moneda}. Registro omitido.")
                continue

            print("🔍 Buscando ID de compañía para:", fila["compania_id"])
            id_compania = obtener_id_compania(fila["compania_id"], conexion)


            # Obtener id_compania desde base de datos
            id_compania = obtener_id_compania(fila["compania_id"], conexion)
            if not id_compania:
                print(f"⚠️ No se encontró la compañía: {fila['compania_id']}. Registro omitido.")
                continue

            print("🔄 Procesando fila:", fila.to_dict())

            cursor.execute("""
                INSERT INTO compras (
                    archivo_id, documento_compras, posicion, fecha_documento, proveedor,
                    texto_breve, valor_neto, moneda, valor_convertido, colaborador, compania_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                archivo_id,
                fila["documento_compras"],
                fila["posicion"],
                fila["fecha_documento"],
                fila["proveedor"],
                fila["texto_breve"],
                valor_neto,
                moneda,
                valor_convertido,
                fila["colaborador"],
                id_compania
            ))
            insertados += 1
        except Exception as e:
            print("⚠️ Error en fila:", fila.to_dict())
            print("❌ Detalle del error:", e)

    # ✅ Actualizar cantidad de registros
    cursor.execute(
        "UPDATE archivos_excel SET cantidad_registros = %s WHERE id = %s",
        (insertados, archivo_id)
    )

    # ✅ Marcar archivo como procesado
    cursor.execute(
        "UPDATE archivos_excel SET estado = 'procesado' WHERE id = %s",
        (archivo_id,)
    )

    print(f"✅ Inserción finalizada. Total insertados correctamente: {insertados}")

    conexion.commit()

    cursor.close()

    print(f"✅ Inserción completada. Total insertados: {insertados}")

#--------------------PARA LOS INDICADORES------------------------------------------------------- 

