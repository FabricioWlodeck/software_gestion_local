import { Alert, Button, Group, Text } from "@mantine/core";
import { IconPlugConnectedX } from "@tabler/icons-react";

interface Props {
  mensaje: string;
  alReintentar: () => void;
}

// Error al traer datos: dice qué pasó y ofrece reintentar.
export function ErrorCarga({ mensaje, alReintentar }: Props) {
  return (
    <Alert color="red" icon={<IconPlugConnectedX size={20} />} title="No se pudieron cargar los datos">
      <Group justify="space-between" gap="sm">
        <Text size="sm">{mensaje}</Text>
        <Button size="xs" variant="white" color="red" onClick={alReintentar}>
          Reintentar
        </Button>
      </Group>
    </Alert>
  );
}
