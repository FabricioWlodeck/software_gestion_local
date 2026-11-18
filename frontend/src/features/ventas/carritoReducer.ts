// Lógica del carrito como reducer: una función pura que recibe el estado actual y una acción,
// y devuelve el estado nuevo. No usa React, así que se puede probar con Node solo.
// (El archivo no se llama carrito.ts para no chocar en Windows con Carrito.tsx.)

import type { ItemCarrito, ProductoVendible } from "../../tipos";

// Cada acción es un objeto con un "tipo". TypeScript obliga a pasar los datos que pide cada tipo.
export type AccionCarrito =
  | { tipo: "agregar"; producto: ProductoVendible; cantidad: string }
  | { tipo: "quitar"; productoId: number }
  | { tipo: "vaciar" };

export function carritoReducer(items: ItemCarrito[], accion: AccionCarrito): ItemCarrito[] {
  switch (accion.tipo) {
    case "agregar": {
      // Si el producto ya estaba, se reemplaza su cantidad en el mismo lugar del ticket.
      const nuevo = { producto: accion.producto, cantidad: accion.cantidad };
      const yaEstaba = items.some((item) => item.producto.id === accion.producto.id);
      return yaEstaba
        ? items.map((item) => (item.producto.id === accion.producto.id ? nuevo : item))
        : [...items, nuevo];
    }
    case "quitar":
      return items.filter((item) => item.producto.id !== accion.productoId);
    case "vaciar":
      return [];
  }
}
