// Funciones de formato. No son componentes: son TypeScript común, reutilizable en cualquier pantalla.

import dayjs from "dayjs";
import "dayjs/locale/es";
import type { Unidad } from "../tipos";

dayjs.locale("es");

const moneda = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });
const kilos = new Intl.NumberFormat("es-AR", { minimumFractionDigits: 3, maximumFractionDigits: 3 });
const enteros = new Intl.NumberFormat("es-AR", { maximumFractionDigits: 0 });
const porcentaje = new Intl.NumberFormat("es-AR", { maximumFractionDigits: 2 });

// "7275.00" → "$ 7.275,00"
export function formatearPrecio(valor: string | number): string {
  return moneda.format(Number(valor));
}

// "0.350" kg → "0,350 kg" · "2.000" unidad → "2 u."
export function formatearCantidad(cantidad: string | number, unidad: Unidad): string {
  const numero = Number(cantidad);
  return unidad === "kg" ? `${kilos.format(numero)} kg` : `${enteros.format(numero)} u.`;
}

// Igual que formatearCantidad pero con signo explícito (movimientos de stock): "+2 u.", "−0,350 kg"
export function formatearCantidadConSigno(cantidad: string, unidad: Unidad): string {
  const numero = Number(cantidad);
  const signo = numero > 0 ? "+" : numero < 0 ? "−" : "";
  return `${signo}${formatearCantidad(Math.abs(numero), unidad)}`;
}

export function formatearPorcentaje(valor: string | number): string {
  return `${porcentaje.format(Number(valor))} %`;
}

// "2026-11-15T10:32:00" → "15/11/2026 10:32"
export function formatearFechaHora(iso: string | null): string {
  return iso ? dayjs(iso).format("DD/MM/YYYY HH:mm") : "—";
}

// "2026-11-15T10:32:00" → "10:32"
export function formatearHora(iso: string): string {
  return dayjs(iso).format("HH:mm");
}

// "2026-11-15" → "15/11/2026"
export function formatearFecha(iso: string): string {
  return dayjs(iso).format("DD/MM/YYYY");
}

// Fecha de hoy en el formato que espera la API (YYYY-MM-DD)
export function hoyIso(): string {
  return dayjs().format("YYYY-MM-DD");
}

export function aIso(fecha: Date | string): string {
  return dayjs(fecha).format("YYYY-MM-DD");
}
