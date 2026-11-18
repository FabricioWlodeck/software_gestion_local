import { ActionIcon, Text } from "@mantine/core";
import { IconX } from "@tabler/icons-react";
import type { ItemCarrito } from "../../tipos";
import { desdeCentavos, subtotalEnCentavos } from "../../utilidades/decimal";
import { formatearCantidad, formatearPrecio } from "../../utilidades/formato";
import clases from "./venta.module.css";

interface Props {
  item: ItemCarrito;
  alEditar: (item: ItemCarrito) => void;
  alQuitar: (productoId: number) => void;
}

// Un renglón del ticket: producto, cantidad × precio y subtotal estimado.
export function LineaTicket({ item, alEditar, alQuitar }: Props) {
  const { producto, cantidad } = item;
  const subtotal = desdeCentavos(subtotalEnCentavos(producto.precio, cantidad));

  return (
    <div className={clases.linea}>
      <button
        type="button"
        className={clases.lineaNombre}
        onClick={() => alEditar(item)}
        title="Cambiar la cantidad"
      >
        <Text component="span" className={clases.lineaTitulo} display="block" truncate>
          {producto.nombre}
        </Text>
        <Text component="span" size="sm" c="var(--pl-tenue)" className="pl-numero">
          {formatearCantidad(cantidad, producto.unidad)} × {formatearPrecio(producto.precio)}
        </Text>
      </button>
      <Text fw={700} className="pl-numero">
        {formatearPrecio(subtotal)}
      </Text>
      <ActionIcon color="gray" aria-label={`Quitar ${producto.nombre} del ticket`} onClick={() => alQuitar(producto.id)}>
        <IconX size={18} />
      </ActionIcon>
    </div>
  );
}
