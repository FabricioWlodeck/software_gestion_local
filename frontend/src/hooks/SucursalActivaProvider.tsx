import { useCallback, useState, type ReactNode } from "react";
import { api } from "../api/cliente";
import { useUsuario } from "../features/auth/sesion";
import { SucursalActivaContext } from "./sucursalActiva";
import { usePedido } from "./usePedido";

const CLAVE_SUCURSAL = "punto-lacteo.sucursal";

function leerGuardada(): number | null {
  try {
    const guardada = Number(localStorage.getItem(CLAVE_SUCURSAL));
    return Number.isInteger(guardada) && guardada > 0 ? guardada : null;
  } catch {
    return null;
  }
}

// Carga las sucursales y decide cuál está activa para todas las pantallas.
export function SucursalActivaProvider({ children }: { children: ReactNode }) {
  const usuario = useUsuario();
  const { datos, recargar: recargarSucursales } = usePedido("sucursales", api.listarSucursales);
  const sucursales = datos ?? [];
  const [elegida, setElegida] = useState<number | null>(leerGuardada);

  const puedeElegir = usuario.rol === "duenio";
  const activas = sucursales.filter((sucursal) => sucursal.activa);

  // Empleado: su sucursal. Dueña: la elegida si sigue existiendo; si no, la primera activa.
  let sucursalId: number | null;
  if (!puedeElegir) {
    sucursalId = usuario.sucursal_id;
  } else if (activas.some((sucursal) => sucursal.id === elegida)) {
    sucursalId = elegida;
  } else {
    sucursalId = activas[0]?.id ?? null;
  }

  const elegir = useCallback((id: number) => {
    setElegida(id);
    try {
      localStorage.setItem(CLAVE_SUCURSAL, String(id));
    } catch {
      // sin localStorage la elección dura hasta recargar la página
    }
  }, []);

  const nombreDe = (id: number | null | undefined) =>
    sucursales.find((sucursal) => sucursal.id === id)?.nombre ?? (id ? `Sucursal ${id}` : "—");

  const sucursal = sucursales.find((s) => s.id === sucursalId) ?? null;

  return (
    <SucursalActivaContext.Provider value={{ sucursales, sucursalId, sucursal, puedeElegir, elegir, nombreDe, recargarSucursales }}>
      {children}
    </SucursalActivaContext.Provider>
  );
}
