# scripts/forzar_conversion.py
from core.procesamiento.conversion import obtener_tipo_cambio

print("Registrando tipo de cambio USD → PEN...")
valor = obtener_tipo_cambio("USD", "PEN")
print(f"✅ Tipo de cambio registrado: 1 USD = {valor} PEN")
