"""
Dos cajas venden 1,5 kg de queso al mismo tiempo, y hay 2,1 kg.

Solo una de las dos ventas debería pasar. El script lo prueba dos veces:
  1. Sin bloqueo: las dos leen 2,1 kg, las dos aprueban y el stock termina mal.
  2. Con SELECT ... FOR UPDATE: la segunda caja espera a que la primera confirme,
     lee el stock actualizado y rechaza la venta.

Ejecutar desde la carpeta de la etapa, con la base ya creada y cargada:
    python demo_concurrencia.py
"""

import threading
import time
from decimal import Decimal

from sqlalchemy import select

from app.database import SesionLocal, engine
from app.models import Producto

QUESO = 1
STOCK_INICIAL = Decimal("2.100")
PEDIDO = Decimal("1.500")
inicio = 0.0


def registrar(caja: str, mensaje: str) -> None:
    print(f"  t={time.perf_counter() - inicio:4.1f} s  {caja}: {mensaje}")


def vender(caja: str, bloquear: bool, demora_inicial: float, resultados: list[str]) -> None:
    time.sleep(demora_inicial)
    with SesionLocal() as sesion:
        consulta = select(Producto).where(Producto.id == QUESO)
        if bloquear:
            consulta = consulta.with_for_update()
            registrar(caja, "pide el stock con FOR UPDATE...")
        producto = sesion.scalars(consulta).one()
        registrar(caja, f"lee stock = {producto.stock} kg")

        if producto.stock < PEDIDO:
            registrar(caja, "no alcanza: rechaza la venta")
            resultados.append("rechazada")
            return

        time.sleep(1.0)  # el tiempo que tarda la caja en terminar de cobrar
        producto.stock -= PEDIDO
        registrar(caja, f"vende {PEDIDO} kg y confirma (commit) con stock = {producto.stock} kg")
        sesion.commit()
        resultados.append("vendida")


def probar(bloquear: bool) -> None:
    global inicio
    with SesionLocal() as sesion:
        sesion.get(Producto, QUESO).stock = STOCK_INICIAL
        sesion.commit()

    titulo = "CON bloqueo (SELECT ... FOR UPDATE)" if bloquear else "SIN bloqueo"
    print(f"\n=== {titulo}: hay {STOCK_INICIAL} kg y cada caja pide {PEDIDO} kg ===")
    resultados: list[str] = []
    inicio = time.perf_counter()
    cajas = [
        threading.Thread(target=vender, args=("Caja 1", bloquear, 0.0, resultados)),
        threading.Thread(target=vender, args=("Caja 2", bloquear, 0.2, resultados)),
    ]
    for caja in cajas:
        caja.start()
    for caja in cajas:
        caja.join()

    with SesionLocal() as sesion:
        final = sesion.get(Producto, QUESO).stock
    vendidas = resultados.count("vendida")
    vendido = PEDIDO * vendidas
    if final == STOCK_INICIAL - vendido:
        estado = "correcto"
    else:
        estado = f"INCORRECTO: se vendieron {vendido} kg de {STOCK_INICIAL} kg y el stock no lo refleja"
    print(f"  Resultado: ventas aprobadas = {vendidas}, stock final = {final} kg ({estado})")


if __name__ == "__main__":
    engine.echo = False  # para que la salida muestre solo la línea de tiempo
    probar(bloquear=False)
    probar(bloquear=True)
