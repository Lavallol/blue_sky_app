def normalizar_decimal(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return valor
    valor = str(valor).strip().replace(',', '.')
    try:
        return float(valor)
    except ValueError:
        return None
