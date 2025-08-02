from datetime import date, datetime
from core.db.conexion import obtener_conexion
from sklearn.ensemble import IsolationForest
import pandas as pd



def generar_alertas_por_modelo(archivo_id, conexion):
    cursor = conexion.cursor(dictionary=True)

    # Obtener las compras asociadas al archivo
    cursor.execute("""
        SELECT id, valor_convertido
        FROM compras
        WHERE archivo_id = %s
    """, (archivo_id,))
    registros = cursor.fetchall()

    if not registros:
        print(" No hay registros para aplicar modelo ML.")
        return

    df = pd.DataFrame(registros, columns=["id", "valor_convertido"])

    # Entrenar el modelo Isolation Forest
    modelo = IsolationForest(contamination=0.1, random_state=42)
    df["es_anomalia"] = modelo.fit_predict(df[["valor_convertido"]])
    df["es_anomalia"] = df["es_anomalia"].apply(lambda val: 1 if val == -1 else 0)
    
    insertados = 0
    for _, fila in df[df["es_anomalia"] == 1].iterrows():
        compra_id = int(fila["id"])
        valor = fila["valor_convertido"]

        # Clasificación por niveles
        if valor >= 650000:
            tipo_alerta = "grave"
        elif valor >= 48000:
            tipo_alerta = "moderada"
        else:
            tipo_alerta = "leve"

        mensaje = f" Compra anómala de {valor:,.2f} soles detectada por modelo – clasificada como {tipo_alerta.upper()}"

        # Insertar en tabla de alertas
        cursor.execute("""
            INSERT INTO alertas_ml (compra_id, archivo_id, tipo_alerta, mensaje, fecha_creacion, origen_alerta)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (compra_id, archivo_id, tipo_alerta, mensaje, "ml"))

        insertados += 1

    cursor.close()
   
    print(f" Alertas por modelo ML generadas y clasificadas: {insertados}")


    
def generar_alertas(df, archivo_id, conexion):
    generar_alertas_por_modelo(archivo_id, conexion)
