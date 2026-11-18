from decimal import Decimal

from app import models
from tests.ayudas import movimientos, stock_de


def test_compra_suma_stock_actualiza_costo_y_recalcula_precio_margen(cliente, h_duenia, sesion, datos):
    respuesta = cliente.post(
        "/compras",
        json={"proveedor_id": datos.proveedor, "sucursal_id": datos.s1, "comprobante": "R-0012", "items": [
            {"producto_id": datos.queso, "cantidad": "10", "costo_unitario": "9800.00"},
            {"producto_id": datos.leche, "cantidad": "24", "costo_unitario": "1100.00"},
        ]},
        headers=h_duenia,
    )
    assert respuesta.status_code == 201, respuesta.text
    compra = respuesta.json()
    assert compra["proveedor"] == "Lácteos del Sur"
    assert compra["usuario"] == "Ana"
    assert compra["comprobante"] == "R-0012"
    assert compra["total"] == "124400.00"  # 98.000 + 26.400
    queso = next(item for item in compra["items"] if item["producto_id"] == datos.queso)
    assert queso == {"producto_id": datos.queso, "producto": "Queso cremoso", "unidad": "kg",
                     "cantidad": "10.000", "costo_unitario": "9800.00", "subtotal": "98000.00"}

    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("15.000")
    assert stock_de(sesion, datos.leche, datos.s1) == Decimal("34.000")
    entradas = movimientos(sesion, compra_id=compra["id"])
    assert {(m.producto_id, m.tipo, m.cantidad) for m in entradas} == {
        (datos.queso, "compra", Decimal("10.000")), (datos.leche, "compra", Decimal("24.000")),
    }

    sesion.rollback()  # foto nueva de la base (ver ayudas._foto_nueva)
    queso_db = sesion.get(models.Producto, datos.queso)
    assert queso_db.costo_ultimo == Decimal("9800.00")
    assert queso_db.precio == Decimal("13230.00")  # 9800 × 1,35
    leche_db = sesion.get(models.Producto, datos.leche)
    assert leche_db.costo_ultimo == Decimal("1100.00")
    assert leche_db.precio == Decimal("1450.00")  # manual: no cambia

    listado = cliente.get(f"/compras?proveedor_id={datos.proveedor}", headers=h_duenia).json()
    assert [c["id"] for c in listado] == [compra["id"]]


def test_compra_validaciones(cliente, h_duenia, datos):
    base = {"proveedor_id": datos.proveedor, "sucursal_id": datos.s1}
    repetido = {**base, "items": [{"producto_id": datos.queso, "cantidad": "1", "costo_unitario": "1"}] * 2}
    assert cliente.post("/compras", json=repetido, headers=h_duenia).status_code == 422
    fraccion = {**base, "items": [{"producto_id": datos.leche, "cantidad": "1.5", "costo_unitario": "1"}]}
    assert cliente.post("/compras", json=fraccion, headers=h_duenia).status_code == 422
    sin_proveedor = {**base, "proveedor_id": 999, "items": [
        {"producto_id": datos.queso, "cantidad": "1", "costo_unitario": "1"}]}
    assert cliente.post("/compras", json=sin_proveedor, headers=h_duenia).status_code == 404


def test_producto_nuevo_crea_stock_en_todas_las_sucursales(cliente, h_duenia, datos):
    respuesta = cliente.post(
        "/productos",
        json={"nombre": "Salame milán", "unidad": "kg", "modo_precio": "margen", "margen": "40",
              "costo_ultimo": "13500", "minimos": {str(datos.s1): "1.000"}},
        headers=h_duenia,
    )
    assert respuesta.status_code == 201, respuesta.text
    producto = respuesta.json()
    assert producto["precio"] == "18900.00"
    assert producto["margen"] == "40.00"
    assert producto["stock"] == [
        {"sucursal_id": datos.s1, "cantidad": "0.000", "minimo": "1.000"},
        {"sucursal_id": datos.s2, "cantidad": "0.000", "minimo": "0.000"},
    ]

    # Nombre repetido → 409; modo manual sin precio → 422; margen sin costo ni precio → 422.
    repetido = {"nombre": "Salame milán", "unidad": "kg", "modo_precio": "manual", "precio": "1"}
    assert cliente.post("/productos", json=repetido, headers=h_duenia).status_code == 409
    sin_precio = {"nombre": "Otro", "unidad": "kg", "modo_precio": "manual"}
    assert cliente.post("/productos", json=sin_precio, headers=h_duenia).status_code == 422
    margen_sin_costo = {"nombre": "Otro", "unidad": "kg", "modo_precio": "margen", "margen": "30"}
    assert cliente.post("/productos", json=margen_sin_costo, headers=h_duenia).status_code == 422
    margen_con_precio = {**margen_sin_costo, "precio": "5000"}
    assert cliente.post("/productos", json=margen_con_precio, headers=h_duenia).status_code == 201


def test_editar_producto_y_minimos(cliente, h_duenia, datos):
    editado = cliente.patch(f"/productos/{datos.queso}", json={"margen": "50"}, headers=h_duenia)
    assert editado.status_code == 200
    assert editado.json()["precio"] == "13888.89"  # 9259,26 × 1,5

    manual = cliente.patch(f"/productos/{datos.queso}", json={"modo_precio": "manual", "precio": "12000"},
                           headers=h_duenia)
    assert manual.json()["precio"] == "12000.00"

    assert cliente.put(f"/productos/{datos.queso}/minimos", json={str(datos.s2): "2.500"},
                       headers=h_duenia).status_code == 204
    productos = cliente.get("/productos?buscar=queso", headers=h_duenia).json()
    assert len(productos) == 1
    assert productos[0]["stock"][1] == {"sucursal_id": datos.s2, "cantidad": "3.000", "minimo": "2.500"}

    inactivo = cliente.patch(f"/productos/{datos.leche}", json={"activo": False}, headers=h_duenia)
    assert inactivo.json()["activo"] is False
    assert len(cliente.get("/productos", headers=h_duenia).json()) == 1
    assert len(cliente.get("/productos?incluir_inactivos=true", headers=h_duenia).json()) == 2
    assert cliente.put(f"/productos/{datos.queso}/minimos", json={"999": "1"}, headers=h_duenia).status_code == 404


def test_proveedores(cliente, h_duenia):
    creado = cliente.post("/proveedores", json={"nombre": "Fiambres La Colonia", "telefono": "", "email": "a@b.c"},
                          headers=h_duenia)
    assert creado.status_code == 201
    assert creado.json() == {"id": creado.json()["id"], "nombre": "Fiambres La Colonia", "telefono": None,
                             "email": "a@b.c", "notas": None, "activo": True}
    proveedor_id = creado.json()["id"]
    assert cliente.post("/proveedores", json={"nombre": "Fiambres La Colonia"}, headers=h_duenia).status_code == 409
    editado = cliente.patch(f"/proveedores/{proveedor_id}", json={"activo": False, "notas": "cerró"},
                            headers=h_duenia)
    assert editado.json()["activo"] is False and editado.json()["notas"] == "cerró"
    assert len(cliente.get("/proveedores", headers=h_duenia).json()) == 1
    assert len(cliente.get("/proveedores?incluir_inactivos=true", headers=h_duenia).json()) == 2
