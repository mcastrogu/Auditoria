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
import mysql.connector
from core.db.conexion import obtener_conexion

def obtener_tipo_cambio(moneda_origen, moneda_destino="PEN", conexion=None):
    if not conexion:
        return None

    cursor = conexion.cursor()
    cursor.execute("""
        SELECT tipo_cambio FROM conversion_moneda
        WHERE moneda_origen = %s AND moneda_destino = %s AND DATE(fecha) = CURDATE()
    """, (moneda_origen.upper(), moneda_destino.upper()))

    
    resultado = cursor.fetchone()
    cursor.close()
    
    if resultado:
        return resultado[0]
    else:
        return None

def guardar_tipo_cambio_si_no_existe(moneda_origen, moneda_destino, conexion):
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT tipo_cambio FROM conversion_moneda
        WHERE moneda_origen = %s AND moneda_destino = %s AND fecha = CURDATE()
        LIMIT 1
    """, (moneda_origen, moneda_destino))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    # Si no existe, llamar API
    try:
        url = f"https://v6.exchangerate-api.com/v6/6eccdce87b4e32c975299c6d/latest/{moneda_origen}"
        respuesta = requests.get(url).json()
        tipo_cambio = respuesta["conversion_rates"].get(moneda_destino)

        if tipo_cambio:
            cursor.execute("""
                INSERT INTO conversion_moneda (moneda_origen, moneda_destino, tipo_cambio, fecha)
                VALUES (%s, %s, %s, CURDATE())
            """, (moneda_origen, moneda_destino, tipo_cambio))
            conexion.commit()
            return tipo_cambio
    except Exception as e:
        print(f"❌ Error al consultar API de tipo de cambio: {e}")
        return None

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
