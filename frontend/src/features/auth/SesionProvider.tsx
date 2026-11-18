import { useEffect, useState, type ReactNode } from "react";
import { api, borrarToken, cuandoSePierdaLaSesion, ErrorApi, leerToken } from "../../api/cliente";
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
    let cancelado = false;
    let espera: ReturnType<typeof setTimeout> | undefined;
    let intentos = 0;

    function verificar() {
      api
        .quienSoy()
        .then((yo) => {
          if (cancelado) return;
          setUsuario(yo);
          setVerificando(false);
        })
        .catch((problema: unknown) => {
          if (cancelado) return;
          // Sin respuesta o 5xx: el backend todavía está arrancando (nginx responde 502).
          // Se reintenta un rato y no se borra el token, para no cerrar la sesión por un reinicio.
          const sinBackend = problema instanceof ErrorApi && (problema.estado === 0 || problema.estado >= 500);
          if (sinBackend && intentos < 15) {
            intentos += 1;
            espera = setTimeout(verificar, 2000);
            return;
          }
          if (!sinBackend) {
            borrarToken(); // el token ya no sirve (401 o inválido)
          }
          setVerificando(false);
        });
    }

    verificar();
    return () => {
      cancelado = true;
      clearTimeout(espera);
    };
  }, []);

  async function iniciarSesion(nombre: string, contrasena: string) {
    await api.iniciarSesion(nombre, contrasena); // guarda el token o lanza ErrorApi
    setUsuario(await api.quienSoy());
  }

  function cerrarSesion() {
    borrarToken();
    setUsuario(null);
  }

  const esDuenia = usuario?.rol === "duenio";

  return (
    <SesionContext.Provider value={{ usuario, esDuenia, verificando, iniciarSesion, cerrarSesion }}>
      {children}
    </SesionContext.Provider>
  );
}
