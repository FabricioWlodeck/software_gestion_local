import { Text } from "@mantine/core";
import { aMilesimas } from "../../utilidades/decimal";
import { formatearCantidad, formatearPrecio } from "../../utilidades/formato";
import type { ProductoEnVenta } from "./productoEnVenta";
import clases from "./venta.module.css";

interface Props {
  producto: ProductoEnVenta;
  resaltada: boolean;
  enTicket: string | null; // cantidad que ya está en el ticket
  alElegir: (producto: ProductoEnVenta) => void;
}

// Un producto como cartel de precio: nombre, precio por kg o por unidad y lo que queda en la sucursal.
export function TarjetaProducto({ producto, resaltada, enTicket, alElegir }: Props) {
  const sinStock = aMilesimas(producto.stock) <= 0;
  const porUnidad = producto.unidad === "kg" ? "/kg" : "c/u";

  let existencias = `Hay ${formatearCantidad(producto.stock, producto.unidad)}`;
  if (sinStock) existencias = "Sin stock";
  else if (enTicket) existencias = `En el ticket: ${formatearCantidad(enTicket, producto.unidad)}`;

  return (
    <button
      type="button"
      className={clases.tarjeta}
      data-resaltada={resaltada || undefined}
      data-en-ticket={enTicket ? true : undefined}
      disabled={sinStock}
      onClick={() => alElegir(producto)}
      aria-label={`${producto.nombre}, ${formatearPrecio(producto.precio)} ${porUnidad}. ${existencias}`}
    >
      <span className={clases.nombre}>{producto.nombre}</span>
      <span>
        <span className={clases.precio}>{formatearPrecio(producto.precio)}</span>
        <span className={clases.porUnidad}>{porUnidad}</span>
      </span>
      <Text component="span" className={clases.existencias} data-bajo={(producto.bajoMinimo && !enTicket) || undefined}>
        {existencias}
      </Text>
    </button>
  );
}
