import { useEffect, useState } from "react";
import { api, ErrorApi } from "../../api/cliente";
import type { ItemCarrito, Producto } from "../../tipos";
import { formatearPrecio } from "../../utilidades/formato";
import { Carrito } from "./Carrito";
import { ListaProductos } from "./ListaProductos";
import "./ventas.css";

// Pantalla principal de la caja. Respecto de la etapa 08, cambian dos cosas:
// los productos vienen de GET /productos y "Cobrar" envía POST /ventas.
export function PantallaVentas() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [carrito, setCarrito] = useState<ItemCarrito[]>([]);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function cargarProductos() {
    api.listarProductos()
      .then(setProductos)
      .catch((problema: ErrorApi) => setError(problema.message))
      .finally(() => setCargando(false));
  }

  useEffect(cargarProductos, []);

  function agregar(producto: Producto, cantidad: string) {
    setCarrito((anterior) => [...anterior.filter((item) => item.producto.id !== producto.id), { producto, cantidad }]);
    setMensaje(null);
    setError(null);
  }

  function quitar(productoId: number) {
    setCarrito((anterior) => anterior.filter((item) => item.producto.id !== productoId));
  }

  async function cobrar() {
    setError(null);
    try {
      const items = carrito.map((item) => ({ producto_id: item.producto.id, cantidad: item.cantidad }));
      const venta = await api.registrarVenta(items);
      // El total que se informa es el del backend, calculado con Decimal: es el que vale.
      setMensaje(`Venta ${venta.id} registrada. Total: ${formatearPrecio(venta.total)}`);
      setCarrito([]);
      cargarProductos(); // el stock cambió: se vuelve a pedir la lista
    } catch (problema) {
      // 409 (sin stock) o 422 (cantidad inválida): el carrito queda como estaba para corregirlo.
      setError(problema instanceof ErrorApi ? problema.message : "No se pudo conectar con el servidor");
    }
  }

  return (
    <div className="pantalla-ventas">
      <div>
        <h2>Productos</h2>
        {cargando ? <p>Cargando productos…</p> : <ListaProductos productos={productos} onAgregar={agregar} />}
      </div>
      <div>
        <Carrito items={carrito} onQuitar={quitar} onCobrar={cobrar} />
        {mensaje && <p className="mensaje-ok">{mensaje}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}
