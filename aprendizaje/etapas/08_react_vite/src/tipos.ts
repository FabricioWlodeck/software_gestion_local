// Tipos compartidos por toda la aplicación.

// Espejo de ProductoOut del backend (etapa 06). Los Decimal llegan como texto.
export interface Producto {
  id: number;
  nombre: string;
  unidad: "kg" | "unidad";
  precio: string;
  stock: string;
}

// Una línea del carrito, antes de enviarla al backend.
export interface ItemCarrito {
  producto: Producto;
  cantidad: string; // tal como la escribió la cajera, con punto decimal
}
