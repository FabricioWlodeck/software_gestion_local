"""Tipos reutilizables para validar la entrada. Los Decimal viajan en el JSON como texto."""

from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field, StringConstraints

from app.formato import redondear_cantidad, redondear_dinero


def _vacio_a_none(valor: object) -> object:
    """Recorta los espacios y convierte el texto vacío en None (los formularios mandan "")."""
    if isinstance(valor, str):
        valor = valor.strip()
        return valor or None
    return valor


def texto(maximo: int, minimo: int = 1):
    """Texto obligatorio, sin espacios sobrantes."""
    return Annotated[str, StringConstraints(strip_whitespace=True, min_length=minimo, max_length=maximo)]


def texto_opcional(maximo: int):
    """Texto opcional: "" y "   " se guardan como NULL."""
    return Annotated[Annotated[str, StringConstraints(max_length=maximo)] | None, BeforeValidator(_vacio_a_none)]


Motivo = texto(200)
MotivoOpcional = texto_opcional(200)

# Dinero DECIMAL(12,2) y cantidades DECIMAL(10,3), como las columnas. AfterValidator lleva el
# valor a la escala de la columna ("40" → 40.00), así la respuesta muestra lo mismo que la base.
_A_CENTAVOS = AfterValidator(redondear_dinero)
_A_GRAMOS = AfterValidator(redondear_cantidad)
Dinero = Annotated[Decimal, Field(max_digits=12, decimal_places=2), _A_CENTAVOS]
DineroNoNegativo = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2), _A_CENTAVOS]
DineroPositivo = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2), _A_CENTAVOS]
Cantidad = Annotated[Decimal, Field(max_digits=10, decimal_places=3), _A_GRAMOS]
CantidadPositiva = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=3), _A_GRAMOS]
CantidadNoNegativa = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=3), _A_GRAMOS]
Porcentaje = Annotated[Decimal, Field(ge=0, max_digits=6, decimal_places=2), _A_CENTAVOS]

# {"<sucursal_id>": "2.000"}: las claves del JSON son texto y Pydantic las convierte a int.
Minimos = dict[int, CantidadNoNegativa]
