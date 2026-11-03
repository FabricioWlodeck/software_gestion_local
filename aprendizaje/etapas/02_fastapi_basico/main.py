"""
Etapa 02 - La misma API de la etapa 01, ahora con FastAPI.

Las rutas, los campos y los códigos son los mismos que en ../01_http/servidor.py,
pero el ruteo, la lectura del JSON, la validación y la conversión de la respuesta
las hace FastAPI a partir de las anotaciones de tipo.

Ejecutar:  fastapi dev main.py
Probar:    http://127.0.0.1:8000/docs   o   python ../01_http/cliente.py
"""

from decimal import Decimal
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

# Igual que en la etapa 01: un texto fijo para ver cómo viaja el header. El módulo 06 lo reemplaza.
TOKEN_DE_PRUEBA = "token-de-prueba-123"

app = FastAPI(title="Punto Lácteo · etapa 02", version="0.2.0")


# ---------- Schemas: la forma de los datos que entran y salen ----------

class ProductoIn(BaseModel):
    """Lo que el cliente envía para crear un producto."""
    nombre: str = Field(min_length=1, max_length=80)
    unidad: Literal["kg", "unidad"]
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class ProductoOut(ProductoIn):
    """Lo que el servidor devuelve: los mismos campos más el id asignado."""
    id: int


# ---------- "Base de datos" en memoria, igual que en la etapa 01 ----------

productos: dict[int, ProductoOut] = {
    1: ProductoOut(id=1, nombre="Queso cremoso", unidad="kg", precio=Decimal("12500.00")),
    2: ProductoOut(id=2, nombre="Leche entera 1 L", unidad="unidad", precio=Decimal("1450.00")),
    3: ProductoOut(id=3, nombre="Salame milán", unidad="kg", precio=Decimal("18900.00")),
}
proximo_id = 4


# ---------- Rutas: cada decorador asocia un método y una ruta con una función ----------

@app.get("/productos")
def listar_productos(unidad: Literal["kg", "unidad"] | None = None) -> list[ProductoOut]:
    """Lista los productos. El parámetro de consulta ?unidad=kg filtra por unidad."""
    if unidad is None:
        return list(productos.values())
    return [producto for producto in productos.values() if producto.unidad == unidad]


@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int) -> ProductoOut:
    """Devuelve un producto por su id."""
    if producto_id not in productos:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return productos[producto_id]


@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoIn, response: Response) -> ProductoOut:
    """Crea un producto. Si el cuerpo no cumple ProductoIn, FastAPI responde 422 sin ejecutar esto."""
    global proximo_id
    producto = ProductoOut(id=proximo_id, **datos.model_dump())
    productos[producto.id] = producto
    proximo_id += 1
    response.headers["Location"] = f"/productos/{producto.id}"
    return producto


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_producto(producto_id: int, authorization: Annotated[str | None, Header()] = None) -> None:
    """Borra un producto. Exige el header Authorization: Bearer <token>."""
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Falta el header Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if authorization != f"Bearer {TOKEN_DE_PRUEBA}":
        raise HTTPException(status_code=401, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
    if productos.pop(producto_id, None) is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
