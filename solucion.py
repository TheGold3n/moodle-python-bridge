import os
import json
from tabulate import tabulate


def evaluar_transaccion(producto: str, stock_actual: int, cantidad: int):
    """
    Motor de decision de 4 estados (evaluacion en orden estricto):
    Caso 1: Dato invalido (cantidad <= 0 o stock_actual < 0)
    Caso 2: Rechazo limite (cantidad > 10)
    Caso 3: Rechazo stock (cantidad > stock_actual)
    Caso 4: Aceptado (descuento de stock y autoriza la venta)
    """
    # Conversiones explicitas a int por seguridad
    stock_actual = int(stock_actual)
    cantidad = int(cantidad)

    # Caso 1 (Dato invalido)
    if cantidad <= 0 or stock_actual < 0:
        estado = "Rechazado"
        motivo = "Dato invalido: cantidad o stock menor/igual a 0"
        stock_restante = stock_actual

    # Caso 2 (Rechazo limite)
    elif cantidad > 10:
        estado = "Rechazado"
        motivo = "Supera el limite maximo de 10 unidades por cliente"
        stock_restante = stock_actual

    # Caso 3 (Rechazo stock)
    elif cantidad > stock_actual:
        estado = "Rechazado"
        motivo = "Stock insuficiente"
        stock_restante = stock_actual

    # Caso 4 (Aceptado)
    else:
        estado = "Aceptado"
        motivo = "Venta autorizada"
        stock_restante = stock_actual - cantidad

    return {
        "producto": str(producto),
        "stock_inicial": stock_actual,
        "cantidad": cantidad,
        "estado": estado,
        "motivo": motivo,
        "stock_restante": stock_restante,
    }


def main():
    print("=== KioskBridge API - Script CLI de Transacciones ===")

    # Solicitar datos por consola
    producto = input("Ingrese el nombre del producto: ").strip()
    
    try:
        stock_actual = int(input("Ingrese el stock actual (entero): "))
        cantidad = int(input("Ingrese la cantidad requerida (entero): "))
    except ValueError:
        print("\n[ERROR] Los datos numericos deben ser enteros validos.")
        return

    # Evaluar transaccion segun motor de decision
    registro = evaluar_transaccion(producto, stock_actual, cantidad)

    archivo_json = "datos.json"
    registros = []

    # Persistencia directa en datos.json
    if os.path.exists(archivo_json):
        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    registros = json.loads(content)
        except (json.JSONDecodeError, OSError):
            registros = []

    registros.append(registro)

    # Guardar lista actualizada en datos.json
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)

    print("\n--- Resultado de la Transaccion ---")
    print(f"Estado: {registro['estado']}")
    print(f"Motivo: {registro['motivo']}")
    print(f"Stock Restante: {registro['stock_restante']}")

    # Mostrar historial completo con tabulate
    print("\n--- Historial Completo de Registros en datos.json ---")
    print(tabulate(registros, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    main()

