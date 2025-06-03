""""
import os
from core.db.conexion import obtener_conexion
from core.procesamiento.procesar_excel import leer_excel_y_validar, insertar_compras
from core.procesamiento.archivo_excel import existe_archivo_excel, registrar_archivo_excel, actualizar_estado_archivo
from core.db.conexion import obtener_conexion
from core.procesamiento.archivo_excel import calcular_hash_archivo

# Parámetros del archivo a cargar
NOMBRE_ARCHIVO = "compras_euro.xlsx"
RUTA_ARCHIVO = f"data/{NOMBRE_ARCHIVO}"

USUARIO_ID = 1  # Este valor es simulado

print("Ruta absoluta esperada:", os.path.abspath(RUTA_ARCHIVO))
print("Existe el archivo?", os.path.exists(RUTA_ARCHIVO))

# Verificar si el archivo ya fue procesado
conexion = obtener_conexion()
hash_archivo = calcular_hash_archivo(RUTA_ARCHIVO)
if existe_archivo_excel(hash_archivo, conexion):
    print(f"⚠️ El archivo '{NOMBRE_ARCHIVO}' ya fue procesado anteriormente.")
else:
    print(f"🔄 Procesando nuevo archivo: {NOMBRE_ARCHIVO}")

    # Registrar el archivo en la base de datos
    archivo_id = registrar_archivo_excel(NOMBRE_ARCHIVO, USUARIO_ID, RUTA_ARCHIVO)
    print(f"📝 Archivo registrado con ID: {archivo_id}")

    # Leer y validar
    try:
        df = leer_excel_y_validar(RUTA_ARCHIVO)
        print(f"📄 Total registros válidos: {len(df)}")

        # Insertar las compras
        insertar_compras(df, archivo_id)
        
        # Actualizar estado del archivo
        actualizar_estado_archivo(archivo_id, "procesado", len(df))
        print("✅ Archivo procesado e insertado correctamente.")
    
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        actualizar_estado_archivo(archivo_id, "error", 0)
"""

# test_funcional.py
import os
from core.procesamiento.procesar_excel import leer_excel_y_validar, insertar_compras
from core.db.conexion import obtener_conexion
from core.procesamiento.archivo_excel import registrar_archivo_excel
from core.procesamiento.alertas import generar_alertas_por_umbral
from core.procesamiento.alertas import generar_alertas_por_modelo

# 📄 Parámetros del archivo a cargar
NOMBRE_ARCHIVO = "excel_prueba_alertas_ml.xlsx"
RUTA_ARCHIVO = f"data/{NOMBRE_ARCHIVO}"
USUARIO_ID = 1  # Este valor es simulado

print("Ruta absoluta esperada:", os.path.abspath(RUTA_ARCHIVO))
print("Existe el archivo?", os.path.exists(RUTA_ARCHIVO))

# 1. Leer y validar Excel
print("📥 Leyendo y validando Excel...")
df = leer_excel_y_validar(RUTA_ARCHIVO)

# 2. Registrar el archivo en la base de datos
conexion = obtener_conexion()
archivo_id = registrar_archivo_excel(NOMBRE_ARCHIVO, USUARIO_ID, RUTA_ARCHIVO)
print(f"✅ Archivo registrado con ID: {archivo_id}")

# 3. Insertar compras
insertar_compras(df, archivo_id)

# 4. Generar alertas por umbral
generar_alertas_por_umbral(archivo_id)

# === PRUEBA: ALERTAS POR MODELO ML ===
print("\n📌 Probando generación de alertas por modelo ML...")

try:
    generar_alertas_por_modelo(archivo_id, bd="sistema_auditoria_db_pruebas")
    print("✅ Alertas por modelo ML generadas correctamente.")
except Exception as e:
    print(f"❌ Error al generar alertas por modelo ML: {e}")
