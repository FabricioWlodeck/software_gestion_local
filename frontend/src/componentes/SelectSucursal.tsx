import { Select, type SelectProps } from "@mantine/core";
import { useSucursalActiva } from "../hooks/sucursalActiva";

interface Props extends Omit<SelectProps, "data" | "value" | "onChange"> {
  valor: number | null;
  alCambiar: (id: number | null) => void;
  conTodas?: boolean; // agrega la opción "Todas las sucursales" (valor null)
  excluir?: number | null; // para el destino de un traspaso
}

// Select de sucursales para filtros y formularios.
export function SelectSucursal({ valor, alCambiar, conTodas = false, excluir, ...props }: Props) {
  const { sucursales } = useSucursalActiva();
  const opciones = sucursales
    .filter((sucursal) => sucursal.activa && sucursal.id !== excluir)
    .map((sucursal) => ({ value: String(sucursal.id), label: sucursal.nombre }));
  const datos = conTodas ? [{ value: "", label: "Todas las sucursales" }, ...opciones] : opciones;

  return (
    <Select
      data={datos}
      value={valor === null ? (conTodas ? "" : null) : String(valor)}
      onChange={(elegida) => alCambiar(elegida ? Number(elegida) : null)}
      {...props}
    />
  );
}
