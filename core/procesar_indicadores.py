from core.ml_model import detectar_anomalias_logicas

def procesar_indicadores(df, archivo_id, conexion):
    # 1. Iniciar tiempo
    #--inicio = time.time()

    # 2. Detectar errores lógicos con ML
    df = detectar_anomalias_logicas(df)  # Agrega columna 'es_error_logico'
    errores_identificados = df['es_error_logico'].sum()

    # 3. Contar discrepancias ya guardadas en alertas_ml

    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM alertas_ml WHERE archivo_id = %s", (archivo_id,))
    discrepancias_identificadas = cursor.fetchone()[0]

    # 4. Calcular tiempo total
    #---fin = time.time()
    #--tiempo_deteccion = round(fin - inicio, 2)

    # 5. Insertar indicadores en la base de datos
    sql = """
        INSERT INTO indicadores_resultado (
            archivo_id, tiempo_deteccion_segundos,
            errores_identificados, discrepancias_identificadas
        ) VALUES (%s, %s, %s, %s)
    """
    valores = (
        int(archivo_id),
        float(0),
        int(errores_identificados),
        int(discrepancias_identificadas)
    )

    cursor.execute(sql, valores)
  

    return df
