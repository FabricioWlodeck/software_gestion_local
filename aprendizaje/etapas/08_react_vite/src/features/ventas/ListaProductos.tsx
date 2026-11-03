import type { Producto } from "../../tipos";
import { TarjetaProducto } from "./TarjetaProducto";

interface Props {
  productos: Producto[];
  onAgregar: (producto: Producto, cantidad: string) => void;
}

// Recibe la lista y dibuja una tarjeta por producto. No tiene estado propio.
export function ListaProductos({ productos, onAgregar }: Props) {
  return (
    <section className="lista-productos" aria-label="Productos">
      {productos.map((producto) => (
        // key le permite a React saber qué tarjeta es cuál entre un dibujo y el siguiente.
        <TarjetaProducto key={producto.id} producto={producto} onAgregar={onAgregar} />
      ))}
    </section>
  );
}
