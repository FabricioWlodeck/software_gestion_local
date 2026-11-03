import { useState } from "react";
import type { Producto } from "../../tipos";
import { formatearPrecio } from "../../utilidades/formato";

interface Props {
  producto: Producto;
  onAgregar: (producto: Producto, cantidad: string) => void;
}

// Un producto con su campo de cantidad. Lo que se está escribiendo es estado local:
// solo le importa a esta tarjeta, así que vive acá y no en la pantalla.
export function TarjetaProducto({ producto, onAgregar }: Props) {
  const [cantidad, setCantidad] = useState(producto.unidad === "kg" ? "0.250" : "1");
  const [error, setError] = useState<string | null>(null);
  const sinStock = Number(producto.stock) === 0;

  function agregar() {
    const numero = Number(cantidad);
    if (!(numero > 0)) {
      setError("Ingresá una cantidad mayor que cero");
      return;
    }
    if (producto.unidad === "unidad" && !Number.isInteger(numero)) {
      setError("Este producto se vende por unidad");
      return;
    }
    setError(null);
    onAgregar(producto, cantidad); // avisa al componente padre; la tarjeta no conoce el carrito
  }

  return (
    <article className="tarjeta-producto">
      <h3>{producto.nombre}</h3>
      <p className="precio">
        {formatearPrecio(producto.precio)} {producto.unidad === "kg" ? "por kg" : "c/u"}
      </p>
      <p className="stock">
        Stock: {Number(producto.stock).toLocaleString("es-AR")} {producto.unidad === "kg" ? "kg" : "u."}
      </p>
      <div className="fila">
        <input
          type="number"
          min="0"
          step={producto.unidad === "kg" ? "0.001" : "1"}
          value={cantidad}
          onChange={(evento) => setCantidad(evento.target.value)}
          disabled={sinStock}
          aria-label={`Cantidad de ${producto.nombre}`}
        />
        <button type="button" onClick={agregar} disabled={sinStock}>
          {sinStock ? "Sin stock" : "Agregar"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </article>
  );
}
