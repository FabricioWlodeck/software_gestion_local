from tests.conftest import CONTRASENA


def test_inicio_de_sesion_correcto(cliente):
    respuesta = cliente.post("/auth/token", data={"username": "bruno", "password": CONTRASENA})
    assert respuesta.status_code == 200
    token = respuesta.json()
    assert token["token_type"] == "bearer"

    yo = cliente.get("/auth/yo", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert yo.status_code == 200
    assert yo.json() == {
        "id": yo.json()["id"], "nombre_usuario": "bruno", "nombre": "Bruno", "rol": "empleado",
        "sucursal_id": yo.json()["sucursal_id"], "activo": True, "telegram_id": None,
    }


def test_contrasena_incorrecta_401(cliente):
    respuesta = cliente.post("/auth/token", data={"username": "bruno", "password": "otra-cosa"})
    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Usuario o contraseña incorrectos"}


def test_usuario_inactivo_no_puede_entrar(cliente, h_duenia, datos):
    desactivar = cliente.patch(f"/usuarios/{datos.bruno}", json={"activo": False}, headers=h_duenia)
    assert desactivar.status_code == 200
    assert desactivar.json()["activo"] is False

    respuesta = cliente.post("/auth/token", data={"username": "bruno", "password": CONTRASENA})
    assert respuesta.status_code == 401


def test_token_de_usuario_desactivado_deja_de_servir(cliente, h_duenia, h_bruno, datos):
    assert cliente.get("/auth/yo", headers=h_bruno).status_code == 200
    cliente.patch(f"/usuarios/{datos.bruno}", json={"activo": False}, headers=h_duenia)
    assert cliente.get("/auth/yo", headers=h_bruno).status_code == 401


def test_sin_token_401(cliente):
    respuesta = cliente.get("/productos")
    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Iniciá sesión para continuar"}


def test_token_invalido_401(cliente):
    respuesta = cliente.get("/productos", headers={"Authorization": "Bearer no-es-un-token"})
    assert respuesta.status_code == 401
