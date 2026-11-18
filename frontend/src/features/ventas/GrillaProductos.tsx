import { Skeleton } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";
import { useEffect, useRef } from "react";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import type { ItemCarrito } from "../../tipos";
import type { ProductoEnVenta } from "./productoEnVenta";
import { TarjetaProducto } from "./TarjetaProducto";
import clases from "./venta.module.css";

interface Props {
  productos: ProductoEnVenta[];
  cargando: boolean;
  busqueda: string;
  resaltado: number;
  items: ItemCarrito[];
  alElegir: (producto: ProductoEnVenta) => void;
}

// Los productos que coinciden con la búsqueda. La tarjeta resaltada es la que agrega Enter.
export function GrillaProductos({ productos, cargando, busqueda, resaltado, items, alElegir }: Props) {
  const grilla = useRef<HTMLDivElement>(null);

  // Con las flechas, la tarjeta resaltada se mantiene a la vista
  useEffect(() => {
    const tarjeta = grilla.current?.children[resaltado];
    tarjeta?.scrollIntoView({ block: "nearest" });
  }, [resaltado]);

  if (cargando && productos.length === 0) {
    return (
      <div className={clases.grilla}>
        {Array.from({ length: 8 }, (_, indice) => (
          <Skeleton key={indice} h={108} radius={6} />
        ))}
      </div>
    );
  }

  if (productos.length === 0) {
    return (
      <PaginaVacia
        icono={<IconSearch size={28} />}
        titulo={busqueda ? `No hay productos que coincidan con «${busqueda}»` : "No hay productos activos"}
        descripcion={
          busqueda ? "Probá con otra palabra del nombre, sin tildes." : "La dueña puede cargarlos en Productos y precios."
        }
      />
    );
  }

  const cantidades = new Map(items.map((item) => [item.producto.id, item.cantidad]));

  return (
    <div className={clases.grilla} ref={grilla}>
      {productos.map((producto, indice) => (
        <TarjetaProducto
          key={producto.id}
          producto={producto}
          resaltada={busqueda !== "" && indice === resaltado}
          enTicket={cantidades.get(producto.id) ?? null}
          alElegir={alElegir}
        />
      ))}
    </div>
  );
}
