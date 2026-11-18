// Producto tal como lo usa la pantalla de venta, armado a partir de GET /stock de la sucursal activa.

import type { FilaStock, ProductoVendible } from "../../tipos";

export interface ProductoEnVenta extends ProductoVendible {
  bajoMinimo: boolean;
}

export function desdeFilaStock(fila: FilaStock): ProductoEnVenta {
  return {
    id: fila.producto_id,
    nombre: fila.nombre,
    unidad: fila.unidad,
    precio: fila.precio,
    stock: fila.cantidad,
    bajoMinimo: fila.bajo_minimo,
  };
}

// Sin tildes ni mayúsculas, para que "lacteo" encuentre "Lácteo"
export function normalizar(texto: string): string {
  return texto.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
}

// Todas las palabras buscadas tienen que aparecer en el nombre, en cualquier orden.
export function coincide(producto: ProductoVendible, busqueda: string): boolean {
  const nombre = normalizar(producto.nombre);
  return normalizar(busqueda)
    .split(/\s+/)
    .filter(Boolean)
    .every((palabra) => nombre.includes(palabra));
}
