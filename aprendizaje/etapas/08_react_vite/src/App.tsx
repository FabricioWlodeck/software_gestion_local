import { PantallaVentas } from "./features/ventas/PantallaVentas";

// Componente raíz: arma el esqueleto de la página. En el módulo 09 decide si muestra
// el inicio de sesión o la caja, según haya un usuario identificado.
export default function App() {
  return (
    <>
      <header className="barra">
        <h1>Punto Lácteo</h1>
        <span>Caja · datos de prueba</span>
      </header>
      <main>
        <PantallaVentas />
      </main>
    </>
  );
}
