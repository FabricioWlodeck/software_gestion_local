"""
Errores de las reglas del negocio. Cada clase trae su código HTTP y main.py los traduce a
{"detail": "mensaje"}. Los services no conocen HTTP: solo lanzan estos errores.
"""


class ErrorDeNegocio(Exception):
    codigo = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class CredencialesInvalidas(ErrorDeNegocio):
    codigo = 401

    def __init__(self, mensaje: str = "Usuario o contraseña incorrectos"):
        # El mismo mensaje si falla el usuario o la contraseña: no se revela cuál de los dos.
        super().__init__(mensaje)


class SinPermiso(ErrorDeNegocio):
    codigo = 403

    def __init__(self, mensaje: str = "No tenés permiso para esta acción"):
        super().__init__(mensaje)


class OtraSucursal(SinPermiso):
    def __init__(self):
        super().__init__("No tenés permiso para operar en otra sucursal")


class NoEncontrado(ErrorDeNegocio):
    codigo = 404

    def __init__(self, que: str, identificador: int | str):
        super().__init__(f"No existe {que} {identificador}")


class Conflicto(ErrorDeNegocio):
    """Regla del negocio que impide la operación: sin stock, caja cerrada, nombre repetido…"""

    codigo = 409


class DatosInvalidos(ErrorDeNegocio):
    codigo = 422


class SucursalRequerida(DatosInvalidos):
    def __init__(self):
        super().__init__("Indicá la sucursal (sucursal_id)")


class CantidadNoEntera(DatosInvalidos):
    def __init__(self, nombre: str):
        super().__init__(f"{nombre} se vende por unidad: la cantidad tiene que ser entera")
