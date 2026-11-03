// Cliente de la API: el único archivo del frontend que sabe de URLs, headers y tokens.
// Las pantallas llaman a api.listarProductos() sin saber cómo viaja la petición.

import type { Producto, Token, Usuario, Venta } from "../tipos";

const BASE = "/api"; // el proxy de Vite (y nginx en producción) lo reenvía al backend
const CLAVE_TOKEN = "punto-lacteo.token";

// Error con el código HTTP, para que cada pantalla decida qué mostrar.
export class ErrorApi extends Error {
  estado: number;

  constructor(estado: number, mensaje: string) {
    super(mensaje);
    this.estado = estado;
  }
}

// ---------- Token en localStorage (ver módulo 06, sección 2.6) ----------

export function leerToken(): string | null {
  return localStorage.getItem(CLAVE_TOKEN);
}

function guardarToken(token: string): void {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function borrarToken(): void {
  localStorage.removeItem(CLAVE_TOKEN);
}

// Si el backend responde 401, la sesión ya no sirve (token vencido o alterado).
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

  const respuesta = await fetch(`${BASE}${ruta}`, { ...opciones, headers });

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
  return `Error ${estado}`;
}

// ---------- Las operaciones de la API ----------

export const api = {
  async iniciarSesion(usuario: string, contrasena: string): Promise<void> {
    // OAuth2 exige un formulario, no JSON (módulo 06). URLSearchParams lo arma.
    const formulario = new URLSearchParams({ username: usuario, password: contrasena });
    const token = await pedir<Token>("/auth/token", { method: "POST", body: formulario });
    guardarToken(token.access_token);
  },

  quienSoy: () => pedir<Usuario>("/auth/yo"),

  listarProductos: () => pedir<Producto[]>("/productos"),

  listarVentas: () => pedir<Venta[]>("/ventas"),

  registrarVenta: (items: { producto_id: number; cantidad: string }[]) =>
    pedir<Venta>("/ventas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    }),
};
