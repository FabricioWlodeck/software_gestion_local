import { Button, Group, Paper, Stack, Text, TextInput, Title } from "@mantine/core";
import { useState } from "react";
import { api } from "../../api/cliente";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import type { Sucursal } from "../../tipos";
import { avisarError, avisarExito } from "../../utilidades/avisos";

// Renombrar una sucursal (por ejemplo, de «Sucursal 1» a «Centro»).
function FilaSucursal({ sucursal, alGuardar }: { sucursal: Sucursal; alGuardar: () => void }) {
  const [nombre, setNombre] = useState(sucursal.nombre);
  const [enviando, setEnviando] = useState(false);
  const cambio = nombre.trim() !== "" && nombre.trim() !== sucursal.nombre;

  async function guardar() {
    setEnviando(true);
    try {
      const guardada = await api.renombrarSucursal(sucursal.id, nombre.trim());
      avisarExito("Sucursal renombrada", guardada.nombre);
      alGuardar();
    } catch (problema) {
      avisarError(problema, "No se pudo renombrar");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Group gap="xs" align="flex-end" wrap="nowrap">
      <TextInput
        aria-label={`Nombre de ${sucursal.nombre}`}
        size="sm"
        maxLength={60}
        value={nombre}
        onChange={(evento) => setNombre(evento.currentTarget.value)}
        style={{ flex: 1 }}
      />
      <Button size="sm" variant="default" disabled={!cambio} loading={enviando} onClick={guardar}>
        Guardar
      </Button>
    </Group>
  );
}

export function SeccionSucursales() {
  const { sucursales, recargarSucursales } = useSucursalActiva();
  return (
    <Paper withBorder radius="sm" p="md" maw={480}>
      <Stack gap="sm">
        <div>
          <Title order={4}>Sucursales</Title>
          <Text size="sm" c="var(--pl-tenue)">
            El nombre aparece en el encabezado, los tickets y los avisos de Telegram.
          </Text>
        </div>
        {sucursales.map((sucursal) => (
          <FilaSucursal key={`${sucursal.id}-${sucursal.nombre}`} sucursal={sucursal} alGuardar={recargarSucursales} />
        ))}
      </Stack>
    </Paper>
  );
}
