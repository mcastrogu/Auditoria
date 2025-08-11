import os
import mysql.connector


def obtener_conexion(nombre_bd="sistema_auditoria_db"):
    """
    Retorna una conexión a la base de datos especificada.
    Por defecto se conecta a 'sistema_auditoria_db'.
    """
    print("PORT =", os.getenv("DB_PORT"), "| TYPE =", type(os.getenv("DB_PORT")))

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=str(os.getenv("DB_PORT")),
        database=str(nombre_bd),
        connection_timeout=5 
    )
