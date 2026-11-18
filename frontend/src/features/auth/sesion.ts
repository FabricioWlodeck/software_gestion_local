// Contexto de sesión: el usuario que inició sesión, disponible para cualquier componente
// sin tener que pasarlo por props a través de todos los niveles del árbol.

import { createContext, useContext } from "react";
import type { Usuario } from "../../tipos";

export interface Sesion {
  usuario: Usuario | null;
  esDuenia: boolean;
  verificando: boolean; // true mientras se comprueba un token guardado de una visita anterior
  iniciarSesion: (nombre: string, contrasena: string) => Promise<void>;
  cerrarSesion: () => void;
}

export const SesionContext = createContext<Sesion | null>(null);

// Hook propio: cualquier componente llama a useSesion() para leer la sesión.
export function useSesion(): Sesion {
  const sesion = useContext(SesionContext);
  if (sesion === null) {
    throw new Error("useSesion se usa dentro de <SesionProvider>");
  }
  return sesion;
}

// Para pantallas que solo se muestran con sesión iniciada (dentro de <RutaProtegida>).
export function useUsuario(): Usuario {
  const { usuario } = useSesion();
  if (usuario === null) {
    throw new Error("useUsuario se usa dentro de <RutaProtegida>");
  }
  return usuario;
}
