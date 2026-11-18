import { Badge } from "@mantine/core";
import type { EstadoVenta } from "../tipos";

const ESTADOS: Record<EstadoVenta, { texto: string; color: string }> = {
  valida: { texto: "Válida", color: "frasco" },
  observada: { texto: "Observada", color: "orange" },
  anulada: { texto: "Anulada", color: "red" },
};

export function EstadoVentaBadge({ estado }: { estado: EstadoVenta }) {
  const { texto, color } = ESTADOS[estado];
  return <Badge color={color}>{texto}</Badge>;
}
