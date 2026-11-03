// Contexto de sesión: el usuario que inició sesión, disponible para cualquier componente
// sin tener que pasarlo por props a través de todos los niveles del árbol.

import { createContext, useContext } from "react";
import type { Usuario } from "../../tipos";

export interface Sesion {
  usuario: Usuario | null;
  verificando: boolean; // true mientras se comprueba un token guardado de una visita anterior
  iniciarSesion: (nombre: string, contrasena: string) => Promise<void>;
  cerrarSesion: () => void;
}

export const SesionContext = createContext<Sesion | null>(null);

// Gancho propio (custom hook): cualquier componente llama a useSesion() para leer la sesión.
export function useSesion(): Sesion {
  const sesion = useContext(SesionContext);
  if (sesion === null) {
    throw new Error("useSesion se usa dentro de <SesionProvider>");
  }
  return sesion;
}
