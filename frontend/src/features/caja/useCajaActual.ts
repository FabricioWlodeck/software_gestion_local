import { api } from "../../api/cliente";
import { usePedido } from "../../hooks/usePedido";

// Caja abierta hoy en la sucursal (o null si está cerrada), con el resumen en vivo de sus ventas.
export function useCajaActual(sucursalId: number | null) {
  return usePedido(sucursalId === null ? null : `caja-${sucursalId}`, () => api.cajaActual(sucursalId ?? 0));
}
