from decimal import Decimal

from tests.ayudas import abrir_caja, movimientos, notificaciones, stock_de, vender


def test_cruzar_el_minimo_avisa_una_sola_vez(cliente, h_bruno, sesion, datos):
    abrir_caja(cliente, h_bruno)
    vender(cliente, h_bruno, [(datos.queso, "2.000")])  # 5 → 3: sigue arriba del mínimo (2)
    assert notificaciones(sesion, "stock_bajo") == []

    vender(cliente, h_bruno, [(datos.queso, "1.250")])  # 3 → 1,750: cruza el mínimo
    avisos = notificaciones(sesion, "stock_bajo")
    assert len(avisos) == 1
    assert avisos[0].sucursal_id == datos.s1
    assert avisos[0].mensaje == "⚠️ Stock bajo en Sucursal 1: Queso cremoso quedó en 1,750 kg (mínimo 2,000 kg)."

    vender(cliente, h_bruno, [(datos.queso, "0.500")])  # ya estaba por debajo: no se repite
    assert len(notificaciones(sesion, "stock_bajo")) == 1


def test_cruzar_el_minimo_justo_en_el_limite(cliente, h_bruno, sesion, datos):
    abrir_caja(cliente, h_bruno)
    vender(cliente, h_bruno, [(datos.leche, "7")])  # 10 → 3: igual al mínimo, todavía no está por debajo
    assert notificaciones(sesion, "stock_bajo") == []
    vender(cliente, h_bruno, [(datos.leche, "1")])  # 3 → 2
    avisos = notificaciones(sesion, "stock_bajo")
    assert [a.mensaje for a in avisos] == [
        "⚠️ Stock bajo en Sucursal 1: Leche entera 1 L quedó en 2 u. (mínimo 3 u.)."
    ]


def test_merma_guarda_negativo_y_avisa(cliente, h_carla, sesion, datos):
    respuesta = cliente.post(
        "/stock/movimientos",
        json={"producto_id": datos.leche, "tipo": "merma", "cantidad": "2", "motivo": "vencido"},
        headers=h_carla,
    )
    assert respuesta.status_code == 201
    movimiento = respuesta.json()
    assert movimiento["tipo"] == "merma"
    assert movimiento["sucursal_id"] == datos.s2
    assert movimiento["cantidad"] == "-2.000"
    assert movimiento["saldo_resultante"] == "3.000"
    assert movimiento["usuario"] == "Carla"
    assert movimiento["motivo"] == "vencido"
    assert stock_de(sesion, datos.leche, datos.s2) == Decimal("3.000")
    avisos = notificaciones(sesion, "merma")
    assert [a.mensaje for a in avisos] == ["🗑️ Merma en Sucursal 2: Leche entera 1 L −2 u. (Carla): vencido."]


def test_merma_requiere_motivo(cliente, h_bruno, sesion, datos):
    for cuerpo in (
        {"producto_id": datos.queso, "tipo": "merma", "cantidad": "0.5"},
        {"producto_id": datos.queso, "tipo": "merma", "cantidad": "0.5", "motivo": ""},
        {"producto_id": datos.queso, "tipo": "merma", "cantidad": "0.5", "motivo": "   "},
    ):
        respuesta = cliente.post("/stock/movimientos", json=cuerpo, headers=h_bruno)
        assert respuesta.status_code == 422, cuerpo
    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("5.000")
    # La merma se informa positiva.
    negativa = {"producto_id": datos.queso, "tipo": "merma", "cantidad": "-0.5", "motivo": "x"}
    assert cliente.post("/stock/movimientos", json=negativa, headers=h_bruno).status_code == 422


def test_ajuste_con_signo_y_cruce_de_minimo(cliente, h_bruno, sesion, datos):
    positivo = cliente.post(
        "/stock/movimientos",
        json={"producto_id": datos.queso, "tipo": "ajuste", "cantidad": "0.500", "motivo": "conteo"},
        headers=h_bruno,
    )
    assert positivo.status_code == 201
    assert positivo.json()["cantidad"] == "0.500"
    negativo = cliente.post(
        "/stock/movimientos",
        json={"producto_id": datos.queso, "tipo": "ajuste", "cantidad": "-4", "motivo": "conteo de cierre"},
        headers=h_bruno,
    )
    assert negativo.status_code == 201
    assert negativo.json()["saldo_resultante"] == "1.500"
    assert [a.mensaje for a in notificaciones(sesion, "ajuste")] == [
        "🔧 Ajuste en Sucursal 1: Queso cremoso +0,500 kg (Bruno): conteo.",
        "🔧 Ajuste en Sucursal 1: Queso cremoso −4,000 kg (Bruno): conteo de cierre.",
    ]
    assert len(notificaciones(sesion, "stock_bajo")) == 1  # 5,5 → 1,5 cruza el mínimo de 2
    # No puede dejar el stock negativo ni ser cero.
    excesivo = {"producto_id": datos.queso, "tipo": "ajuste", "cantidad": "-2", "motivo": "x"}
    assert cliente.post("/stock/movimientos", json=excesivo, headers=h_bruno).status_code == 409
    cero = {"producto_id": datos.queso, "tipo": "ajuste", "cantidad": "0", "motivo": "x"}
    assert cliente.post("/stock/movimientos", json=cero, headers=h_bruno).status_code == 422


def test_traspaso_crea_el_par_de_movimientos(cliente, h_duenia, sesion, datos):
    respuesta = cliente.post(
        "/stock/traspasos",
        json={"producto_id": datos.queso, "origen_id": datos.s1, "destino_id": datos.s2, "cantidad": "3.500",
              "motivo": "reposición"},
        headers=h_duenia,
    )
    assert respuesta.status_code == 201
    traspaso = respuesta.json()
    assert traspaso["cantidad"] == "3.500"
    assert traspaso["origen_id"] == datos.s1 and traspaso["destino_id"] == datos.s2
    assert stock_de(sesion, datos.queso, datos.s1) == Decimal("1.500")
    assert stock_de(sesion, datos.queso, datos.s2) == Decimal("6.500")

    par = movimientos(sesion, traspaso_id=traspaso["id"])
    assert sorted((m.tipo, m.sucursal_id, m.cantidad, m.saldo_resultante) for m in par) == [
        ("traspaso_entrada", datos.s2, Decimal("3.500"), Decimal("6.500")),
        ("traspaso_salida", datos.s1, Decimal("-3.500"), Decimal("1.500")),
    ]
    # Regla 2 en el origen: 5 → 1,5 cruza el mínimo de 2.
    assert [a.sucursal_id for a in notificaciones(sesion, "stock_bajo")] == [datos.s1]


def test_traspaso_validaciones(cliente, h_duenia, datos):
    misma = {"producto_id": datos.queso, "origen_id": datos.s1, "destino_id": datos.s1, "cantidad": "1"}
    assert cliente.post("/stock/traspasos", json=misma, headers=h_duenia).status_code == 422
    mucho = {"producto_id": datos.queso, "origen_id": datos.s2, "destino_id": datos.s1, "cantidad": "3.001"}
    assert cliente.post("/stock/traspasos", json=mucho, headers=h_duenia).status_code == 409
    fraccion = {"producto_id": datos.leche, "origen_id": datos.s1, "destino_id": datos.s2, "cantidad": "0.5"}
    assert cliente.post("/stock/traspasos", json=fraccion, headers=h_duenia).status_code == 422


def test_listar_stock_de_la_sucursal(cliente, h_bruno, h_duenia, datos):
    cliente.post(
        "/stock/movimientos",
        json={"producto_id": datos.queso, "tipo": "merma", "cantidad": "3.5", "motivo": "hongos"},
        headers=h_bruno,
    )
    stock = {fila["nombre"]: fila for fila in cliente.get("/stock", headers=h_bruno).json()}
    assert stock["Queso cremoso"] == {
        "producto_id": datos.queso, "nombre": "Queso cremoso", "unidad": "kg", "precio": "12500.00",
        "cantidad": "1.500", "minimo": "2.000", "bajo_minimo": True,
    }
    assert stock["Leche entera 1 L"]["bajo_minimo"] is False
    # Los productos inactivos no aparecen.
    cliente.patch(f"/productos/{datos.leche}", json={"activo": False}, headers=h_duenia)
    assert [f["nombre"] for f in cliente.get("/stock", headers=h_bruno).json()] == ["Queso cremoso"]
