import { MantineProvider } from "@mantine/core";
import { DatesProvider } from "@mantine/dates";
import { Notifications } from "@mantine/notifications";
import { lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { PantallaLogin } from "./features/auth/PantallaLogin";
import { RutaProtegida } from "./features/auth/RutaProtegida";
import { SesionProvider } from "./features/auth/SesionProvider";
import { PantallaStock } from "./features/stock/PantallaStock";
import { PantallaHistorialVentas } from "./features/ventas/PantallaHistorialVentas";
import { PantallaVenta } from "./features/ventas/PantallaVenta";
import { Marco } from "./layout/Marco";
import { tema } from "./tema";

// Las pantallas de la dueña se descargan recién cuando se abren: el empleado nunca las baja.
const PantallaCierres = lazy(() => import("./features/caja/PantallaCierres").then((m) => ({ default: m.PantallaCierres })));
const PantallaCompras = lazy(() => import("./features/compras/PantallaCompras").then((m) => ({ default: m.PantallaCompras })));
const PantallaEmpleados = lazy(() => import("./features/empleados/PantallaEmpleados").then((m) => ({ default: m.PantallaEmpleados })));
const PantallaProductos = lazy(() => import("./features/productos/PantallaProductos").then((m) => ({ default: m.PantallaProductos })));
const PantallaProveedores = lazy(() => import("./features/proveedores/PantallaProveedores").then((m) => ({ default: m.PantallaProveedores })));
const PantallaReportes = lazy(() => import("./features/reportes/PantallaReportes").then((m) => ({ default: m.PantallaReportes })));

// Componente raíz: tema, avisos, sesión y rutas.
export default function App() {
  return (
    <MantineProvider theme={tema} defaultColorScheme="light">
      <DatesProvider settings={{ locale: "es", firstDayOfWeek: 1 }}>
        <Notifications position="top-right" />
        <SesionProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<PantallaLogin />} />

              {/* Con sesión iniciada: cualquier rol */}
              <Route element={<RutaProtegida />}>
                <Route element={<Marco />}>
                  <Route index element={<PantallaVenta />} />
                  <Route path="ventas" element={<PantallaHistorialVentas />} />
                  <Route path="stock" element={<PantallaStock />} />

                  {/* Solo la dueña: al empleado lo devuelve a la venta */}
                  <Route element={<RutaProtegida soloDuenia />}>
                    <Route path="caja/cierres" element={<PantallaCierres />} />
                    <Route path="productos" element={<PantallaProductos />} />
                    <Route path="compras" element={<PantallaCompras />} />
                    <Route path="proveedores" element={<PantallaProveedores />} />
                    <Route path="empleados" element={<PantallaEmpleados />} />
                    <Route path="reportes" element={<PantallaReportes />} />
                  </Route>
                </Route>
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </SesionProvider>
      </DatesProvider>
    </MantineProvider>
  );
}
