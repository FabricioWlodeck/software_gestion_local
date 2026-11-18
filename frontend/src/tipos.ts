// Tipos compartidos: el contrato de la API (docs/contrato.md) visto desde el frontend.
// Los Decimal llegan como texto ("0.350", "7275.00") y las fechas en ISO sin zona.

export type Rol = "duenio" | "empleado";
export type Unidad = "kg" | "unidad";
export type ModoPrecio = "manual" | "margen";
export type MedioPago = "efectivo" | "transferencia";
export type EstadoVenta = "valida" | "observada" | "anulada";
export type EstadoCaja = "abierta" | "cerrada";
export type TipoMovimiento =
  | "compra"
  | "venta"
  | "merma"
  | "ajuste"
  | "traspaso_salida"
  | "traspaso_entrada"
  | "anulacion";

// ---------- Autenticación y usuarios ----------

export interface Token {
  access_token: string;
  token_type: "bearer";
}

export interface Usuario {
  id: number;
  nombre_usuario: string;
  nombre: string;
  rol: Rol;
  sucursal_id: number | null;
  activo: boolean;
  telegram_id: number | null;
}

export interface UsuarioNuevo {
  nombre_usuario: string;
  nombre: string;
  contrasena: string;
  rol: Rol;
  sucursal_id?: number | null;
}

export interface CambiosUsuario {
  nombre?: string;
  rol?: Rol;
  sucursal_id?: number | null;
  activo?: boolean;
  telegram_id?: number | null;
}

export interface Sucursal {
  id: number;
  nombre: string;
  activa: boolean;
}

// ---------- Productos y stock ----------

export interface StockDeProducto {
  sucursal_id: number;
  cantidad: string;
  minimo: string;
}

// El empleado recibe el mismo objeto sin modo_precio, margen ni costo_ultimo (regla 12).
export interface Producto {
  id: number;
  nombre: string;
  unidad: Unidad;
  precio: string;
  activo: boolean;
  modo_precio?: ModoPrecio;
  margen?: string | null;
  costo_ultimo?: string | null;
  stock: StockDeProducto[];
}

// Mínimos por sucursal: {"1": "2.000", "2": "1.000"}
export type Minimos = Record<string, string>;

export interface DatosProducto {
  nombre: string;
  unidad: Unidad;
  modo_precio: ModoPrecio;
  margen?: string | null;
  costo_ultimo?: string | null;
  precio?: string | null;
  minimos?: Minimos;
}

export type CambiosProducto = Partial<DatosProducto> & { activo?: boolean };

export interface FilaStock {
  producto_id: number;
  nombre: string;
  unidad: Unidad;
  precio: string;
  cantidad: string;
  minimo: string;
  bajo_minimo: boolean;
}

export interface Movimiento {
  id: number;
  fecha: string;
  producto_id: number;
  producto: string;
  unidad: Unidad;
  sucursal_id: number;
  tipo: TipoMovimiento;
  cantidad: string;
  saldo_resultante: string;
  usuario: string;
  motivo: string | null;
  venta_id: number | null;
  compra_id: number | null;
  traspaso_id: number | null;
}

export interface MovimientoNuevo {
  sucursal_id?: number;
  producto_id: number;
  tipo: "merma" | "ajuste";
  cantidad: string;
  motivo: string;
}

export interface TraspasoNuevo {
  producto_id: number;
  origen_id: number;
  destino_id: number;
  cantidad: string;
  motivo?: string | null;
}

export interface Traspaso {
  id: number;
  fecha: string;
  producto_id: number;
  producto: string;
  unidad: Unidad;
  origen_id: number;
  destino_id: number;
  cantidad: string;
  usuario: string;
  motivo: string | null;
}

// ---------- Caja ----------

export interface Caja {
  id: number;
  sucursal_id: number;
  estado: EstadoCaja;
  abierta_por: string;
  abierta_en: string;
  fondo_inicial: string;
  cerrada_por: string | null;
  cerrada_en: string | null;
  efectivo_esperado: string | null;
  efectivo_contado: string | null;
  diferencia: string | null;
  observacion: string | null;
}

// Caja abierta + resumen en vivo de sus ventas no anuladas
export interface CajaActual extends Caja {
  ventas_efectivo: string;
  ventas_transferencia: string;
  cantidad_ventas: number;
  efectivo_esperado_actual: string;
}

// ---------- Ventas ----------

export interface ItemVenta {
  producto_id: number;
  producto: string;
  unidad: Unidad;
  cantidad: string;
  precio_unitario: string;
  subtotal: string;
}

// observada_por y resuelta_por son nombres, como abierta_por en Caja.
export interface Venta {
  id: number;
  fecha: string;
  sucursal_id: number;
  caja_id: number;
  usuario_id: number;
  usuario: string;
  medio_pago: MedioPago;
  total: string;
  estado: EstadoVenta;
  motivo_observacion: string | null;
  observada_por: string | null;
  observada_en: string | null;
  motivo_resolucion: string | null;
  resuelta_por: string | null;
  resuelta_en: string | null;
  items: ItemVenta[];
}

export interface VentaNueva {
  sucursal_id?: number;
  medio_pago: MedioPago;
  items: { producto_id: number; cantidad: string }[];
}

// ---------- Proveedores y compras ----------

export interface Proveedor {
  id: number;
  nombre: string;
  telefono: string | null;
  email: string | null;
  notas: string | null;
  activo: boolean;
}

export interface DatosProveedor {
  nombre: string;
  telefono?: string | null;
  email?: string | null;
  notas?: string | null;
}

export type CambiosProveedor = Partial<DatosProveedor> & { activo?: boolean };

export interface ItemCompra {
  producto_id: number;
  producto: string;
  unidad: Unidad;
  cantidad: string;
  costo_unitario: string;
  subtotal: string;
}

export interface Compra {
  id: number;
  fecha: string;
  proveedor_id: number;
  proveedor: string;
  sucursal_id: number;
  usuario: string;
  comprobante: string | null;
  total: string;
  items: ItemCompra[];
}

export interface CompraNueva {
  proveedor_id: number;
  sucursal_id: number;
  comprobante?: string | null;
  items: { producto_id: number; cantidad: string; costo_unitario: string }[];
}

// ---------- Reportes ----------

export interface Resumen {
  desde: string;
  hasta: string;
  total: string;
  cantidad_ventas: number;
  por_medio: Record<MedioPago, string>;
  por_sucursal: { sucursal_id: number; nombre: string; total: string; cantidad_ventas: number }[];
  top_productos: { producto_id: number; nombre: string; unidad: Unidad; cantidad: string; total: string }[];
  ventas_observadas: number;
  ventas_anuladas: number;
  mermas_y_ajustes: {
    fecha: string;
    sucursal_id: number;
    producto: string;
    unidad: Unidad;
    tipo: "merma" | "ajuste";
    cantidad: string;
    usuario: string;
    motivo: string | null;
  }[];
  diferencias_caja: { caja_id: number; sucursal_id: number; cerrada_en: string; diferencia: string }[];
}

export interface VentaDiaria {
  fecha: string; // "2026-11-15"
  sucursal_id: number | null;
  total: string;
  cantidad: number;
}

// ---------- Estado de pantalla (no es parte del contrato) ----------

// Lo mínimo que el carrito necesita saber de un producto.
export interface ProductoVendible {
  id: number;
  nombre: string;
  unidad: Unidad;
  precio: string;
  stock: string; // existencias en la sucursal activa
}

// Una línea del carrito antes de enviarla al backend.
export interface ItemCarrito {
  producto: ProductoVendible;
  cantidad: string; // con punto decimal, como la espera el backend ("0.350")
}
