import { ActionIcon, Box, Grid, Select, Text } from "@mantine/core";
import { IconTrash } from "@tabler/icons-react";
import { EntradaCantidad } from "../../componentes/EntradaCantidad";
import { EntradaDinero } from "../../componentes/EntradaDinero";
import type { Producto } from "../../tipos";
import { desdeCentavos } from "../../utilidades/decimal";
import { formatearPrecio } from "../../utilidades/formato";

export interface Linea {
  clave: number; // identifica la línea en la lista aunque todavía no tenga producto
  productoId: number | null;
  cantidad: number | string;
  costo: number | string;
}

interface Props {
  linea: Linea;
  productos: Producto[];
  subtotalCentavos: number | null;
  puedeQuitar: boolean;
  alCambiar: (cambios: Partial<Linea>) => void;
  alQuitar: () => void;
}

// Un renglón de la compra: producto, cantidad, costo unitario y subtotal.
export function LineaCompra({ linea, productos, subtotalCentavos, puedeQuitar, alCambiar, alQuitar }: Props) {
  const producto = productos.find((p) => p.id === linea.productoId) ?? null;

  function elegirProducto(valor: string | null) {
    const elegido = productos.find((p) => p.id === Number(valor)) ?? null;
    // Se sugiere el último costo, que la dueña puede cambiar
    alCambiar({
      productoId: elegido?.id ?? null,
      costo: elegido?.costo_ultimo ? Number(elegido.costo_ultimo) : linea.costo,
    });
  }

  return (
    <Grid gap="xs" align="flex-end">
      <Grid.Col span={{ base: 12, sm: 5 }}>
        <Select
          label="Producto"
          placeholder="Buscá el producto"
          searchable
          data={productos.map((p) => ({ value: String(p.id), label: p.nombre }))}
          value={linea.productoId === null ? null : String(linea.productoId)}
          onChange={elegirProducto}
          nothingFoundMessage="No hay productos con ese nombre"
        />
      </Grid.Col>
      <Grid.Col span={{ base: 6, sm: 2 }}>
        <EntradaCantidad
          unidad={producto?.unidad ?? "kg"}
          label="Cantidad"
          value={linea.cantidad}
          onChange={(valor) => alCambiar({ cantidad: valor })}
          hideControls
        />
      </Grid.Col>
      <Grid.Col span={{ base: 6, sm: 2 }}>
        <EntradaDinero
          label={producto?.unidad === "unidad" ? "Costo c/u" : "Costo por kg"}
          value={linea.costo}
          onChange={(valor) => alCambiar({ costo: valor })}
        />
      </Grid.Col>
      <Grid.Col span={{ base: 10, sm: 2 }}>
        <Box ta={{ base: "left", sm: "right" }} pb={8}>
          <Text size="sm" c="var(--pl-tenue)" hiddenFrom="sm">
            Subtotal
          </Text>
          <Text fw={700} className="pl-numero">
            {subtotalCentavos === null ? "—" : formatearPrecio(desdeCentavos(subtotalCentavos))}
          </Text>
        </Box>
      </Grid.Col>
      <Grid.Col span={{ base: 2, sm: 1 }}>
        <ActionIcon color="red" mb={4} disabled={!puedeQuitar} onClick={alQuitar} aria-label="Quitar esta línea">
          <IconTrash size={18} />
        </ActionIcon>
      </Grid.Col>
    </Grid>
  );
}
