# Software Design Document (SDD) - KioskBridge API

## 1. Problemática
Los puntos de venta tipo kiosco en entornos de baja complejidad o sistemas embebidos requieren un mecanismo de validación rápida de transacciones de stock que funcione de forma autónoma, sin incurrir en la sobrecarga de administración, configuración y mantenimiento de un motor de Base de Datos Relacional (como PostgreSQL, MySQL o SQLite).

Adicionalmente, se requiere garantizar un control de calidad estricto al momento de autorizar transacciones para evitar compras masivas inconsistentes, cantidades inválidas o ventas sin stock disponible.

## 2. Solución Técnica Propuesta
**KioskBridge API** es una arquitectura híbrida de validación y visualización basada en Python y Django:
1. **Script CLI (`solucion.py`):** Interfaz interactiva de línea de comandos para la captura, evaluación estricta en 4 estados y persistencia en tiempo real.
2. **Persistencia Directa JSON (`datos.json`):** Almacenamiento ligero y transparente mediante archivos JSON sin uso de ORM ni migraciones.
3. **Panel Web de Resumen (`kioskbridge` / Django):** Vista web basada en Django que lee y renderiza el historial completo almacenado en `datos.json` mediante plantillas HTML estilizadas.
4. **Seguridad y Entorno:** Manejo de claves mediante variables de entorno aisladas (`python-decouple` y `.env`).

---

## 3. Matriz MoSCoW

| Categoría | Requerimiento / Funcionalidad | Descripción |
| :--- | :--- | :--- |
| **Must Have** (Imprescindible) | **Persistencia JSON Sin BD** | Lectura/Escritura directa en `datos.json`. Cero tablas u ORM (`models.py`). |
| **Must Have** (Imprescindible) | **Motor de 4 Estados** | Evaluación en orden estricto: Dato inválido -> Rechazo límite -> Rechazo stock -> Aceptado. |
| **Must Have** (Imprescindible) | **Conversión Explícita** | Parseo obligatorio con `int()` para stock y cantidad. |
| **Must Have** (Imprescindible) | **Visualización CLI** | Formateo e impresión del historial por consola usando la librería `tabulate`. |
| **Must Have** (Imprescindible) | **Vista Django Resumen** | Renderizado HTML en ruta raíz (`/`) leyendo `datos.json` con soporte para bloque `{% empty %}`. |
| **Must Have** (Imprescindible) | **Gestión de Entorno** | Carga de `SECRET_KEY` desde `.env` usando `python-decouple`. |
| **Should Have** (Debería tener) | **Estilo UI en HTML** | Tabla responsiva con bordes limpios y distintivos visuales según el estado de la venta. |
| **Should Have** (Debería tener) | **Manejo de Archivo Ausente** | Si `datos.json` no existe o está vacío, retornar lista vacía `[]` sin romper el servidor web ni el CLI. |
| **Could Have** (Podría tener) | **Filtros por Producto** | Búsqueda o filtrado visual en la interfaz web de transacciones. |
| **Won't Have** (No se incluirá) | **Persistencia Relacional** | No se utilizará SQLite, PostgreSQL ni ningún motor SQL. |
| **Won't Have** (No se incluirá) | **Autenticación/Usuarios** | No se incluirán sistemas de login o permisos de sesión en esta versión. |

---

## 4. Especificación OpenAPI 3.0 (OpenSpec YAML)

```yaml
openapi: 3.0.3
info:
  title: KioskBridge API Spec
  description: Especificacion del contrato de datos y transacciones para KioskBridge API (Persistencia JSON).
  version: 1.0.0
paths:
  /:
    get:
      summary: Obtiene el resumen de transacciones desde datos.json
      description: Lee el archivo datos.json y retorna el listado completo procesado.
      responses:
        '200':
          description: Listado de transacciones obtenido exitosamente.
          content:
            text/html:
              schema:
                type: string
                example: "<html>...<table>...</table></html>"
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Transaccion'

components:
  schemas:
    Transaccion:
      type: object
      required:
        - producto
        - stock_inicial
        - cantidad
        - estado
        - motivo
        - stock_restante
      properties:
        producto:
          type: string
          example: "Bebida 500ml"
        stock_inicial:
          type: integer
          example: 15
        cantidad:
          type: integer
          example: 2
        estado:
          type: string
          enum: [Aceptado, Rechazado]
          example: "Aceptado"
        motivo:
          type: string
          example: "Venta autorizada"
        stock_restante:
          type: integer
          example: 13
```

