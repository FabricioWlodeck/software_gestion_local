from tests.ayudas import abrir_caja, vender


def test_reportes_cuentan_solo_las_ventas_validas(cliente, h_bruno, h_carla, h_duenia, datos):
    caja = abrir_caja(cliente, h_bruno, fondo="0")
    abrir_caja(cliente, h_carla, fondo="0")
    vender(cliente, h_bruno, [(datos.queso, "1")])                          # 12.500 efectivo, S1
    vender(cliente, h_bruno, [(datos.leche, "2")], medio="transferencia")   # 2.900 transferencia, S1
    vender(cliente, h_carla, [(datos.leche, "1")])                          # 1.450 efectivo, S2
    observada = vender(cliente, h_bruno, [(datos.queso, "1")])              # no cuenta
    anulada = vender(cliente, h_bruno, [(datos.leche, "3")])                # no cuenta
    cliente.post(f"/ventas/{observada['id']}/observar", json={"motivo": "revisar"}, headers=h_bruno)
    cliente.post(f"/ventas/{anulada['id']}/anular", json={"motivo": "error"}, headers=h_duenia)
    cliente.post("/stock/movimientos", json={"producto_id": datos.leche, "tipo": "merma", "cantidad": "1",
                                             "motivo": "vencido"}, headers=h_carla)
    cliente.post(f"/cajas/{caja['id']}/cerrar", json={"efectivo_contado": "24500"}, headers=h_bruno)  # esperado 25.000

    hoy = observada["fecha"][:10]
    resumen = cliente.get(f"/reportes/resumen?desde={hoy}&hasta={hoy}", headers=h_duenia)
    assert resumen.status_code == 200
    r = resumen.json()
    assert r["desde"] == hoy and r["hasta"] == hoy
    assert r["total"] == "16850.00"
    assert r["cantidad_ventas"] == 3
    assert r["por_medio"] == {"efectivo": "13950.00", "transferencia": "2900.00"}
    assert r["por_sucursal"] == [
        {"sucursal_id": datos.s1, "nombre": "Sucursal 1", "total": "15400.00", "cantidad_ventas": 2},
        {"sucursal_id": datos.s2, "nombre": "Sucursal 2", "total": "1450.00", "cantidad_ventas": 1},
    ]
    assert r["top_productos"][0] == {"producto_id": datos.queso, "nombre": "Queso cremoso", "unidad": "kg",
                                     "cantidad": "1.000", "total": "12500.00"}
    assert r["top_productos"][1]["cantidad"] == "3.000"  # leche: 2 + 1, sin la anulada
    assert r["ventas_observadas"] == 1
    assert r["ventas_anuladas"] == 1
    assert len(r["mermas_y_ajustes"]) == 1
    merma = r["mermas_y_ajustes"][0]
    assert merma["tipo"] == "merma" and merma["cantidad"] == "-1.000" and merma["usuario"] == "Carla"
    assert merma["producto"] == "Leche entera 1 L" and merma["motivo"] == "vencido"
    assert merma["unidad"] == "unidad"
    assert r["diferencias_caja"] == [{"caja_id": caja["id"], "sucursal_id": datos.s1,
                                      "cerrada_en": r["diferencias_caja"][0]["cerrada_en"], "diferencia": "-500.00"}]

    solo_s2 = cliente.get(f"/reportes/resumen?desde={hoy}&hasta={hoy}&sucursal_id={datos.s2}",
                          headers=h_duenia).json()
    assert solo_s2["total"] == "1450.00"
    assert [s["sucursal_id"] for s in solo_s2["por_sucursal"]] == [datos.s2]
    assert solo_s2["diferencias_caja"] == []

    diarias = cliente.get(f"/reportes/ventas-diarias?desde={hoy}&hasta={hoy}", headers=h_duenia).json()
    assert diarias == [
        {"fecha": hoy, "sucursal_id": datos.s1, "total": "15400.00", "cantidad": 2},
        {"fecha": hoy, "sucursal_id": datos.s2, "total": "1450.00", "cantidad": 1},
    ]

    vacio = cliente.get("/reportes/resumen?desde=2020-01-01&hasta=2020-01-31", headers=h_duenia).json()
    assert vacio["total"] == "0.00" and vacio["cantidad_ventas"] == 0 and vacio["top_productos"] == []
    assert cliente.get("/reportes/resumen?desde=2026-11-10&hasta=2026-11-01", headers=h_duenia).status_code == 422
    assert cliente.get("/reportes/resumen?desde=2026-11-10", headers=h_duenia).status_code == 422


def test_usuarios_crear_editar_y_reglas(cliente, h_duenia, datos):
    nuevo = cliente.post("/usuarios", json={"nombre_usuario": "dario", "nombre": "Darío", "contrasena": "123456",
                                            "rol": "empleado", "sucursal_id": datos.s2}, headers=h_duenia)
    assert nuevo.status_code == 201
    dario = nuevo.json()
    assert dario["rol"] == "empleado" and dario["sucursal_id"] == datos.s2 and dario["activo"] is True
    assert "password_hash" not in dario and "contrasena" not in dario

    assert cliente.post("/auth/token", data={"username": "dario", "password": "123456"}).status_code == 200

    repetido = {"nombre_usuario": "dario", "nombre": "Otro", "contrasena": "123456", "rol": "duenio"}
    assert cliente.post("/usuarios", json=repetido, headers=h_duenia).status_code == 409
    corta = {"nombre_usuario": "eva", "nombre": "Eva", "contrasena": "123", "rol": "duenio"}
    assert cliente.post("/usuarios", json=corta, headers=h_duenia).status_code == 422
    sin_sucursal = {"nombre_usuario": "eva", "nombre": "Eva", "contrasena": "123456", "rol": "empleado"}
    assert cliente.post("/usuarios", json=sin_sucursal, headers=h_duenia).status_code == 422

    editado = cliente.patch(f"/usuarios/{dario['id']}", json={"sucursal_id": datos.s1, "telegram_id": 123456789},
                            headers=h_duenia)
    assert editado.status_code == 200
    assert editado.json()["sucursal_id"] == datos.s1 and editado.json()["telegram_id"] == 123456789
    otro_con_mismo = cliente.patch(f"/usuarios/{datos.bruno}", json={"telegram_id": 123456789}, headers=h_duenia)
    assert otro_con_mismo.status_code == 409

    assert cliente.put(f"/usuarios/{dario['id']}/contrasena", json={"contrasena": "nueva123"},
                       headers=h_duenia).status_code == 204
    assert cliente.post("/auth/token", data={"username": "dario", "password": "nueva123"}).status_code == 200

    # La dueña no puede desactivarse a sí misma.
    propia = cliente.patch(f"/usuarios/{datos.duenia}", json={"activo": False}, headers=h_duenia)
    assert propia.status_code == 409
    assert len(cliente.get("/usuarios", headers=h_duenia).json()) == 4


def test_sucursales(cliente, h_bruno, h_duenia, datos):
    assert cliente.get("/sucursales", headers=h_bruno).json() == [
        {"id": datos.s1, "nombre": "Sucursal 1", "activa": True},
        {"id": datos.s2, "nombre": "Sucursal 2", "activa": True},
    ]
    renombrada = cliente.patch(f"/sucursales/{datos.s1}", json={"nombre": "Centro"}, headers=h_duenia)
    assert renombrada.json() == {"id": datos.s1, "nombre": "Centro", "activa": True}
    assert cliente.patch(f"/sucursales/{datos.s2}", json={"nombre": "Centro"}, headers=h_duenia).status_code == 409
