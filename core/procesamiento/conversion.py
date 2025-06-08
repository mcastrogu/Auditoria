import requests
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
from datetime import date
from core.db.conexion import obtener_conexion
load_dotenv()

API_KEY = os.getenv("EXCHANGERATE_API_KEY")
URL_BASE = "https://v6.exchangerate-api.com/v6"

# Conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Consulta tipo de cambio desde la base de datos

def obtener_tipo_cambio(moneda_origen, moneda_destino="PEN", conexion=None):
    if not conexion:
        return None

    hoy = date.today()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT tipo_cambio FROM conversion_moneda
        WHERE moneda_origen = %s AND moneda_destino = %s AND fecha = %s
    """, (moneda_origen.upper(), moneda_destino.upper(), hoy))

    resultado = cursor.fetchone()
    cursor.close()
    
    if resultado:
        return resultado[0]
    else:
        return None


def guardar_tipo_cambio_si_no_existe(moneda_origen, moneda_destino, conexion):
    hoy = date.today()
    cursor = conexion.cursor()

    # Verificar si ya existe el tipo de cambio
    cursor.execute("""
        SELECT tipo_cambio FROM conversion_moneda
        WHERE moneda_origen = %s AND moneda_destino = %s AND fecha = %s
        LIMIT 1
    """, (moneda_origen, moneda_destino, hoy))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]  # Ya existe, se retorna directamente

    # Si no existe, consultar la API e insertar
    try:
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{moneda_origen}"
        respuesta = requests.get(url).json()
        tipo_cambio = respuesta["conversion_rates"].get(moneda_destino)

        if tipo_cambio:
            cursor.execute("""
                INSERT INTO conversion_moneda (moneda_origen, moneda_destino, tipo_cambio, fecha)
                VALUES (%s, %s, %s, %s)
            """, (moneda_origen, moneda_destino, tipo_cambio, hoy))
            conexion.commit()
            print(f"✅ Registrado tipo de cambio {moneda_origen} → {moneda_destino}: {tipo_cambio}")
            return tipo_cambio
        else:
            print("❌ No se obtuvo el tipo de cambio desde la API (valor nulo o inválido)")
            return None

    except Exception as e:
        print(f"❌ Error al consultar API de tipo de cambio: {e}")
        return None
    finally:
        cursor.close()



# Consulta tipo de cambio desde la API
def consultar_api_tipo_cambio(moneda_origen, moneda_destino):
    url = f"{URL_BASE}/{API_KEY}/latest/{moneda_origen}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["result"] == "success":
            tipo_cambio = data["conversion_rates"].get(moneda_destino)
            if tipo_cambio is not None and isinstance(tipo_cambio, (float, int)):
                return tipo_cambio
    print(f"❌ Error al consultar API para {moneda_origen} → {moneda_destino}")
    return None

# Verifica e inserta tipo de cambio si no existe en la base de datos
def registrar_si_no_existe(moneda_origen, moneda_destino):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    hoy = datetime.today().date()

    query = """
        SELECT id FROM conversion_moneda
        WHERE moneda_origen = %s AND moneda_destino = %s AND fecha = %s
    """
    cursor.execute(query, (moneda_origen, moneda_destino, hoy))
    resultado = cursor.fetchone()

    if resultado:
        print(f"🟡 Ya existe registro para {moneda_origen} → {moneda_destino} del día {hoy}")
    else:
        tasa = consultar_api_tipo_cambio(moneda_origen, moneda_destino)
        if tasa:
            insert = """
                INSERT INTO conversion_moneda (moneda_origen, moneda_destino, tipo_cambio, fecha)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert, (moneda_origen, moneda_destino, tasa, hoy))
            conexion.commit()
            print(f"✅ Registrado tipo de cambio {moneda_origen} → {moneda_destino}: {tasa}")
        else:
            print("⚠️ No se insertó por error en la API o respuesta inválida.")

    cursor.close()
    conexion.close()


# Llamado principal
def ejecutar_registro_conversiones():
    registrar_si_no_existe("USD", "PEN")
    registrar_si_no_existe("EUR", "PEN")


if __name__ == "__main__":
    ejecutar_registro_conversiones()
