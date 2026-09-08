from django.urls import path
from kioskbridge.views import (
    resumen,
    admin_productos,
    api_productos,
    api_producto_detalle,
    moodle_users,
    moodle_status
)

urlpatterns = [
    # Panel Modo Kiosco (Resumen de Transacciones)
    path('', resumen, name='resumen'),

    # Panel Modo Administrador (Gestión de Productos e Inventario)
    path('admin-panel/', admin_productos, name='admin_productos'),

    # API REST de Productos
    path('api/productos/', api_productos, name='api_productos'),
    path('api/productos/<int:producto_id>/', api_producto_detalle, name='api_producto_detalle'),

    # API REST Puente Moodle
    path('api/moodle/usuarios/', moodle_users, name='moodle_users'),
    path('api/moodle/status/', moodle_status, name='moodle_status'),
]
