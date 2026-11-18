import { Text, type TextProps } from "@mantine/core";
import { formatearPrecio } from "../utilidades/formato";

interface Props extends TextProps {
  valor: string | number;
  cifra?: boolean; // true: letra condensada grande de los carteles de precios
}

// Un importe en pesos con números tabulares, listo para alinear en columnas.
export function Dinero({ valor, cifra = false, ...props }: Props) {
  return (
    <Text component="span" inherit className={cifra ? "pl-cifra" : "pl-numero"} {...props}>
      {formatearPrecio(valor)}
    </Text>
  );
}
