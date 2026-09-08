@echo off
chcp 65001 >nul
title KioskBridge - Inicio del Ecosistema Docker

echo ==============================================================================
echo           INICIANDO ECOSISTEMA KIOSKBRIDGE & MOODLE (DOCKER)
echo ==============================================================================
echo.

:: 1. Verificar si existe el archivo .env, si no, crearlo desde .env.example
if not exist ".env" (
    echo [INFO] No se encontro el archivo .env. Creando uno a partir de .env.example...
    copy .env.example .env >nul
    if %errorlevel% equ 0 (
        echo [OK] Archivo .env generado exitosamente.
    ) else (
        echo [ERROR] No se pudo crear el archivo .env. Asegurate de que .env.example exista.
        pause
        exit /b 1
    )
) else (
    echo [OK] Archivo .env detectado.
)

echo.
:: 2. Verificar si Docker está instalado y en ejecución
echo [INFO] Comprobando disponibilidad de Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker no esta en ejecucion o no esta instalado.
    echo Por favor abre Docker Desktop y vuelve a ejecutar este script.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker esta en ejecucion.
echo.

:: 3. Construir y levantar contenedores
echo [INFO] Construyendo y levantando contenedores en segundo plano...
echo ------------------------------------------------------------------------------
docker compose up -d --build
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un error al ejecutar 'docker compose up'.
    echo Revisa los mensajes anteriores para mas detalles.
    echo.
    pause
    exit /b 1
)

echo ------------------------------------------------------------------------------
echo [OK] Todos los servicios han sido iniciados correctamente.
echo.

:: 4. Resumen de URLs y accesos
echo ==============================================================================
echo                             SERVICIOS DISPONIBLES
echo ==============================================================================
echo  - Modo Kiosco (Resumen):     http://localhost:8001/
echo  - Modo Admin (Productos):     http://localhost:8001/admin-panel/
echo  - API REST de Productos:      http://localhost:8001/api/productos/
echo  - Endpoint Moodle (Mock):     http://localhost:8001/api/moodle/usuarios/?mock=true
echo  - Diagnostico Moodle:         http://localhost:8001/api/moodle/status/
echo  - Plataforma Moodle:          http://localhost:8080/
echo    * Usuario Admin Moodle:     admin
echo    * Password Admin Moodle:    Moodle123!
echo  - Base de Datos MongoDB:      localhost:27017
echo  - Base de Datos MySQL:        localhost:3306
echo ==============================================================================
echo.
echo Presiona cualquier tecla para ver los logs en tiempo real (Ctrl + C para salir de los logs)...
pause >nul
docker compose logs -f

