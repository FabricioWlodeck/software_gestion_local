// Tipos compartidos: el contrato de la API de la etapa 06, visto desde el frontend.
// Cada interfaz es espejo de un schema de Pydantic. Los Decimal y las fechas llegan como texto.

export interface Producto {
  id: number;
  nombre: string;
  unidad: "kg" | "unidad";
  precio: string;
  stock: string;
}

export interface ItemVenta {
  producto_id: number;
  nombre: string;
  cantidad: string;
  precio_unitario: string;
  subtotal: string;
}

export interface Venta {
  id: number;
  fecha: string;
  usuario_id: number;
  items: ItemVenta[];
  total: string;
}

export interface Usuario {
  id: number;
  nombre: string;
  rol: "duenio" | "empleado";
}

export interface Token {
  access_token: string;
  token_type: "bearer";
}

// Una línea del carrito, antes de enviarla al backend. No es parte del contrato: es estado de la pantalla.
export interface ItemCarrito {
  producto: Producto;
  cantidad: string;
}
