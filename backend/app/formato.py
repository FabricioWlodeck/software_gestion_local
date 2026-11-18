"""
Redondeos y formato de números en español (coma decimal y punto de miles).

Se usa en los mensajes de notificacion (que el bot envía tal cual por Telegram) y en los
textos de error. En el JSON los números viajan como texto con punto decimal, sin formato.
"""

from decimal import ROUND_HALF_UP, Decimal

CENTAVOS = Decimal("0.01")
GRAMOS = Decimal("0.001")  # la misma escala que las columnas DECIMAL(10, 3)
MENOS = "−"  # signo menos tipográfico, como en los ejemplos del contrato


def redondear_dinero(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def redondear_cantidad(valor: Decimal) -> Decimal:
    return valor.quantize(GRAMOS, rounding=ROUND_HALF_UP)


def _numero(valor: Decimal, decimales: int) -> str:
    """1234.5 con 2 decimales → «1.234,50» (sin signo)."""
    texto = f"{abs(valor):,.{decimales}f}"  # formato inglés: 1,234.50
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def formatear_dinero(valor: Decimal, con_signo: bool = False) -> str:
    """«$45.300,00»; con_signo agrega «+» o «−» delante (para diferencias de caja)."""
    signo = MENOS if valor < 0 else ("+" if con_signo and valor > 0 else "")
    return f"{signo}${_numero(valor, 2)}"


def formatear_cantidad(valor: Decimal, unidad: str, con_signo: bool = False) -> str:
    """«1,750 kg» o «2 u.»; con_signo agrega «+» o «−» delante."""
    signo = MENOS if valor < 0 else ("+" if con_signo and valor > 0 else "")
    if unidad == "unidad":
        return f"{signo}{_numero(valor, 0)} u."
    return f"{signo}{_numero(valor, 3)} kg"


def con_punto_final(texto: str) -> str:
    texto = texto.strip()
    return texto if texto.endswith((".", "!", "?", "…")) else f"{texto}."
