import { NumberInput, Text, type NumberInputProps } from "@mantine/core";
import type { Unidad } from "../tipos";

interface Props extends NumberInputProps {
  unidad: Unidad;
}

// Campo de cantidad según la unidad: kg con 3 decimales (gramos) o unidades enteras.
// Para mandarlo a la API se pasa por textoDecimal(valor, unidad === "kg" ? 3 : 0).
export function EntradaCantidad({ unidad, ...props }: Props) {
  const esKg = unidad === "kg";
  return (
    <NumberInput
      decimalScale={esKg ? 3 : 0}
      allowDecimal={esKg}
      decimalSeparator=","
      thousandSeparator="."
      allowNegative={false}
      step={esKg ? 0.05 : 1}
      min={0}
      inputMode={esKg ? "decimal" : "numeric"}
      rightSection={<Text c="var(--pl-tenue)">{esKg ? "kg" : "u."}</Text>}
      {...props}
    />
  );
}
