import { Group, Select, Text } from "@mantine/core";
import { IconMapPin } from "@tabler/icons-react";
import { useSucursalActiva } from "../hooks/sucursalActiva";

// Sucursal activa en el encabezado: la dueña la cambia; el empleado ve la suya, fija.
export function SelectorSucursal() {
  const { sucursales, sucursalId, sucursal, puedeElegir, elegir } = useSucursalActiva();

  if (!puedeElegir) {
    return (
      <Group gap={6} wrap="nowrap">
        <IconMapPin size={18} aria-hidden />
        <Text fw={600} truncate>
          {sucursal?.nombre ?? "Sucursal"}
        </Text>
      </Group>
    );
  }

  return (
    <Select
      aria-label="Sucursal en la que trabajás"
      size="sm"
      w={{ base: 140, xs: 180 }}
      leftSection={<IconMapPin size={16} aria-hidden />}
      data={sucursales
        .filter((s) => s.activa)
        .map((s) => ({ value: String(s.id), label: s.nombre }))}
      value={sucursalId === null ? null : String(sucursalId)}
      onChange={(elegida) => elegida && elegir(Number(elegida))}
      comboboxProps={{ withinPortal: true }}
    />
  );
}
