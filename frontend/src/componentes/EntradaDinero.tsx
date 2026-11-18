import { NumberInput, type NumberInputProps } from "@mantine/core";

// Campo para importes en pesos: "$ 10.000,50". El valor sale como number (o "" si está vacío);
// para mandarlo a la API se pasa por textoDecimal(valor, 2).
export function EntradaDinero(props: NumberInputProps) {
  return (
    <NumberInput
      prefix="$ "
      thousandSeparator="."
      decimalSeparator=","
      decimalScale={2}
      allowNegative={false}
      hideControls
      inputMode="decimal"
      {...props}
    />
  );
}
