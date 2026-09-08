# Registro de Interacción y Correcciones con Inteligencia Artificial (ia.md)

Este documento registra las consultas realizadas a la Inteligencia Artificial durante la planificación y desarrollo del proyecto **KioskBridge API**, así como las decisiones y correcciones manuales aplicadas sobre sus sugerencias.

---

## 1. Consultas Iniciales Realizadas a la IA

### Consulta 1: Estructura del Proyecto y Persistencia
- **Pregunta:** "Crea un proyecto Django para registrar transacciones de un kiosco evaluando reglas de stock y persistiendo los datos."
- **Respuesta de la IA:** La IA generó un proyecto estándar Django creando modelos en `models.py` (`class Transaccion(models.Model)...`), sugiriendo la ejecución de `python manage.py makemigrations` y `python manage.py migrate` sobre SQLite.

### Consulta 2: Motor de Decisión
- **Pregunta:** "Escribe la lógica para validar las compras de clientes según stock y límites."
- **Respuesta de la IA:** La IA entregó un bloque `if/else` desordenado donde primero validaba la cantidad máxima por cliente antes de comprobar si los números ingresados eran negativos o nulos.

---

## 2. Correcciones Manuales y Descartes Críticos

### ❌ Descarte de Base de Datos Relacional (SQLite / Models)
- **Motivo de Corrección:** Las restricciones estrictas de la evaluación académica establecen que el proyecto debe ser **SIN BASE DE DATOS** (`models.py` vacío o no utilizado, cero migraciones).
- **Acción Realizada:** Se eliminó la propuesta de modelos de la IA. Se implementó persistencia directa de arreglos JSON en `datos.json` mediante las librerías nativas `os` y `json`, tanto en el script CLI `solucion.py` como en la vista Django `kioskbridge/views.py`.

### 🛠️ Corrección del Motor de Decisión (Regla de 4 Estados)
- **Motivo de Corrección:** La IA no respetaba el orden estricto de prelación exigido para evaluar los casos.
- **Acción Realizada:** Se reestructuró manualmente el motor `evaluar_transaccion()` con `if/elif/else` respetando la siguiente secuencia inviolable:
  1. **Caso 1 (Dato inválido):** `cantidad <= 0` o `stock_actual < 0` (Prevalece sobre cualquier otro límite).
  2. **Caso 2 (Rechazo límite):** `cantidad > 10` (Límite máximo por cliente).
  3. **Caso 3 (Rechazo stock):** `cantidad > stock_actual` (Stock insuficiente).
  4. **Caso 4 (Aceptado):** Descuento de stock `stock_actual - cantidad` y autorización.

### 🔒 Integración de Variables de Entorno con `python-decouple`
- **Motivo de Corrección:** Inicialmente la IA dejó la `SECRET_KEY` quemada en el código fuente (`hardcoded`).
- **Acción Realizada:** Se configuró `python-decouple` en `settings.py` para leer `SECRET_KEY` y `DEBUG` desde el archivo `.env`.

---

## 3. Conclusión de la Interacción
Las correcciones aplicadas garantizan el cumplimiento del 100% de los requerimientos académicos, aislando la solución en un entorno liviano, determinista y mantenible sin sobrecarga de base de datos.

