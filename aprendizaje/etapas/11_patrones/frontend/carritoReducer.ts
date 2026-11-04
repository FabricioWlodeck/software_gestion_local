// Lógica del carrito como reducer: una función pura que recibe el estado actual y una acción,
// y devuelve el estado nuevo. No usa React, así que se puede probar con Node solo.
//
// Todas las formas de cambiar el carrito quedan en un solo lugar. Cuando se agreguen
// descuentos o medios de pago, se suma un caso acá y la pantalla no cambia.

import type { ItemCarrito, Producto } from "./tipos.ts";

// Cada acción es un objeto con un "tipo". TypeScript obliga a pasar los datos que pide cada tipo.
export type AccionCarrito =
  | { tipo: "agregar"; producto: Producto; cantidad: string }
  | { tipo: "quitar"; productoId: number }
  | { tipo: "vaciar" };

export function carritoReducer(items: ItemCarrito[], accion: AccionCarrito): ItemCarrito[] {
  switch (accion.tipo) {
    case "agregar":
      // Si el producto ya estaba, se reemplaza su cantidad (igual que en la etapa 08).
      return [
        ...items.filter((item) => item.producto.id !== accion.producto.id),
        { producto: accion.producto, cantidad: accion.cantidad },
      ];
    case "quitar":
      return items.filter((item) => item.producto.id !== accion.productoId);
    case "vaciar":
      return [];
  }
}
