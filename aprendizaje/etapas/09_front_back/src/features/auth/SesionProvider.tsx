import { useEffect, useState, type ReactNode } from "react";
import { api, borrarToken, cuandoSePierdaLaSesion, leerToken } from "../../api/cliente";
import type { Usuario } from "../../tipos";
import { SesionContext } from "./sesion";

// Guarda quién inició sesión y se lo ofrece a todo lo que esté adentro (children).
export function SesionProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [verificando, setVerificando] = useState(leerToken() !== null);

  // Al abrir la página: si quedó un token de una visita anterior, se pregunta al backend de quién es.
  useEffect(() => {
    cuandoSePierdaLaSesion(() => setUsuario(null));
    if (leerToken() === null) {
      return;
    }
    api.quienSoy()
      .then(setUsuario)
      .catch(() => borrarToken())
      .finally(() => setVerificando(false));
  }, []);

  async function iniciarSesion(nombre: string, contrasena: string) {
    await api.iniciarSesion(nombre, contrasena); // guarda el token o lanza ErrorApi
    setUsuario(await api.quienSoy());
  }

  function cerrarSesion() {
    borrarToken();
    setUsuario(null);
  }

  return (
    <SesionContext.Provider value={{ usuario, verificando, iniciarSesion, cerrarSesion }}>
      {children}
    </SesionContext.Provider>
  );
}
