// Sucursal en la que se está trabajando. El empleado tiene la suya fija;
// la dueña la elige en el encabezado y la elección queda guardada en el navegador.

import { createContext, useContext } from "react";
import type { Sucursal } from "../tipos";

export interface SucursalActiva {
  sucursales: Sucursal[];
  sucursalId: number | null; // null mientras cargan las sucursales
  sucursal: Sucursal | null;
  puedeElegir: boolean; // solo la dueña
  elegir: (id: number) => void;
  nombreDe: (id: number | null | undefined) => string;
  recargarSucursales: () => void; // después de renombrar una sucursal
}

export const SucursalActivaContext = createContext<SucursalActiva | null>(null);

export function useSucursalActiva(): SucursalActiva {
  const valor = useContext(SucursalActivaContext);
  if (valor === null) {
    throw new Error("useSucursalActiva se usa dentro de <SucursalActivaProvider>");
  }
  return valor;
}
