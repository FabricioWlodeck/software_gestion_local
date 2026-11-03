"""
Usa el service de ventas directamente, sin HTTP ni FastAPI.

Así lo usaría un script de carga masiva o un bot: las reglas del negocio
están en el service, no en las rutas, y por eso se pueden reutilizar.

Ejecutar desde la carpeta de la etapa:  python probar_service.py
"""

from decimal import Decimal

from app.errores import ErrorDeNegocio
from app.repositories.memoria import RepositorioProductos, RepositorioVentas
from app.schemas.venta import ItemVentaIn, VentaIn
from app.services.ventas import ServicioVentas

servicio = ServicioVentas(RepositorioProductos(), RepositorioVentas())

pedidos = {
    "0,350 kg de queso y 2 leches": [ItemVentaIn(producto_id=1, cantidad=Decimal("0.350")),
                                     ItemVentaIn(producto_id=2, cantidad=Decimal("2"))],
    "3 kg de queso (hay 1,750 kg)": [ItemVentaIn(producto_id=1, cantidad=Decimal("3"))],
    "1,5 leches": [ItemVentaIn(producto_id=2, cantidad=Decimal("1.5"))],
}

for descripcion, items in pedidos.items():
    try:
        venta = servicio.registrar(VentaIn(items=items))
        print(f"{descripcion}: venta {venta.id} registrada, total ${venta.total}")
    except ErrorDeNegocio as error:
        print(f"{descripcion}: rechazada ({type(error).__name__}: {error})")
