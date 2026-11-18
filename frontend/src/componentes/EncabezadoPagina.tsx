import { Box, Group, Text, Title } from "@mantine/core";
import type { ReactNode } from "react";

interface Props {
  titulo: string;
  detalle?: ReactNode; // una línea que dice de qué sucursal o período se trata
  acciones?: ReactNode;
}

// Título de cada pantalla con sus botones principales a la derecha.
export function EncabezadoPagina({ titulo, detalle, acciones }: Props) {
  return (
    <Group justify="space-between" align="flex-end" gap="sm" mb="md">
      <Box>
        <Title order={2}>{titulo}</Title>
        {detalle && <Text c="var(--pl-tenue)">{detalle}</Text>}
      </Box>
      {acciones && <Group gap="xs">{acciones}</Group>}
    </Group>
  );
}
