# 🚀 KioskBridge API — Integración PoC con Moodle

Prueba de Concepto (PoC) para extender el backend de **KioskBridge** (Django + MongoDB) integrándolo con la plataforma de aprendizaje **Moodle** (Moodle + MySQL) mediante un ecosistema unificado y contenerizado con **Docker Compose**, además de un endpoint puente en Django construido con la librería `requests`.

---

## 🏛️ Arquitectura del Ecosistema

El proyecto orquesta 4 servicios interconectados a través de una red interna bridge (`kiosk-network`):

| Servicio | Contenedor | Imagen Base | Puerto Expuesto | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`django`** | `kioskbridge_django` | `python:3.10-slim` | `8001` | API Django KioskBridge y puente REST hacia Moodle. |
| **`mysql`** | `kioskbridge_mysql` | `mysql:8.0` | `3306` | Motor de base de datos relacional UTF8MB4 requerido por Moodle. |
| **`moodle`** | `kioskbridge_moodle` | `bitnamilegacy/moodle:latest` | `8080`, `8443` | LMS Moodle listo para habilitar Web Services REST. |

```
                       [ Host / Cliente / Browser ]
                                     |
               +---------------------+---------------------+
               | :8001                                     | :8080
       +---------------+                           +---------------+
       +-------+-------+                           +-------+-------+
               |                                           |
               | (requests REST)                           | (SQL)
               v                                           v
       +-------+-------+                           +-------+-------+
       | mongodb (DB)  |                           |  mysql (DB)   |
       +---------------+                           +---------------+
              (Red Docker Interna Compartida: kiosk-network)
```

---

## 📋 Requisitos Previos

- **Docker Desktop** (con soporte Docker Compose v2) instalado y en ejecución en Windows/Linux/macOS.
- **Python 3.10+** (opcional, únicamente si se desea ejecutar el script CLI o el servidor fuera de Docker).

---

## ⚙️ 1. Configuración del Entorno (`.env`)

Antes de iniciar el ecosistema, inicializa el archivo `.env` a partir de la plantilla:

### En Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

### En Linux / macOS:
```bash
cp .env.example .env
```

El archivo `.env` incluye las siguientes variables clave:
```ini
# Configuración Django
SECRET_KEY=django-insecure-kioskbridge-demo-key-12345
DEBUG=True
ALLOWED_HOSTS=*

# MongoDB (KioskBridge)
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
MONGO_INITDB_DATABASE=kioskbridge_db
MONGO_URI=mongodb://root:example@mongodb:27017/kioskbridge_db?authSource=admin

# MySQL (Moodle)
MYSQL_ROOT_PASSWORD=moodle_root_password
MYSQL_DATABASE=moodle
MYSQL_USER=moodle_user
MYSQL_PASSWORD=moodle_password

# Moodle
MOODLE_BASE_URL=http://localhost:8080
MOODLE_WS_TOKEN=
MOODLE_ADMIN_USER=admin
MOODLE_ADMIN_PASSWORD=Moodle123!
MOODLE_ADMIN_EMAIL=admin@example.com
MOODLE_SITE_NAME=KioskBridge Moodle PoC
```

---

## 🐳 2. Levantar el Ecosistema Completo

Ejecuta el siguiente comando en la raíz del proyecto para construir y levantar todos los contenedores en segundo plano:

```bash
docker compose up -d --build
```

### Verificar estado de los contenedores:
```bash
docker compose ps
```

Deberás ver los cuatro contenedores (`kioskbridge_django`, `kioskbridge_mongodb`, `kioskbridge_mysql`, `kioskbridge_moodle`) con estado `Up` o `running`.

> **Nota sobre el primer inicio de Moodle:** La primera vez que se inicia Moodle, este inicializa las tablas en MySQL y compila los esquemas iniciales. Este proceso puede tardar entre 2 y 5 minutos. Puedes seguir el progreso con:
> ```bash
> docker compose logs -f moodle
> ```

---

## 🔑 3. Configuración de Moodle Web Services (Paso a Paso)

Para que Django pueda consultar usuarios reales de Moodle mediante la API REST, sigue estos pasos en el panel administrativo:

1. **Ingresar a Moodle:**
   - Abre en tu navegador: `http://localhost:8080`
   - Inicia sesión con usuario `admin` y contraseña `Moodle123!` (o los definidos en tu `.env`).

2. **Habilitar Servicios Web:**
   - Ve a **Site administration** (*Administración del sitio*) > **Server** (*Servidor*) > **Web services** (*Servicios web*) > **Overview** (*Visión general*).
   - Haz clic en **Enable web services** y activa la casilla correspondiente.

3. **Habilitar Protocolo REST:**
   - Ve a **Site administration** > **Server** > **Web services** > **Manage protocols** (*Administrar protocolos*).
   - En la fila **REST protocol**, haz clic en el ícono del ojo para habilitarlo.

4. **Crear un Servicio Externo:**
   - Ve a **Site administration** > **Server** > **Web services** > **External services** (*Servicios externos*).
   - Haz clic en **Add** (*Añadir*).
   - Nombre: `KioskBridge Service`.
   - Nombre corto: `kioskbridge_svc`.
   - Activa las casillas **Enabled** y **Authorized users only**.
   - Guarda los cambios.

5. **Añadir la función de Usuarios al Servicio:**
   - En la lista de servicios externos, haz clic en **Functions** (*Funciones*) junto a `KioskBridge Service`.
   - Haz clic en **Add functions** (*Añadir funciones*).
   - Busca y selecciona: `core_user_get_users`.
   - Haz clic en **Add functions**.

6. **Generar el Token de Acceso:**
   - Ve a **Site administration** > **Server** > **Web services** > **Manage tokens** (*Gestionar tokens*).
   - Haz clic en **Add** (*Añadir*).
   - Selecciona el usuario `Admin User` y el servicio `KioskBridge Service`.
   - Guarda los cambios y **copia el token generado** (cadena alfanumérica de 32 caracteres).

7. **Configurar el Token en Django:**
   - Pega el token obtenido en tu archivo `.env`:
     ```ini
     MOODLE_WS_TOKEN=tu_token_aqui_1234567890abcdef
     ```
   - Reinicia el contenedor de Django para cargar el nuevo token:
     ```bash
     docker compose restart django
     ```

---

## 🧪 4. Pruebas y Consumo del Endpoint Puente

Django expone las siguientes rutas para interactuar con Moodle y con el sistema KioskBridge:

### A) Endpoint Puente: Obtener Usuarios de Moodle
- **Ruta:** `GET /api/moodle/usuarios/`
- **URL completa:** `http://localhost:8001/api/moodle/usuarios/`
- **Librería utilizada:** `requests.get()` hacia `/webservice/rest/server.php?wsfunction=core_user_get_users`

No necesitas configurar el token ni esperar a que Moodle termine de iniciar para validar el formato de salida JSON:
```bash
curl "http://localhost:8001/api/moodle/usuarios/?mock=true"
```
*Respuesta JSON:*
```json
  "status": "success",
  "mode": "mock",
  "message": "Datos de prueba simulados. Para datos reales configure MOODLE_WS_TOKEN en .env",
  "total_users": 3,
  "users": [
    {
      "id": 1,
      "username": "guest",
      "fullname": "Invitado",
      "email": "root@localhost",
      "department": "Demo",
      "auth": "manual"
    },
    {
      "id": 2,
      "username": "admin",
      "fullname": "Administrador KioskBridge",
      "email": "admin@example.com",
      "department": "TI / Sistemas",
      "auth": "manual"
    },
    {
      "id": 3,
      "username": "estudiante_demo",
      "fullname": "Juan Pérez",
      "email": "estudiante@demo.com",
      "department": "Capacitación Kiosco",
      "auth": "manual"
    }
  ]
}
```

#### Opción 2: Prueba con Moodle Activo (Token Configurado en `.env`)
```bash
curl "http://localhost:8001/api/moodle/usuarios/"
```

#### Opción 3: Pasar Token o Criterios Directamente por Query String
```bash
curl "http://localhost:8001/api/moodle/usuarios/?token=tu_token_aqui"

# Filtrando por nombre de usuario
curl "http://localhost:8001/api/moodle/usuarios/?token=tu_token_aqui&key=username&value=admin"
```


### B) Endpoint de Diagnóstico / Health Check de Moodle
- **Ruta:** `GET /api/moodle/status/`

Verifica si la instancia Moodle está respondiendo y mide la latencia de respuesta:
```bash
curl "http://localhost:8001/api/moodle/status/"
```
*Respuesta:*
```json
  "status": "online",
  "moodle_url": "http://moodle:8080",
  "http_status": 200,
  "latency_ms": 12.45,
}
```

---

### C) Modo Administrador: Gestión de Catálogo e Inventario
- **Ruta Web:** `GET /admin-panel/`
- **URL:** `http://localhost:8001/admin-panel/`

Interfaz web interactiva para el perfil de Administrador donde es posible:
1. **Ingresar nuevos productos**: Nombre, Categoría, Cantidad en Stock y Precio unitario en CLP.
2. **Visualizar métricas de inventario**: Total de productos, unidades acumuladas, valorización monetaria total del stock y alerta de stock crítico ($\le 5$ unidades).
3. **Administrar catálogo**: Listado con badges de disponibilidad y botón de eliminación directa.

---

### D) API REST de Productos
- **`GET /api/productos/`**: Retorna el catálogo completo de productos en formato JSON.
- **`POST /api/productos/`**: Registra un nuevo producto mediante payload JSON o Form-Data.
  ```json
  {
    "nombre": "Café Grano 250g",
    "categoria": "Cafetería",
    "cantidad": 12,
    "precio": 3500
  }
  ```
- **`DELETE /api/productos/<id>/`**: Elimina un producto por su identificador único.

---

### E) Panel Web de Resumen KioskBridge (Modo Kiosco)
- **Ruta:** `GET /`
- **URL:** `http://localhost:8001/`

Renderiza la interfaz web con el historial de transacciones procesadas desde `datos.json`.

---

## 📁 Estructura del Proyecto

```
moodle-python-bridge/
├── Dockerfile               # Imagen de contenedor para la API Django
├── requirements.txt         # Dependencias Python (Django, requests, decouple, etc.)
├── .env.example             # Plantilla de variables de entorno
├── .env                     # Variables de entorno activas
├── manage.py                # Entrada administrativa de Django
├── README.md                # Esta documentación
├── datos.json               # Persistencia JSON de transacciones
├── solucion.py              # CLI de evaluación de stock
├── templates/
│   └── resumen.html         # Plantilla visual del panel de transacciones
└── kioskbridge/
    ├── __init__.py
    ├── settings.py          # Configuración Django, Moodle y MongoDB
    ├── urls.py              # Enrutamiento (/api/moodle/usuarios/, /api/moodle/status/, /)
    ├── views.py             # Lógica de consumo REST con requests y panel resumen
    └── wsgi.py              # Punto de entrada WSGI
```

---

## 🛠️ Comandos de Mantenimiento Útiles

```bash
# Ver logs en tiempo real de todos los servicios
docker compose logs -f

# Ver logs únicamente del servicio Django
docker compose logs -f django

# Detener los contenedores sin eliminar volúmenes
docker compose stop

# Detener y eliminar los contenedores manteniendo los datos en volúmenes
docker compose down

# Eliminar contenedores Y volúmenes (reinicio completo desde cero)
docker compose down -v

# Ejecutar el check de Django dentro del contenedor
docker compose exec django python manage.py check
```

---

## 📄 Licencia

Este proyecto y su código fuente están bajo la [Licencia MIT](LICENSE). 
El autor ("Velvyn") permite el uso comercial, modificación y distribución, siempre que se mantenga el aviso de copyright y la exención de garantía presentes en el archivo de licencia.

## ⚠️ Aviso Legal

Este software se proporciona "AS IS" (tal cual), sin garantías de ningún tipo.
Dado que funciona como middleware o proxy que puede manejar transacciones críticas, el consumidor o integrador asume total y exclusiva responsabilidad al utilizar y exponer estos endpoints en entornos de producción. El autor no se hace responsable por ninguna pérdida de datos, interrupciones del servicio, o cualquier otro fallo derivado del uso de este software.
