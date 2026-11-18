"""El empleado no puede usar las rutas de la dueña ni operar en otra sucursal."""

import pytest

from tests.ayudas import abrir_caja, vender


@pytest.mark.parametrize(
    ("metodo", "ruta", "cuerpo"),
    [
        ("get", "/compras", None),
        ("post", "/compras", {"proveedor_id": 1, "sucursal_id": 1, "items": [
            {"producto_id": 1, "cantidad": "1", "costo_unitario": "100"}]}),
        ("post", "/ventas/1/anular", {"motivo": "error"}),
        ("post", "/ventas/1/confirmar", {}),
        ("post", "/stock/traspasos", {"producto_id": 1, "origen_id": 1, "destino_id": 2, "cantidad": "1"}),
        ("post", "/productos", {"nombre": "Nuevo", "unidad": "kg", "modo_precio": "manual", "precio": "100"}),
        ("patch", "/productos/1", {"precio": "100"}),
        ("put", "/productos/1/minimos", {"1": "1.000"}),
        ("get", "/usuarios", None),
        ("post", "/usuarios", {"nombre_usuario": "x", "nombre": "X", "contrasena": "123456", "rol": "duenio"}),
        ("patch", "/usuarios/1", {"nombre": "X"}),
        ("put", "/usuarios/1/contrasena", {"contrasena": "1234567"}),
        ("get", "/reportes/resumen?desde=2026-11-01&hasta=2026-11-30", None),
        ("get", "/reportes/ventas-diarias?desde=2026-11-01&hasta=2026-11-30", None),
        ("get", "/proveedores", None),
        ("get", "/cajas", None),
        ("patch", "/sucursales/1", {"nombre": "Otra"}),
    ],
)
def test_empleado_403_en_rutas_de_duenia(cliente, h_bruno, metodo, ruta, cuerpo):
    respuesta = cliente.request(metodo, ruta, json=cuerpo, headers=h_bruno)
    assert respuesta.status_code == 403
    assert respuesta.json() == {"detail": "No tenés permiso para esta acción"}


def test_empleado_403_operando_en_otra_sucursal(cliente, h_bruno, h_carla, datos):
    otra = datos.s2
    assert cliente.post("/cajas", json={"sucursal_id": otra, "fondo_inicial": "0"}, headers=h_bruno).status_code == 403
    assert cliente.get(f"/cajas/actual?sucursal_id={otra}", headers=h_bruno).status_code == 403
    assert cliente.get(f"/stock?sucursal_id={otra}", headers=h_bruno).status_code == 403
    assert cliente.get(f"/stock/movimientos?sucursal_id={otra}", headers=h_bruno).status_code == 403
    assert cliente.get(f"/ventas?sucursal_id={otra}", headers=h_bruno).status_code == 403
    merma = {"sucursal_id": otra, "producto_id": datos.queso, "tipo": "merma", "cantidad": "0.100", "motivo": "x"}
    assert cliente.post("/stock/movimientos", json=merma, headers=h_bruno).status_code == 403
    vender(cliente, h_bruno, [(datos.queso, "0.100")], sucursal_id=otra, esperado=403)

    # Sobre cosas de la otra sucursal: la caja y la venta de Carla.
    caja = abrir_caja(cliente, h_carla)
    venta = vender(cliente, h_carla, [(datos.leche, "1")])
    assert cliente.get(f"/ventas/{venta['id']}", headers=h_bruno).status_code == 403
    assert cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "x"}, headers=h_bruno).status_code == 403
    cerrar = cliente.post(f"/cajas/{caja['id']}/cerrar", json={"efectivo_contado": "0"}, headers=h_bruno)
    assert cerrar.status_code == 403
    assert cerrar.json() == {"detail": "No tenés permiso para operar en otra sucursal"}


def test_empleado_sin_sucursal_id_usa_la_suya(cliente, h_bruno, datos):
    caja = abrir_caja(cliente, h_bruno)
    assert caja["sucursal_id"] == datos.s1
    stock = cliente.get("/stock", headers=h_bruno)
    assert stock.status_code == 200


def test_duenia_tiene_que_indicar_la_sucursal(cliente, h_duenia, datos):
    respuesta = cliente.post("/cajas", json={"fondo_inicial": "0"}, headers=h_duenia)
    assert respuesta.status_code == 422
    assert "sucursal" in respuesta.json()["detail"]
    assert cliente.get("/stock", headers=h_duenia).status_code == 422
    assert cliente.get("/cajas/actual", headers=h_duenia).status_code == 422
    # En los listados puede omitirla para ver las dos sucursales.
    assert cliente.get("/ventas", headers=h_duenia).status_code == 200
    assert cliente.get("/stock/movimientos", headers=h_duenia).status_code == 200


def test_sucursal_inexistente_404(cliente, h_duenia):
    assert cliente.get("/stock?sucursal_id=999", headers=h_duenia).status_code == 404


def test_productos_para_empleado_sin_costos(cliente, h_bruno, h_duenia):
    empleado = cliente.get("/productos", headers=h_bruno).json()
    duenia = cliente.get("/productos", headers=h_duenia).json()
    assert len(empleado) == len(duenia) == 2
    for producto in empleado:
        assert not {"modo_precio", "margen", "costo_ultimo"} & producto.keys()
        assert {"id", "nombre", "unidad", "precio", "activo", "stock"} == producto.keys()
    queso = next(p for p in duenia if p["nombre"] == "Queso cremoso")
    assert queso["modo_precio"] == "margen"
    assert queso["margen"] == "35.00"
    assert queso["costo_ultimo"] == "9259.26"
    assert queso["precio"] == "12500.00"
    primera = queso["stock"][0]
    assert primera == {"sucursal_id": primera["sucursal_id"], "cantidad": "5.000", "minimo": "2.000"}
    leche = next(p for p in duenia if p["nombre"] == "Leche entera 1 L")
    assert leche["costo_ultimo"] is None and leche["margen"] is None


def test_errores_siempre_con_detail_en_texto(cliente, h_duenia, datos):
    ruta = cliente.get("/no-existe", headers=h_duenia)
    assert ruta.status_code == 404
    assert ruta.json() == {"detail": "No existe la ruta pedida"}
    venta = cliente.post("/ventas", json={"medio_pago": "efectivo", "items": [
        {"producto_id": datos.queso, "cantidad": "1"}]}, headers=h_duenia)
    assert venta.status_code == 422
    assert venta.json() == {"detail": "Indicá la sucursal (sucursal_id)"}
    login = cliente.post("/auth/token", data={})
    assert login.status_code == 422
    assert isinstance(login.json()["detail"], str)
