from decimal import Decimal

from sqlalchemy.orm import Session

from app.errores import Conflicto, NoEncontrado
from app.models import Producto, Usuario
from app.repositories.productos import RepositorioProductos
from app.repositories.stock import RepositorioStock
from app.repositories.sucursales import RepositorioSucursales
from app.schemas.producto import ProductoCrear, ProductoDuenio, ProductoEditar, ProductoEmpleado, StockDeSucursal
from app.services.permisos import es_duenio
from app.services.precios import calcular_precio


def producto_para(usuario: Usuario, producto: Producto) -> ProductoDuenio | ProductoEmpleado:
    """Regla 12: el empleado no ve costos ni márgenes."""
    stock = [
        StockDeSucursal(sucursal_id=fila.sucursal_id, cantidad=fila.cantidad, minimo=fila.minimo)
        for fila in sorted(producto.stocks, key=lambda fila: fila.sucursal_id)
    ]
    comunes = dict(
        id=producto.id, nombre=producto.nombre, unidad=producto.unidad, precio=producto.precio,
        activo=producto.activo, stock=stock,
    )
    if es_duenio(usuario):
        return ProductoDuenio(
            **comunes, modo_precio=producto.modo_precio, margen=producto.margen, costo_ultimo=producto.costo_ultimo
        )
    return ProductoEmpleado(**comunes)


class ServicioProductos:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.productos = RepositorioProductos(sesion)
        self.stock = RepositorioStock(sesion)
        self.sucursales = RepositorioSucursales(sesion)

    def _obtener(self, producto_id: int) -> Producto:
        producto = self.productos.obtener(producto_id)
        if producto is None:
            raise NoEncontrado("el producto", producto_id)
        return producto

    def _validar_sucursales(self, minimos: dict[int, Decimal]) -> None:
        existentes = {sucursal.id for sucursal in self.sucursales.listar()}
        for sucursal_id in minimos:
            if sucursal_id not in existentes:
                raise NoEncontrado("la sucursal", sucursal_id)

    def _aplicar_minimos(self, producto: Producto, minimos: dict[int, Decimal]) -> None:
        self._validar_sucursales(minimos)
        filas = {fila.sucursal_id: fila for fila in self.productos.stock_del_producto(producto.id)}
        for sucursal_id, minimo in minimos.items():
            if sucursal_id in filas:
                filas[sucursal_id].minimo = minimo
            else:
                self.stock.crear(producto.id, sucursal_id, minimo)

    def listar(self, usuario: Usuario, incluir_inactivos: bool, buscar: str | None):
        productos = self.productos.listar(incluir_inactivos, buscar.strip() if buscar else None)
        return [producto_para(usuario, producto) for producto in productos]

    def crear(self, usuario: Usuario, datos: ProductoCrear) -> ProductoDuenio:
        if self.productos.existe_nombre(datos.nombre):
            raise Conflicto(f"Ya existe un producto llamado {datos.nombre}")
        minimos = datos.minimos or {}
        self._validar_sucursales(minimos)
        producto = self.productos.agregar(
            Producto(
                nombre=datos.nombre,
                unidad=datos.unidad,
                modo_precio=datos.modo_precio,
                margen=datos.margen,
                costo_ultimo=datos.costo_ultimo,
                precio=calcular_precio(datos.modo_precio, datos.margen, datos.costo_ultimo, datos.precio),
            )
        )
        # Regla 11: una fila de stock en cero para cada sucursal, con su mínimo (0 por defecto).
        for sucursal in self.sucursales.listar():
            self.stock.crear(producto.id, sucursal.id, minimos.get(sucursal.id, Decimal("0.000")))
        self.sesion.commit()
        self.sesion.refresh(producto, ["stocks"])
        return producto_para(usuario, producto)

    def editar(self, usuario: Usuario, producto_id: int, datos: ProductoEditar) -> ProductoDuenio:
        producto = self._obtener(producto_id)
        cambios = datos.model_dump(exclude_unset=True)
        nombre = cambios.get("nombre")
        if nombre is not None and nombre != producto.nombre:
            if self.productos.existe_nombre(nombre, salvo_id=producto.id):
                raise Conflicto(f"Ya existe un producto llamado {nombre}")
            producto.nombre = nombre
        for campo in ("unidad", "modo_precio", "activo"):
            if cambios.get(campo) is not None:
                setattr(producto, campo, cambios[campo])
        for campo in ("margen", "costo_ultimo"):  # aceptan null para borrarlos
            if campo in cambios:
                setattr(producto, campo, cambios[campo])
        precio_pedido = cambios.get("precio") or producto.precio
        producto.precio = calcular_precio(producto.modo_precio, producto.margen, producto.costo_ultimo, precio_pedido)
        if cambios.get("minimos"):
            self._aplicar_minimos(producto, cambios["minimos"])
        self.sesion.commit()
        self.sesion.refresh(producto, ["stocks"])
        return producto_para(usuario, producto)

    def fijar_minimos(self, producto_id: int, minimos: dict[int, Decimal]) -> None:
        producto = self._obtener(producto_id)
        self._aplicar_minimos(producto, minimos)
        self.sesion.commit()
