# core/procesamiento/normalizar.py

import pandas as pd

MAPEO_COLUMNAS = {
    "Documento compras": "documento_compras",
    "Posición": "posicion",
    "Fecha documento": "fecha_documento",
    "Proveedor/Centro suministrador": "proveedor",
    "Texto breve": "texto_breve",
    "Valor neto de pedido": "valor_neto",
    "Moneda": "moneda",
    "Colaborador que aprobó la compra": "colaborador",
    "Compañía": "compania_id"
}

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombra las columnas de un DataFrame según el mapeo predefinido.
    Solo renombra las columnas que están en el mapeo.
    """
    columnas_actuales = df.columns.tolist()
    columnas_renombradas = {
        col: MAPEO_COLUMNAS[col]
        for col in columnas_actuales
        if col in MAPEO_COLUMNAS
    }

    df = df.rename(columns=columnas_renombradas)
    print("✅ Columnas normalizadas correctamente.")
    return df
