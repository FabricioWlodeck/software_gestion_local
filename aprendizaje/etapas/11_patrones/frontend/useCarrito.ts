// Hook personalizado: junta el estado del carrito y las acciones que lo cambian.
// La pantalla ya no sabe cómo se agrega o se quita un item; solo llama a estas funciones.
//
// Para usarlo en la etapa 08 o 09: copiar este archivo y carritoReducer.ts a src/features/ventas/
// y cambiar en los dos el import de "./tipos.ts" por "../../tipos" (ver ejercicio 4 del módulo 11).

import { useReducer } from "react";
import { carritoReducer } from "./carritoReducer.ts";
import type { ItemCarrito, Producto } from "./tipos.ts";

const CARRITO_VACIO: ItemCarrito[] = [];

export function useCarrito() {
  // useReducer guarda el estado y devuelve dispatch: llamarlo con una acción ejecuta el reducer
  // y vuelve a dibujar el componente con el estado nuevo.
  const [items, dispatch] = useReducer(carritoReducer, CARRITO_VACIO);

  return {
    items,
    agregar: (producto: Producto, cantidad: string) => dispatch({ tipo: "agregar", producto, cantidad }),
    quitar: (productoId: number) => dispatch({ tipo: "quitar", productoId }),
    vaciar: () => dispatch({ tipo: "vaciar" }),
  };
}
