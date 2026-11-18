import { Stack, Table, Text } from "@mantine/core";
import { Cantidad } from "../../componentes/Cantidad";
import { Dinero } from "../../componentes/Dinero";
import type { Venta } from "../../tipos";
import { formatearFechaHora } from "../../utilidades/formato";

// Lo que se ve al desplegar una venta: sus productos y la historia de la observación.
export function DetalleVenta({ venta }: { venta: Venta }) {
  return (
    <Stack gap="xs" py="xs">
      <Table withRowBorders={false} verticalSpacing={4} highlightOnHover={false} fz="sm">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Producto</Table.Th>
            <Table.Th ta="right">Cantidad</Table.Th>
            <Table.Th ta="right">Precio</Table.Th>
            <Table.Th ta="right">Subtotal</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {venta.items.map((item) => (
            <Table.Tr key={item.producto_id}>
              <Table.Td>{item.producto}</Table.Td>
              <Table.Td ta="right">
                <Cantidad valor={item.cantidad} unidad={item.unidad} />
              </Table.Td>
              <Table.Td ta="right">
                <Dinero valor={item.precio_unitario} />
              </Table.Td>
              <Table.Td ta="right">
                <Dinero valor={item.subtotal} />
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      {venta.motivo_observacion && (
        <Text size="sm">
          <b>Observada</b> por {venta.observada_por ?? "—"} el {formatearFechaHora(venta.observada_en)}:{" "}
          {venta.motivo_observacion}
        </Text>
      )}
      {venta.resuelta_en && (
        <Text size="sm">
          <b>{venta.estado === "anulada" ? "Anulada" : "Confirmada"}</b> por {venta.resuelta_por ?? "—"} el{" "}
          {formatearFechaHora(venta.resuelta_en)}
          {venta.motivo_resolucion ? `: ${venta.motivo_resolucion}` : "."}
        </Text>
      )}
    </Stack>
  );
}
