@echo off
chcp 65001 >nul
title KioskBridge - Detener Ecosistema Docker

echo ==============================================================================
echo           DETENIENDO ECOSISTEMA KIOSKBRIDGE & MOODLE (DOCKER)
echo ==============================================================================
echo.
echo [INFO] Deteniendo y removiendo contenedores (los volumenes de datos se conservan)...
docker compose down

echo.
echo [OK] Servicios detenidos exitosamente.
echo.
pause

