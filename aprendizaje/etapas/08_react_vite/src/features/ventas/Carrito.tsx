import type { ItemCarrito } from "../../tipos";
import { calcularSubtotal, formatearCantidad, formatearPrecio } from "../../utilidades/formato";

interface Props {
  items: ItemCarrito[];
  onQuitar: (productoId: number) => void;
  onCobrar: () => void;
}

// Muestra el carrito. No guarda nada: todo lo recibe por props.
export function Carrito({ items, onQuitar, onCobrar }: Props) {
  // Estado derivado: el total se calcula en cada dibujo a partir de los items, no se guarda aparte.
  const total = items.reduce((suma, item) => suma + calcularSubtotal(item.producto.precio, item.cantidad), 0);

  return (
    <aside className="carrito">
      <h2>Carrito</h2>
      {items.length === 0 ? (
        <p className="vacio">Todavía no hay productos.</p>
      ) : (
        <>
          <ul>
            {items.map((item) => (
              <li key={item.producto.id}>
                <span>{item.producto.nombre}</span>
                <span>{formatearCantidad(item.cantidad, item.producto.unidad)}</span>
                <span>{formatearPrecio(calcularSubtotal(item.producto.precio, item.cantidad))}</span>
                <button type="button" className="quitar" onClick={() => onQuitar(item.producto.id)} aria-label={`Quitar ${item.producto.nombre}`}>
                  ✕
                </button>
              </li>
            ))}
          </ul>
          <p className="total">
            Total: <strong>{formatearPrecio(total)}</strong>
          </p>
          <button type="button" className="cobrar" onClick={onCobrar}>
            Cobrar
          </button>
        </>
      )}
    </aside>
  );
}
