import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder

def detectar_anomalias_logicas(df):
    """
    Detecta errores estructurales lógicos mediante Machine Learning.
    Marca como 1 los registros anómalos en la columna 'es_error_logico'.
    """

    columnas_logicas = ["unidad_medida", "tipo_imputacion", "proveedor", "moneda"]

    # Verificar qué columnas están disponibles en el archivo
    columnas_existentes = [col for col in columnas_logicas if col in df.columns]
    if not columnas_existentes:
        df["es_error_logico"] = 0
        return df

    # Reemplazar valores nulos
    df_limpio = df[columnas_existentes].fillna("NULO")

    # Codificación One-Hot para datos categóricos
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_encoded = encoder.fit_transform(df_limpio)

    # Aplicar Isolation Forest
    modelo = IsolationForest(contamination=0.03, random_state=42)
    modelo.fit(X_encoded)

    predicciones = modelo.predict(X_encoded)

    # Convertir -1 (anómalo) → 1, 1 (normal) → 0
    df["es_error_logico"] = [1 if p == -1 else 0 for p in predicciones]

    return df
