from decimal import Decimal

from app import models
from tests.ayudas import abrir_caja, movimientos, notificaciones, stock_de, vender


def test_venta_descuenta_stock_y_crea_movimientos(cliente, h_bruno, sesion, datos):
    caja = abrir_caja(cliente, h_bruno)
    venta = vender(cliente, h_bruno, [(datos.queso, "0.350"), (datos.leche, "2"), (datos.queso, "0.150")])

    # Las líneas del mismo producto se suman: 0,500 kg de queso.
    assert venta["sucursal_id"] == datos.s1
    assert venta["caja_id"] == caja["id"]
    assert venta["usuario_id"] == datos.bruno
    assert venta["usuario"] == "Bruno"
    assert venta["estado"] == "valida"
    items = {item["producto_id"]: item for item in venta["items"]}
    assert items[datos.queso] == {
        "producto_id": datos.queso, "producto": "Queso cremoso", "unidad": "kg", "cantidad": "0.500",
        "precio_unitario": "12500.00", "subtotal": "6250.00",
    }
    assert items[datos.leche]["subtotal"] == "2900.00"
    assert venta["total"] == "9150.00"
    assert "T" in venta["fecha"] and "+" not in venta["fecha"]  # ISO 8601 sin zona

    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("4.500")
    assert stock_de(sesion, datos.leche, datos.s1) == Decimal("8.000")
    assert stock_de(sesion, datos.queso, datos.s2) == Decimal("3.000")  # la otra sucursal no cambia

    libro = movimientos(sesion, venta_id=venta["id"])
    assert [(m.producto_id, m.tipo, m.cantidad, m.saldo_resultante) for m in libro] == [
        (datos.queso, "venta", Decimal("-0.500"), Decimal("4.500")),
        (datos.leche, "venta", Decimal("-2.000"), Decimal("8.000")),
    ]

    # Y se puede leer por la API.
    respuesta = cliente.get(f"/stock/movimientos?producto_id={datos.queso}", headers=h_bruno).json()
    assert respuesta[0]["tipo"] == "venta"
    assert respuesta[0]["cantidad"] == "-0.500"
    assert respuesta[0]["usuario"] == "Bruno"
    assert respuesta[0]["venta_id"] == venta["id"]


def test_venta_redondea_el_subtotal(cliente, h_bruno, datos):
    abrir_caja(cliente, h_bruno)
    venta = vender(cliente, h_bruno, [(datos.queso, "0.333")])
    assert venta["total"] == "4162.50"  # 0,333 × 12500 = 4162,5


def test_no_se_puede_vender_sin_caja_abierta(cliente, h_bruno, sesion, datos):
    respuesta = cliente.post(
        "/ventas", json={"medio_pago": "efectivo", "items": [{"producto_id": datos.queso, "cantidad": "1"}]},
        headers=h_bruno,
    )
    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "La caja de la sucursal está cerrada"}
    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("5.000")


def test_producto_por_unidad_exige_cantidad_entera(cliente, h_bruno, sesion, datos):
    abrir_caja(cliente, h_bruno)
    respuesta = cliente.post(
        "/ventas", json={"medio_pago": "efectivo", "items": [{"producto_id": datos.leche, "cantidad": "1.5"}]},
        headers=h_bruno,
    )
    assert respuesta.status_code == 422
    assert "entera" in respuesta.json()["detail"]
    assert stock_de(sesion, datos.leche, datos.s1) == Decimal("10.000")


def test_stock_insuficiente_409_y_no_guarda_nada(cliente, h_bruno, sesion, datos):
    abrir_caja(cliente, h_bruno)
    respuesta = cliente.post(
        "/ventas",
        json={"medio_pago": "efectivo", "items": [
            {"producto_id": datos.leche, "cantidad": "1"}, {"producto_id": datos.queso, "cantidad": "5.001"}]},
        headers=h_bruno,
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "Stock insuficiente de Queso cremoso en Sucursal 1: hay 5,000 kg y se pidieron 5,001 kg"
    )
    # La transacción se descartó entera: ni la venta, ni la leche descontada, ni movimientos.
    assert stock_de(sesion, datos.leche, datos.s1) == Decimal("10.000")
    assert sesion.query(models.Venta).count() == 0
    assert movimientos(sesion, tipo="venta") == []


def test_validaciones_de_la_venta(cliente, h_bruno, datos):
    abrir_caja(cliente, h_bruno)
    sin_items = cliente.post("/ventas", json={"medio_pago": "efectivo", "items": []}, headers=h_bruno)
    assert sin_items.status_code == 422
    assert isinstance(sin_items.json()["detail"], str)
    negativa = cliente.post(
        "/ventas", json={"medio_pago": "efectivo", "items": [{"producto_id": datos.queso, "cantidad": "-1"}]},
        headers=h_bruno,
    )
    assert negativa.status_code == 422
    assert negativa.json()["detail"] == "Datos inválidos: items.0.cantidad: tiene que ser mayor que 0"
    medio = cliente.post(
        "/ventas", json={"medio_pago": "tarjeta", "items": [{"producto_id": datos.queso, "cantidad": "1"}]},
        headers=h_bruno,
    )
    assert medio.status_code == 422
    inexistente = cliente.post(
        "/ventas", json={"medio_pago": "efectivo", "items": [{"producto_id": 9999, "cantidad": "1"}]},
        headers=h_bruno,
    )
    assert inexistente.status_code == 404


def test_producto_inactivo_no_se_vende(cliente, h_bruno, h_duenia, datos):
    abrir_caja(cliente, h_bruno)
    cliente.patch(f"/productos/{datos.leche}", json={"activo": False}, headers=h_duenia)
    vender(cliente, h_bruno, [(datos.leche, "1")], esperado=409)


def test_observar_genera_notificacion(cliente, h_bruno, sesion, datos):
    abrir_caja(cliente, h_bruno)
    venta = vender(cliente, h_bruno, [(datos.queso, "1")])
    respuesta = cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "cobró de más"}, headers=h_bruno)
    assert respuesta.status_code == 200
    observada = respuesta.json()
    assert observada["estado"] == "observada"
    assert observada["motivo_observacion"] == "cobró de más"
    assert observada["observada_por"] == "Bruno"
    assert observada["observada_en"] is not None

    avisos = notificaciones(sesion, "venta_observada")
    assert len(avisos) == 1
    assert avisos[0].sucursal_id == datos.s1
    assert avisos[0].mensaje == f"👀 Venta {venta['id']} observada en Sucursal 1 por Bruno: cobró de más."
    # Observar no devuelve stock.
    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("4.000")

    # No se puede observar dos veces, y el motivo es obligatorio.
    otra = cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "otra vez"}, headers=h_bruno)
    assert otra.status_code == 409
    sin_motivo = cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "  "}, headers=h_bruno)
    assert sin_motivo.status_code == 422


def test_confirmar_venta_observada(cliente, h_bruno, h_duenia, datos):
    abrir_caja(cliente, h_bruno)
    venta = vender(cliente, h_bruno, [(datos.queso, "1")])
    # Solo se confirma una venta observada.
    assert cliente.post(f"/ventas/{venta['id']}/confirmar", headers=h_duenia).status_code == 409

    cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "revisar"}, headers=h_bruno)
    respuesta = cliente.post(f"/ventas/{venta['id']}/confirmar", json={"motivo": "estaba bien"}, headers=h_duenia)
    assert respuesta.status_code == 200
    confirmada = respuesta.json()
    assert confirmada["estado"] == "valida"
    assert confirmada["motivo_resolucion"] == "estaba bien"
    assert confirmada["resuelta_por"] == "Ana"
    assert confirmada["resuelta_en"] is not None
    assert confirmada["motivo_observacion"] == "revisar"  # queda el historial

    # El cuerpo es opcional.
    cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "de nuevo"}, headers=h_bruno)
    assert cliente.post(f"/ventas/{venta['id']}/confirmar", headers=h_duenia).status_code == 200


def test_anular_devuelve_stock_con_movimientos_anulacion(cliente, h_bruno, h_duenia, sesion, datos):
    abrir_caja(cliente, h_bruno)
    venta = vender(cliente, h_bruno, [(datos.queso, "1.250"), (datos.leche, "3")])
    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("3.750")

    respuesta = cliente.post(f"/ventas/{venta['id']}/anular", json={"motivo": "cliente arrepentido"},
                             headers=h_duenia)
    assert respuesta.status_code == 200
    anulada = respuesta.json()
    assert anulada["estado"] == "anulada"
    assert anulada["motivo_resolucion"] == "cliente arrepentido"
    assert anulada["resuelta_por"] == "Ana"

    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("5.000")
    assert stock_de(sesion, datos.leche, datos.s1) == Decimal("10.000")
    devueltos = movimientos(sesion, venta_id=venta["id"], tipo="anulacion")
    assert [(m.producto_id, m.cantidad, m.saldo_resultante) for m in devueltos] == [
        (datos.queso, Decimal("1.250"), Decimal("5.000")),
        (datos.leche, Decimal("3.000"), Decimal("10.000")),
    ]
    assert all(m.motivo and "cliente arrepentido" in m.motivo for m in devueltos)

    # Ya anulada: 409, y el motivo es obligatorio.
    assert cliente.post(f"/ventas/{venta['id']}/anular", json={"motivo": "x"}, headers=h_duenia).status_code == 409
    otra = vender(cliente, h_bruno, [(datos.leche, "1")])
    assert cliente.post(f"/ventas/{otra['id']}/anular", json={}, headers=h_duenia).status_code == 422


def test_anular_una_venta_observada(cliente, h_bruno, h_duenia, datos):
    abrir_caja(cliente, h_bruno)
    venta = vender(cliente, h_bruno, [(datos.leche, "1")])
    cliente.post(f"/ventas/{venta['id']}/observar", json={"motivo": "duplicada"}, headers=h_bruno)
    respuesta = cliente.post(f"/ventas/{venta['id']}/anular", json={"motivo": "era duplicada"}, headers=h_duenia)
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "anulada"


def test_listar_ventas(cliente, h_bruno, h_carla, h_duenia, datos):
    abrir_caja(cliente, h_bruno)
    abrir_caja(cliente, h_carla)
    primera = vender(cliente, h_bruno, [(datos.leche, "1")])
    segunda = vender(cliente, h_bruno, [(datos.leche, "2")], medio="transferencia")
    vender(cliente, h_carla, [(datos.leche, "1")])

    propias = cliente.get("/ventas", headers=h_bruno).json()
    assert [v["id"] for v in propias] == [segunda["id"], primera["id"]]  # de la más nueva a la más vieja

    todas = cliente.get("/ventas", headers=h_duenia).json()
    assert len(todas) == 3
    s2 = cliente.get(f"/ventas?sucursal_id={datos.s2}", headers=h_duenia).json()
    assert len(s2) == 1
    hoy = segunda["fecha"][:10]
    rango = cliente.get(f"/ventas?sucursal_id={datos.s1}&desde={hoy}&hasta={hoy}", headers=h_duenia).json()
    assert len(rango) == 2
    assert cliente.get("/ventas?desde=2020-01-01&hasta=2020-01-02", headers=h_duenia).json() == []
    assert len(cliente.get("/ventas?estado=valida&limite=1", headers=h_duenia).json()) == 1
    assert cliente.get(f"/ventas/{primera['id']}", headers=h_bruno).json()["id"] == primera["id"]
    assert cliente.get("/ventas/9999", headers=h_duenia).status_code == 404
