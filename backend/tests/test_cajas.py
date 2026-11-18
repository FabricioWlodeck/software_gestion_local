from tests.ayudas import abrir_caja, notificaciones, vender


def test_caja_actual_y_una_sola_abierta_por_sucursal(cliente, h_bruno, h_duenia, datos):
    assert cliente.get("/cajas/actual", headers=h_bruno).json() is None

    caja = abrir_caja(cliente, h_bruno, fondo="10000.00")
    assert caja["estado"] == "abierta"
    assert caja["abierta_por"] == "Bruno"
    assert caja["fondo_inicial"] == "10000.00"
    assert caja["cerrada_por"] is None and caja["diferencia"] is None

    # La dueña no puede abrir otra en la misma sucursal; sí en la otra.
    repetida = cliente.post("/cajas", json={"sucursal_id": datos.s1, "fondo_inicial": "0"}, headers=h_duenia)
    assert repetida.status_code == 409
    abrir_caja(cliente, h_duenia, sucursal_id=datos.s2, fondo="0")


def test_cierre_con_esperado_diferencia_y_notificacion(cliente, h_bruno, h_duenia, sesion, datos):
    caja = abrir_caja(cliente, h_bruno, fondo="10000.00")
    vender(cliente, h_bruno, [(datos.queso, "2")])                         # 25.000 en efectivo
    vender(cliente, h_bruno, [(datos.leche, "2")], medio="transferencia")  # 2.900 por transferencia
    anulada = vender(cliente, h_bruno, [(datos.leche, "4")])               # 5.800 en efectivo, se anula
    observada = vender(cliente, h_bruno, [(datos.leche, "2")])             # 2.900 en efectivo, observada
    cliente.post(f"/ventas/{anulada['id']}/anular", json={"motivo": "error"}, headers=h_duenia)
    cliente.post(f"/ventas/{observada['id']}/observar", json={"motivo": "revisar"}, headers=h_bruno)

    actual = cliente.get("/cajas/actual", headers=h_bruno).json()
    assert actual["id"] == caja["id"]
    assert actual["ventas_efectivo"] == "27900.00"  # las observadas cuentan; las anuladas no
    assert actual["ventas_transferencia"] == "2900.00"
    assert actual["cantidad_ventas"] == 3
    assert actual["efectivo_esperado_actual"] == "37900.00"

    respuesta = cliente.post(
        f"/cajas/{caja['id']}/cerrar", json={"efectivo_contado": "36700.00", "observacion": "faltante"},
        headers=h_bruno,
    )
    assert respuesta.status_code == 200
    cerrada = respuesta.json()
    assert cerrada["estado"] == "cerrada"
    assert cerrada["cerrada_por"] == "Bruno"
    assert cerrada["cerrada_en"] is not None
    assert cerrada["efectivo_esperado"] == "37900.00"
    assert cerrada["efectivo_contado"] == "36700.00"
    assert cerrada["diferencia"] == "-1200.00"
    assert cerrada["observacion"] == "faltante"

    avisos = notificaciones(sesion, "diferencia_caja")
    assert len(avisos) == 1
    assert avisos[0].mensaje == (
        "💵 Caja de Sucursal 1 cerrada con diferencia de −$1.200,00 (esperado $37.900,00, contado $36.700,00)."
    )

    # Ya cerrada: no se vuelve a cerrar ni se puede vender.
    otra = cliente.post(f"/cajas/{caja['id']}/cerrar", json={"efectivo_contado": "1"}, headers=h_bruno)
    assert otra.status_code == 409
    vender(cliente, h_bruno, [(datos.leche, "1")], esperado=409)
    assert cliente.get("/cajas/actual", headers=h_bruno).json() is None

    # La dueña ve el historial.
    historial = cliente.get(f"/cajas?sucursal_id={datos.s1}", headers=h_duenia).json()
    assert [c["id"] for c in historial] == [caja["id"]]


def test_cierre_sin_diferencia_no_avisa(cliente, h_bruno, sesion, datos):
    caja = abrir_caja(cliente, h_bruno, fondo="5000.00")
    vender(cliente, h_bruno, [(datos.leche, "1")])
    cerrada = cliente.post(f"/cajas/{caja['id']}/cerrar", json={"efectivo_contado": "6450"}, headers=h_bruno).json()
    assert cerrada["diferencia"] == "0.00"
    assert notificaciones(sesion, "diferencia_caja") == []


def test_cerrar_caja_inexistente_404(cliente, h_duenia):
    assert cliente.post("/cajas/999/cerrar", json={"efectivo_contado": "0"}, headers=h_duenia).status_code == 404
