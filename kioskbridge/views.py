import os
import json
import time
from datetime import datetime
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


PRODUCTOS_JSON_FILE = "productos.json"
DATOS_JSON_FILE = "datos.json"


# ------------------------------------------------------------------------------
# Helpers de Persistencia JSON para Productos
# ------------------------------------------------------------------------------

def cargar_productos():
    """Lee y retorna la lista de productos desde productos.json."""
    if not os.path.exists(PRODUCTOS_JSON_FILE):
        return []
    try:
        with open(PRODUCTOS_JSON_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return []
    return []


def guardar_productos(productos):
    """Guarda la lista de productos en productos.json."""
    with open(PRODUCTOS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------------------
# Vistas Web de KioskBridge
# ------------------------------------------------------------------------------

def resumen(request):
    """
    Vista Django que lee registros de transacciones desde datos.json (Modo Kiosco).
    """
    registros = []
    if os.path.exists(DATOS_JSON_FILE):
        try:
            with open(DATOS_JSON_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    registros = json.loads(content)
        except (json.JSONDecodeError, OSError):
            registros = []

    context = {
        "registros": registros
    }
    return render(request, "resumen.html", context)


def admin_productos(request):
    """
    Vista de Perfil Administrador (Modo Admin).
    Permite visualizar el catálogo, métricas de inventario e ingresar nuevos productos
    (nombre, cantidad y precio).
    """
    mensaje = None
    tipo_mensaje = "success"

    if request.method == "POST":
        accion = request.POST.get("accion", "crear")

        if accion == "crear":
            nombre = request.POST.get("nombre", "").strip()
            categoria = request.POST.get("categoria", "General").strip()
            cantidad_raw = request.POST.get("cantidad", "").strip()
            precio_raw = request.POST.get("precio", "").strip()

            if not nombre:
                mensaje = "El nombre del producto es obligatorio."
                tipo_mensaje = "error"
            else:
                try:
                    cantidad = int(cantidad_raw)
                    precio = int(precio_raw)

                    if cantidad < 0 or precio < 0:
                        mensaje = "La cantidad y el precio deben ser valores positivos o cero."
                        tipo_mensaje = "error"
                    else:
                        productos = cargar_productos()
                        # Generar ID auto-incremental único
                        nuevo_id = max([p.get("id", 0) for p in productos], default=0) + 1

                        nuevo_producto = {
                            "id": nuevo_id,
                            "nombre": nombre,
                            "categoria": categoria,
                            "cantidad": cantidad,
                            "precio": precio,
                            "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        productos.append(nuevo_producto)
                        guardar_productos(productos)
                        mensaje = f"Producto '{nombre}' ingresado exitosamente al inventario (Stock: {cantidad}, Precio: ${precio})."
                        tipo_mensaje = "success"
                except ValueError:
                    mensaje = "La cantidad y el precio deben ser números enteros válidos."
                    tipo_mensaje = "error"

        elif accion == "eliminar":
            producto_id_raw = request.POST.get("producto_id", "")
            try:
                producto_id = int(producto_id_raw)
                productos = cargar_productos()
                productos_filtrados = [p for p in productos if p.get("id") != producto_id]
                if len(productos_filtrados) < len(productos):
                    guardar_productos(productos_filtrados)
                    mensaje = f"Producto #{producto_id} eliminado del inventario correctamente."
                    tipo_mensaje = "success"
                else:
                    mensaje = f"No se encontró el producto #{producto_id}."
                    tipo_mensaje = "error"
            except ValueError:
                mensaje = "ID de producto inválido."
                tipo_mensaje = "error"

    # Cargar y enriquecer listado de productos para la plantilla
    productos = cargar_productos()
    total_stock = 0
    valor_inventario = 0
    stock_critico = 0

    for p in productos:
        cant = p.get("cantidad", 0)
        prec = p.get("precio", 0)
        p["valor_total"] = cant * prec
        total_stock += cant
        valor_inventario += p["valor_total"]
        if cant <= 5:
            stock_critico += 1

    context = {
        "productos": productos,
        "total_productos": len(productos),
        "total_stock": total_stock,
        "valor_inventario": f"{valor_inventario:,}".replace(",", "."),
        "stock_critico": stock_critico,
        "mensaje": mensaje,
        "tipo_mensaje": tipo_mensaje
    }
    return render(request, "admin_productos.html", context)


# ------------------------------------------------------------------------------
# Endpoints API REST para Productos (JSON)
# ------------------------------------------------------------------------------

@csrf_exempt
def api_productos(request):
    """
    Endpoint API REST para gestionar el catálogo de productos.
    - GET: Retorna listado de productos en formato JSON.
    - POST: Crea un nuevo producto (acepta JSON o form-data).
    """
    if request.method == "GET":
        productos = cargar_productos()
        return JsonResponse({
            "status": "success",
            "total": len(productos),
            "productos": productos
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})

    elif request.method == "POST":
        data = {}
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"status": "error", "message": "JSON inválido en el cuerpo de la petición."}, status=400)
        else:
            data = request.POST

        nombre = data.get("nombre", "").strip()
        categoria = data.get("categoria", "General").strip()
        cantidad = data.get("cantidad")
        precio = data.get("precio")

        if not nombre:
            return JsonResponse({"status": "error", "message": "El campo 'nombre' es obligatorio."}, status=400)

        try:
            cantidad = int(cantidad)
            precio = int(precio)
            if cantidad < 0 or precio < 0:
                return JsonResponse({"status": "error", "message": "'cantidad' y 'precio' deben ser >= 0."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "'cantidad' y 'precio' deben ser números enteros."}, status=400)

        productos = cargar_productos()
        nuevo_id = max([p.get("id", 0) for p in productos], default=0) + 1
        nuevo_producto = {
            "id": nuevo_id,
            "nombre": nombre,
            "categoria": categoria,
            "cantidad": cantidad,
            "precio": precio,
            "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        productos.append(nuevo_producto)
        guardar_productos(productos)

        return JsonResponse({
            "status": "success",
            "message": "Producto creado exitosamente.",
            "producto": nuevo_producto
        }, status=201, json_dumps_params={"indent": 2, "ensure_ascii": False})

    return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)


@csrf_exempt
def api_producto_detalle(request, producto_id):
    """
    Endpoint API REST para consultar o eliminar un producto específico por su ID.
    - GET: Retorna datos del producto.
    - DELETE: Elimina el producto del inventario.
    """
    productos = cargar_productos()
    producto = next((p for p in productos if p.get("id") == producto_id), None)

    if not producto:
        return JsonResponse({"status": "error", "message": f"Producto con ID {producto_id} no encontrado."}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "status": "success",
            "producto": producto
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})

    elif request.method == "DELETE":
        productos_restantes = [p for p in productos if p.get("id") != producto_id]
        guardar_productos(productos_restantes)
        return JsonResponse({
            "status": "success",
            "message": f"Producto con ID {producto_id} eliminado exitosamente."
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})

    return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)


# ------------------------------------------------------------------------------
# Endpoints Puente Moodle (PoC)
# ------------------------------------------------------------------------------

def moodle_users(request):
    """
    Endpoint puente que consume el Web Service REST de Moodle (core_user_get_users)
    utilizando la librería 'requests' y retorna los datos en formato JSON.
    """
    is_mock = request.GET.get("mock", "").lower() in ("true", "1", "yes")
    
    if is_mock:
        sample_users = [
            {
                "id": 1,
                "username": "guest",
                "fullname": "Invitado",
                "email": "root@localhost",
                "department": "Demo",
                "firstaccess": 0,
                "lastaccess": int(time.time()),
                "auth": "manual"
            },
            {
                "id": 2,
                "username": "admin",
                "fullname": "Administrador KioskBridge",
                "email": "admin@example.com",
                "department": "TI / Sistemas",
                "firstaccess": int(time.time()) - 86400,
                "lastaccess": int(time.time()),
                "auth": "manual"
            },
            {
                "id": 3,
                "username": "estudiante_demo",
                "fullname": "Juan Pérez",
                "email": "estudiante@demo.com",
                "department": "Capacitación Kiosco",
                "firstaccess": int(time.time()) - 3600,
                "lastaccess": int(time.time()),
                "auth": "manual"
            }
        ]
        return JsonResponse({
            "status": "success",
            "mode": "mock",
            "message": "Datos de prueba simulados. Para datos reales configure MOODLE_WS_TOKEN en .env",
            "total_users": len(sample_users),
            "users": sample_users
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})

    base_url = request.GET.get("moodle_url", getattr(settings, "MOODLE_BASE_URL", "http://localhost:8080")).rstrip("/")
    token = request.GET.get("token", getattr(settings, "MOODLE_WS_TOKEN", "")).strip()

    if not token:
        return JsonResponse({
            "status": "error",
            "code": "MISSING_TOKEN",
            "message": (
                "No se ha configurado el token de Moodle Web Services (MOODLE_WS_TOKEN). "
                "Genere un token en Moodle (Site administration > Server > Web services > Manage tokens) "
                "y agréguelo a su archivo .env o envíelo como ?token=<su_token>. "
                "Para probar la respuesta JSON inmediatamente sin Moodle, use ?mock=true"
            ),
            "hint": f"{request.build_absolute_uri('?mock=true')}"
        }, status=400, json_dumps_params={"indent": 2, "ensure_ascii": False})

    search_key = request.GET.get("key", "email")
    search_value = request.GET.get("value", "%")

    endpoint_url = f"{base_url}/webservice/rest/server.php"
    params = {
        "wstoken": token,
        "wsfunction": "core_user_get_users",
        "moodlewsrestformat": "json",
        "criteria[0][key]": search_key,
        "criteria[0][value]": search_value,
    }

    headers = {
        "User-Agent": "KioskBridge-Django-Bridge/1.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(endpoint_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and ("exception" in data or "errorcode" in data):
            return JsonResponse({
                "status": "error",
                "source": "moodle_api",
                "message": data.get("message", "Error reportado por Moodle Web Services"),
                "errorcode": data.get("errorcode"),
                "exception": data.get("exception"),
                "raw": data
            }, status=400, json_dumps_params={"indent": 2, "ensure_ascii": False})

        users_list = data.get("users", []) if isinstance(data, dict) else data

        return JsonResponse({
            "status": "success",
            "source": "moodle_api",
            "moodle_url": base_url,
            "total_users": len(users_list) if isinstance(users_list, list) else 1,
            "users": users_list,
            "warnings": data.get("warnings", []) if isinstance(data, dict) else []
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})

    except requests.exceptions.ConnectionError:
        return JsonResponse({
            "status": "error",
            "code": "CONNECTION_FAILED",
            "message": f"No se pudo conectar al servicio Moodle en '{base_url}'. Verifique que el contenedor de Moodle esté iniciado y en ejecución.",
            "moodle_url": base_url,
            "hint": "Si está ejecutando en Docker Compose, asegúrese de usar http://moodle:8080 como MOODLE_BASE_URL internamente."
        }, status=503, json_dumps_params={"indent": 2, "ensure_ascii": False})

    except requests.exceptions.Timeout:
        return JsonResponse({
            "status": "error",
            "code": "TIMEOUT",
            "message": f"Tiempo de espera agotado al conectar con Moodle ({base_url}).",
        }, status=504, json_dumps_params={"indent": 2, "ensure_ascii": False})

    except requests.exceptions.RequestException as exc:
        return JsonResponse({
            "status": "error",
            "code": "REQUEST_EXCEPTION",
            "message": f"Error al realizar la petición a Moodle: {str(exc)}"
        }, status=500, json_dumps_params={"indent": 2, "ensure_ascii": False})

    except ValueError:
        return JsonResponse({
            "status": "error",
            "code": "INVALID_JSON",
            "message": "La respuesta recibida de Moodle no tiene un formato JSON válido.",
            "raw_preview": response.text[:500] if 'response' in locals() else ""
        }, status=502, json_dumps_params={"indent": 2, "ensure_ascii": False})


def moodle_status(request):
    """
    Endpoint de diagnóstico para comprobar el estado y conectividad con la instancia Moodle.
    """
    base_url = str(getattr(settings, "MOODLE_BASE_URL", "http://localhost:8080")).rstrip("/")
    start_time = time.time()
    
    try:
        resp = requests.get(base_url, timeout=5)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return JsonResponse({
            "status": "online" if resp.status_code < 500 else "degraded",
            "moodle_url": base_url,
            "http_status": resp.status_code,
            "latency_ms": elapsed_ms,
            "token_configured": bool(str(getattr(settings, "MOODLE_WS_TOKEN", "")).strip())
        }, json_dumps_params={"indent": 2, "ensure_ascii": False})
    except Exception as exc:
        return JsonResponse({
            "status": "offline",
            "moodle_url": base_url,
            "error": str(exc),
            "token_configured": bool(str(getattr(settings, "MOODLE_WS_TOKEN", "")).strip())
        }, status=503, json_dumps_params={"indent": 2, "ensure_ascii": False})
