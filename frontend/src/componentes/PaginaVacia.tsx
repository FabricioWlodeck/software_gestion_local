import { Stack, Text, ThemeIcon } from "@mantine/core";
import type { ReactNode } from "react";

interface Props {
  icono: ReactNode;
  titulo: string;
  descripcion?: ReactNode;
  accion?: ReactNode;
}

// Lo que se muestra cuando una lista no tiene nada: qué pasa y qué se puede hacer.
export function PaginaVacia({ icono, titulo, descripcion, accion }: Props) {
  return (
    <Stack align="center" gap="xs" py="xl" px="md" ta="center">
      <ThemeIcon variant="light" color="gray" size={56} radius="xl">
        {icono}
      </ThemeIcon>
      <Text fw={600} size="lg">
        {titulo}
      </Text>
      {descripcion && (
        <Text c="var(--pl-tenue)" maw={420}>
          {descripcion}
        </Text>
      )}
      {accion}
    </Stack>
  );
}
