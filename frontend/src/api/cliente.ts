// Cliente de la API: el único archivo del frontend que sabe de URLs, headers y tokens.
// Las pantallas llaman a api.listarStock(1) sin saber cómo viaja la petición.

import type {
  Caja,
  CajaActual,
  CambiosProducto,
  CambiosProveedor,
  CambiosUsuario,
  Compra,
  CompraNueva,
  DatosProducto,
  DatosProveedor,
  EstadoVenta,
  FilaStock,
  Minimos,
  Movimiento,
  MovimientoNuevo,
  Producto,
  Proveedor,
  Resumen,
  Sucursal,
  TipoMovimiento,
  Token,
  Traspaso,
  TraspasoNuevo,
  Usuario,
  UsuarioNuevo,
  Venta,
  VentaDiaria,
  VentaNueva,
} from "../tipos";

const BASE = "/api"; // el proxy de Vite (y nginx en producción) lo reenvía al backend
const CLAVE_TOKEN = "punto-lacteo.token";

// Error con el código HTTP, para que cada pantalla decida qué mostrar.
// estado 0 = no hubo respuesta (servidor apagado o sin red).
export class ErrorApi extends Error {
  estado: number;

  constructor(estado: number, mensaje: string) {
    super(mensaje);
    this.estado = estado;
  }
}

const SIN_CONEXION = "No se pudo conectar con el servidor. Revisá que el sistema esté encendido y probá de nuevo.";

// Mensaje para mostrar de cualquier error (de la API o inesperado).
export function mensajeDe(error: unknown): string {
  if (error instanceof ErrorApi) {
    return error.message;
  }
  return SIN_CONEXION;
}

// ---------- Token en localStorage ----------

export function leerToken(): string | null {
  return localStorage.getItem(CLAVE_TOKEN);
}

function guardarToken(token: string): void {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function borrarToken(): void {
  localStorage.removeItem(CLAVE_TOKEN);
}

// Si el backend responde 401, la sesión ya no sirve (token vencido o usuario desactivado).
// La aplicación registra acá qué hacer en ese caso: volver a la pantalla de inicio de sesión.
let alPerderSesion: () => void = () => {};

export function cuandoSePierdaLaSesion(accion: () => void): void {
  alPerderSesion = accion;
}

// ---------- La función que hacen todas las peticiones ----------

async function pedir<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const headers = new Headers(opciones.headers);
  const token = leerToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, { ...opciones, headers });
  } catch {
    throw new ErrorApi(0, SIN_CONEXION); // fetch solo falla así cuando no hay respuesta
  }

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null);
    if (respuesta.status === 401 && token) {
      borrarToken();
      alPerderSesion();
    }
    throw new ErrorApi(respuesta.status, mensajeDeError(cuerpo, respuesta.status));
  }
  if (respuesta.status === 204) {
    return undefined as T;
  }
  return (await respuesta.json()) as T;
}

// FastAPI responde {"detail": "texto"} o, en los 422 de Pydantic, {"detail": [{msg, loc, ...}]}.
function mensajeDeError(cuerpo: unknown, estado: number): string {
  const detalle = (cuerpo as { detail?: unknown } | null)?.detail;
  if (typeof detalle === "string") {
    return detalle;
  }
  if (Array.isArray(detalle)) {
    return detalle.map((error: { msg?: string }) => error.msg ?? "Dato inválido").join(". ");
  }
  // Sin detail: el proxy (Vite o nginx) no llegó al backend
  if (estado >= 500) {
    return `${SIN_CONEXION} (error ${estado})`;
  }
  return `Error ${estado}`;
}

// Arma "?a=1&b=2" salteando los valores vacíos.
type ValorConsulta = string | number | boolean | null | undefined;

function consulta(parametros: Record<string, ValorConsulta>): string {
  const buscador = new URLSearchParams();
  for (const [clave, valor] of Object.entries(parametros)) {
    if (valor !== null && valor !== undefined && valor !== "") {
      buscador.set(clave, String(valor));
    }
  }
  const texto = buscador.toString();
  return texto ? `?${texto}` : "";
}

function enviar<T>(metodo: "POST" | "PATCH" | "PUT", ruta: string, cuerpo: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
}

// ---------- Filtros de los listados ----------

export interface FiltroFechas {
  desde?: string; // YYYY-MM-DD, inclusiva
  hasta?: string; // YYYY-MM-DD, inclusiva
}

export interface FiltroMovimientos extends FiltroFechas {
  sucursal_id: number;
  producto_id?: number | null;
  tipo?: TipoMovimiento | null;
  limite?: number;
}

export interface FiltroVentas extends FiltroFechas {
  sucursal_id: number;
  estado?: EstadoVenta | null;
  limite?: number;
}

export interface FiltroCajas extends FiltroFechas {
  sucursal_id?: number | null;
}

export interface FiltroCompras extends FiltroFechas {
  sucursal_id?: number | null;
  proveedor_id?: number | null;
}

export interface FiltroReporte {
  desde: string;
  hasta: string;
  sucursal_id?: number | null;
}

// ---------- Las operaciones de la API (una por ruta del contrato) ----------

export const api = {
  // Autenticación
  async iniciarSesion(usuario: string, contrasena: string): Promise<void> {
    // OAuth2 exige un formulario, no JSON. URLSearchParams lo arma.
    const formulario = new URLSearchParams({ username: usuario, password: contrasena });
    const token = await pedir<Token>("/auth/token", { method: "POST", body: formulario });
    guardarToken(token.access_token);
  },
  quienSoy: () => pedir<Usuario>("/auth/yo"),

  // Sucursales
  listarSucursales: () => pedir<Sucursal[]>("/sucursales"),
  renombrarSucursal: (id: number, nombre: string) => enviar<Sucursal>("PATCH", `/sucursales/${id}`, { nombre }),

  // Usuarios (dueña)
  listarUsuarios: () => pedir<Usuario[]>("/usuarios"),
  crearUsuario: (datos: UsuarioNuevo) => enviar<Usuario>("POST", "/usuarios", datos),
  editarUsuario: (id: number, cambios: CambiosUsuario) => enviar<Usuario>("PATCH", `/usuarios/${id}`, cambios),
  cambiarContrasena: (id: number, contrasena: string) =>
    enviar<void>("PUT", `/usuarios/${id}/contrasena`, { contrasena }),

  // Productos
  listarProductos: (opciones: { incluir_inactivos?: boolean; buscar?: string } = {}) =>
    pedir<Producto[]>(`/productos${consulta({ ...opciones })}`),
  crearProducto: (datos: DatosProducto) => enviar<Producto>("POST", "/productos", datos),
  editarProducto: (id: number, cambios: CambiosProducto) => enviar<Producto>("PATCH", `/productos/${id}`, cambios),
  guardarMinimos: (id: number, minimos: Minimos) => enviar<void>("PUT", `/productos/${id}/minimos`, minimos),

  // Stock
  listarStock: (sucursalId: number) => pedir<FilaStock[]>(`/stock${consulta({ sucursal_id: sucursalId })}`),
  listarMovimientos: (filtro: FiltroMovimientos) =>
    pedir<Movimiento[]>(`/stock/movimientos${consulta({ ...filtro })}`),
  registrarMovimiento: (datos: MovimientoNuevo) => enviar<Movimiento>("POST", "/stock/movimientos", datos),
  registrarTraspaso: (datos: TraspasoNuevo) => enviar<Traspaso>("POST", "/stock/traspasos", datos),

  // Caja
  cajaActual: (sucursalId: number) => pedir<CajaActual | null>(`/cajas/actual${consulta({ sucursal_id: sucursalId })}`),
  abrirCaja: (sucursalId: number, fondoInicial: string) =>
    enviar<Caja>("POST", "/cajas", { sucursal_id: sucursalId, fondo_inicial: fondoInicial }),
  cerrarCaja: (cajaId: number, efectivoContado: string, observacion: string | null) =>
    enviar<Caja>("POST", `/cajas/${cajaId}/cerrar`, { efectivo_contado: efectivoContado, observacion }),
  listarCajas: (filtro: FiltroCajas = {}) => pedir<Caja[]>(`/cajas${consulta({ ...filtro })}`),

  // Ventas
  registrarVenta: (datos: VentaNueva) => enviar<Venta>("POST", "/ventas", datos),
  listarVentas: (filtro: FiltroVentas) => pedir<Venta[]>(`/ventas${consulta({ ...filtro })}`),
  obtenerVenta: (id: number) => pedir<Venta>(`/ventas/${id}`),
  observarVenta: (id: number, motivo: string) => enviar<Venta>("POST", `/ventas/${id}/observar`, { motivo }),
  confirmarVenta: (id: number, motivo: string | null) =>
    enviar<Venta>("POST", `/ventas/${id}/confirmar`, { motivo }),
  anularVenta: (id: number, motivo: string) => enviar<Venta>("POST", `/ventas/${id}/anular`, { motivo }),

  // Proveedores (dueña)
  listarProveedores: (incluirInactivos = false) =>
    pedir<Proveedor[]>(`/proveedores${consulta({ incluir_inactivos: incluirInactivos })}`),
  crearProveedor: (datos: DatosProveedor) => enviar<Proveedor>("POST", "/proveedores", datos),
  editarProveedor: (id: number, cambios: CambiosProveedor) =>
    enviar<Proveedor>("PATCH", `/proveedores/${id}`, cambios),

  // Compras (dueña)
  listarCompras: (filtro: FiltroCompras = {}) => pedir<Compra[]>(`/compras${consulta({ ...filtro })}`),
  registrarCompra: (datos: CompraNueva) => enviar<Compra>("POST", "/compras", datos),

  // Reportes (dueña)
  resumen: (filtro: FiltroReporte) => pedir<Resumen>(`/reportes/resumen${consulta({ ...filtro })}`),
  ventasDiarias: (filtro: FiltroReporte) =>
    pedir<VentaDiaria[]>(`/reportes/ventas-diarias${consulta({ ...filtro })}`),
};
