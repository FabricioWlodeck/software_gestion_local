import { useEffect, useState } from "react";
import { cargarProductosDePrueba } from "../../datos/productosDePrueba";
import type { ItemCarrito, Producto } from "../../tipos";
import { Carrito } from "./Carrito";
import { ListaProductos } from "./ListaProductos";
import "./ventas.css";

// Pantalla principal de la caja. Es la dueña del estado compartido: los productos y el carrito.
// Los hijos reciben datos por props y avisan cambios llamando a funciones (onAgregar, onQuitar).
export function PantallaVentas() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [carrito, setCarrito] = useState<ItemCarrito[]>([]);
  const [mensaje, setMensaje] = useState<string | null>(null);

  // Efecto: se ejecuta después del primer dibujo. Con [] como dependencias, una sola vez.
  useEffect(() => {
    cargarProductosDePrueba().then((lista) => {
      setProductos(lista);
      setCargando(false);
    });
  }, []);

  function agregar(producto: Producto, cantidad: string) {
    // Siempre se crea un arreglo nuevo: React detecta cambios comparando referencias, no contenidos.
    setCarrito((anterior) => [
      ...anterior.filter((item) => item.producto.id !== producto.id), // si ya estaba, se reemplaza
      { producto, cantidad },
    ]);
    setMensaje(null);
  }

  function quitar(productoId: number) {
    setCarrito((anterior) => anterior.filter((item) => item.producto.id !== productoId));
  }

  function cobrar() {
    // En el módulo 09, esto envía POST /ventas al backend.
    setMensaje(`Venta simulada con ${carrito.length} producto(s). En el módulo 09 se guarda de verdad.`);
    setCarrito([]);
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
      </div>
    </div>
  );
}
