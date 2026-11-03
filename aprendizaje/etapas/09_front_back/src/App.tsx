import { PantallaLogin } from "./features/auth/PantallaLogin";
import { SesionProvider } from "./features/auth/SesionProvider";
import { useSesion } from "./features/auth/sesion";
import { PantallaVentas } from "./features/ventas/PantallaVentas";
import { ResumenVentas } from "./features/ventas/ResumenVentas";

// Componente raíz: ofrece la sesión a toda la aplicación.
export default function App() {
  return (
    <SesionProvider>
      <Contenido />
    </SesionProvider>
  );
}

// Decide qué mostrar según la sesión: verificando, inicio de sesión o la caja.
function Contenido() {
  const { usuario, verificando, cerrarSesion } = useSesion();

  return (
    <>
      <header className="barra">
        <h1>Punto Lácteo</h1>
        <span>Caja</span>
        {usuario && (
          <div className="usuario-actual">
            <span>
              {usuario.nombre} · {usuario.rol === "duenio" ? "dueño" : "empleado"}
            </span>
            <button type="button" onClick={cerrarSesion}>
              Cerrar sesión
            </button>
          </div>
        )}
      </header>
      <main>
        {verificando ? (
          <p>Verificando sesión…</p>
        ) : usuario === null ? (
          <PantallaLogin />
        ) : (
          <>
            <PantallaVentas />
            {/* Ocultar no es proteger: el backend responde 403 a un empleado igual (módulo 06). */}
            {usuario.rol === "duenio" && <ResumenVentas />}
          </>
        )}
      </main>
    </>
  );
}
