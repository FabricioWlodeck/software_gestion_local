import { Text, type TextProps } from "@mantine/core";
import type { Unidad } from "../tipos";
import { formatearCantidad, formatearCantidadConSigno } from "../utilidades/formato";

interface Props extends TextProps {
  valor: string;
  unidad: Unidad;
  conSigno?: boolean; // para movimientos de stock: "+2 u.", "−0,350 kg"
}

// Una cantidad con su unidad: "0,350 kg" o "2 u."
export function Cantidad({ valor, unidad, conSigno = false, ...props }: Props) {
  return (
    <Text component="span" inherit className="pl-numero" {...props}>
      {conSigno ? formatearCantidadConSigno(valor, unidad) : formatearCantidad(valor, unidad)}
    </Text>
  );
}
