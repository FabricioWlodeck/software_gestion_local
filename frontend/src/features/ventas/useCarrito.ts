// Hook personalizado: junta el estado del carrito y las acciones que lo cambian.
// La pantalla no sabe cómo se agrega o se quita un item; solo llama a estas funciones.

import { useReducer } from "react";
import type { ItemCarrito, ProductoVendible } from "../../tipos";
import { subtotalEnCentavos } from "../../utilidades/decimal";
import { carritoReducer } from "./carritoReducer";

const CARRITO_VACIO: ItemCarrito[] = [];

export function useCarrito() {
  // useReducer guarda el estado y devuelve dispatch: llamarlo con una acción ejecuta el reducer
  // y vuelve a dibujar el componente con el estado nuevo.
  const [items, dispatch] = useReducer(carritoReducer, CARRITO_VACIO);

  // Total estimado en centavos; el que vale es el que devuelve el backend al cobrar.
  const totalCentavos = items.reduce(
    (total, item) => total + subtotalEnCentavos(item.producto.precio, item.cantidad),
    0,
  );

  return {
    items,
    totalCentavos,
    agregar: (producto: ProductoVendible, cantidad: string) => dispatch({ tipo: "agregar", producto, cantidad }),
    quitar: (productoId: number) => dispatch({ tipo: "quitar", productoId }),
    vaciar: () => dispatch({ tipo: "vaciar" }),
  };
}
