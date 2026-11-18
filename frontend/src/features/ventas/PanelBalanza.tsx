import { Box, Button, Group, Kbd, NumberInput, Text } from "@mantine/core";
import { IconCornerDownLeft } from "@tabler/icons-react";
import type { Ref } from "react";
import { desdeCentavos, subtotalEnCentavos, textoDecimal } from "../../utilidades/decimal";
import { formatearCantidad, formatearPrecio } from "../../utilidades/formato";
import type { ProductoEnVenta } from "./productoEnVenta";
import clases from "./venta.module.css";

// Pesos habituales del mostrador, en kg
const PESOS_RAPIDOS = [
  { texto: "100 g", valor: 0.1 },
  { texto: "¼ kg", valor: 0.25 },
  { texto: "½ kg", valor: 0.5 },
  { texto: "1 kg", valor: 1 },
];

interface Props {
  ref: Ref<HTMLInputElement>;
  producto: ProductoEnVenta | null;
  cantidad: string | number;
  enTicket: boolean;
  error: string | null;
  alCambiarCantidad: (valor: string | number) => void;
  alAgregar: () => void;
  alCancelar: () => void;
}

// Como la balanza: producto elegido, cantidad (peso o unidades) e importe antes de sumarlo al ticket.
export function PanelBalanza({ ref, producto, cantidad, enTicket, error, alCambiarCantidad, alAgregar, alCancelar }: Props) {
  if (producto === null) {
    return (
      <Box className={clases.balanza} data-vacia>
        <Text c="var(--pl-tenue)" visibleFrom="sm">
          Escribí parte del nombre y apretá <Kbd>Enter</Kbd> para elegir el producto, o tocá una tarjeta. Con{" "}
          <Kbd>↑</Kbd> <Kbd>↓</Kbd> cambiás de producto y con <Kbd>F9</Kbd> cobrás.
        </Text>
        <Text c="var(--pl-tenue)" hiddenFrom="sm">
          Buscá o tocá un producto para elegirlo.
        </Text>
      </Box>
    );
  }

  const esKg = producto.unidad === "kg";
  const cantidadTexto = textoDecimal(cantidad, esKg ? 3 : 0);
  const importe = cantidadTexto ? subtotalEnCentavos(producto.precio, cantidadTexto) : null;

  return (
    <Box className={clases.balanza}>
      <Group justify="space-between" align="flex-end" gap="md">
        <Box style={{ flex: "1 1 220px", minWidth: 0 }}>
          <Text fw={700} size="lg" lh={1.2}>
            {producto.nombre}
          </Text>
          <Text size="sm" c="var(--pl-tenue)">
            {formatearPrecio(producto.precio)} {esKg ? "el kg" : "la unidad"}. Hay{" "}
            {formatearCantidad(producto.stock, producto.unidad)}.
          </Text>
        </Box>

        <Box>
          <NumberInput
            ref={ref}
            label={esKg ? "Peso" : "Unidades"}
            w={160}
            size="lg"
            value={cantidad}
            onChange={alCambiarCantidad}
            decimalScale={esKg ? 3 : 0}
            allowDecimal={esKg}
            decimalSeparator=","
            allowNegative={false}
            step={esKg ? 0.05 : 1}
            min={0}
            hideControls
            inputMode={esKg ? "decimal" : "numeric"}
            rightSection={<Text c="var(--pl-tenue)">{esKg ? "kg" : "u."}</Text>}
            error={error}
            onKeyDown={(evento) => {
              if (evento.key === "Enter") {
                evento.preventDefault();
                alAgregar();
              } else if (evento.key === "Escape") {
                alCancelar();
              }
            }}
          />
        </Box>

        {esKg && (
          <Group gap={6} wrap="wrap">
            {PESOS_RAPIDOS.map((peso) => (
              <Button key={peso.texto} variant="default" size="sm" onClick={() => alCambiarCantidad(peso.valor)}>
                {peso.texto}
              </Button>
            ))}
          </Group>
        )}

        <Box ta="right" miw={130}>
          <Text size="sm" c="var(--pl-tenue)">
            Importe
          </Text>
          <Text className="pl-cifra" fz={28} lh={1.1}>
            {importe === null ? "—" : formatearPrecio(desdeCentavos(importe))}
          </Text>
        </Box>

        <Group gap="xs">
          <Button variant="subtle" color="gray" onClick={alCancelar}>
            Cancelar
          </Button>
          <Button size="lg" onClick={alAgregar} rightSection={<IconCornerDownLeft size={18} aria-hidden />}>
            {enTicket ? "Cambiar" : "Agregar"}
          </Button>
        </Group>
      </Group>
    </Box>
  );
}
