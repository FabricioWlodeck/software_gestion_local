import { Divider, NavLink, Stack } from "@mantine/core";
import {
  IconBuildingWarehouse,
  IconCashRegister,
  IconChartBar,
  IconCheese,
  IconPackages,
  IconReceipt,
  IconScale,
  IconTruckDelivery,
  IconUsers,
} from "@tabler/icons-react";
import type { ComponentType } from "react";
import { NavLink as EnlaceRouter, useLocation } from "react-router";
import { useSesion } from "../features/auth/sesion";
import clases from "./Marco.module.css";

interface Enlace {
  ruta: string;
  texto: string;
  Icono: ComponentType<{ size?: number; stroke?: number }>;
}

const PARA_TODOS: Enlace[] = [
  { ruta: "/", texto: "Vender", Icono: IconScale },
  { ruta: "/ventas", texto: "Ventas", Icono: IconReceipt },
  { ruta: "/stock", texto: "Stock", Icono: IconPackages },
];

const SOLO_DUENIA: Enlace[] = [
  { ruta: "/reportes", texto: "Reportes", Icono: IconChartBar },
  { ruta: "/caja/cierres", texto: "Cierres de caja", Icono: IconCashRegister },
  { ruta: "/productos", texto: "Productos y precios", Icono: IconCheese },
  { ruta: "/compras", texto: "Compras", Icono: IconTruckDelivery },
  { ruta: "/proveedores", texto: "Proveedores", Icono: IconBuildingWarehouse },
  { ruta: "/empleados", texto: "Empleados", Icono: IconUsers },
];

// Menú lateral. El empleado nunca ve los enlaces de la dueña.
export function MenuNavegacion({ alNavegar }: { alNavegar: () => void }) {
  const { esDuenia } = useSesion();
  const { pathname } = useLocation();

  const dibujar = ({ ruta, texto, Icono }: Enlace) => (
    <NavLink
      key={ruta}
      component={EnlaceRouter}
      to={ruta}
      label={texto}
      leftSection={<Icono size={22} stroke={1.75} />}
      active={ruta === "/" ? pathname === "/" : pathname.startsWith(ruta)}
      className={clases.enlace}
      onClick={alNavegar}
    />
  );

  return (
    <Stack gap={2}>
      {PARA_TODOS.map(dibujar)}
      {esDuenia && (
        <>
          <Divider my="sm" />
          {SOLO_DUENIA.map(dibujar)}
        </>
      )}
    </Stack>
  );
}
