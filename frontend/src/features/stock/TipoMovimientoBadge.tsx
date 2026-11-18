import { Badge } from "@mantine/core";
import type { TipoMovimiento } from "../../tipos";
import { TIPOS_MOVIMIENTO } from "./tiposMovimiento";

export function TipoMovimientoBadge({ tipo }: { tipo: TipoMovimiento }) {
  const { texto, color } = TIPOS_MOVIMIENTO[tipo] ?? { texto: tipo, color: "gray" };
  return <Badge color={color}>{texto}</Badge>;
}
