import { Drawer, Group, Select, Stack, Table, Text } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { IconHistory } from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { Cantidad } from "../../componentes/Cantidad";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { FiltroFechas } from "../../componentes/FiltroFechas";
import { rangoUltimosDias, type RangoFechas } from "../../utilidades/rangos";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { usePedido } from "../../hooks/usePedido";
import type { FilaStock, Movimiento, TipoMovimiento } from "../../tipos";
import { formatearFechaHora } from "../../utilidades/formato";
import { TipoMovimientoBadge } from "./TipoMovimientoBadge";
import { OPCIONES_TIPO } from "./tiposMovimiento";

interface Props {
  abierto: boolean;
  sucursalId: number;
  nombreSucursal: string;
  filas: FilaStock[];
  productoInicial: number | null;
  alCerrar: () => void;
}

// De dónde sale cada movimiento: la venta, la compra, el traspaso o el motivo escrito
function origenDe(movimiento: Movimiento): string {
  const partes: string[] = [];
  if (movimiento.venta_id) partes.push(`Venta ${movimiento.venta_id}`);
  if (movimiento.compra_id) partes.push(`Compra ${movimiento.compra_id}`);
  if (movimiento.traspaso_id) partes.push(`Traspaso ${movimiento.traspaso_id}`);
  if (movimiento.motivo) partes.push(movimiento.motivo);
  return partes.join(": ") || "—";
}

// Libro de movimientos de stock de la sucursal, del más nuevo al más viejo.
export function DrawerMovimientos({ abierto, sucursalId, nombreSucursal, filas, productoInicial, alCerrar }: Props) {
  const [productoId, setProductoId] = useState<number | null>(productoInicial);
  const [tipo, setTipo] = useState<TipoMovimiento | null>(null);
  const [rango, setRango] = useState<RangoFechas>(() => rangoUltimosDias(7));
  const pantallaChica = useMediaQuery("(max-width: 48em)");

  const clave = abierto ? `movimientos-${sucursalId}-${productoId}-${tipo}-${rango.desde}-${rango.hasta}` : null;
  const movimientos = usePedido(clave, () =>
    api.listarMovimientos({ sucursal_id: sucursalId, producto_id: productoId, tipo, desde: rango.desde, hasta: rango.hasta, limite: 100 }),
  );
  const lista = movimientos.datos ?? [];

  return (
    <Drawer
      opened={abierto}
      onClose={alCerrar}
      position="right"
      size={pantallaChica ? "100%" : "xl"}
      title={<Text fw={700} size="lg">Movimientos de stock en {nombreSucursal}</Text>}
    >
      <Stack gap="sm">
        <Group gap="xs" wrap="wrap">
          <Select
            aria-label="Producto"
            placeholder="Todos los productos"
            size="sm"
            w={220}
            searchable
            clearable
            allowDeselect
            data={filas.map((f) => ({ value: String(f.producto_id), label: f.nombre }))}
            value={productoId === null ? null : String(productoId)}
            onChange={(valor) => setProductoId(valor ? Number(valor) : null)}
          />
          <Select
            aria-label="Tipo de movimiento"
            placeholder="Todos los tipos"
            size="sm"
            w={190}
            clearable
            allowDeselect
            data={OPCIONES_TIPO}
            value={tipo}
            onChange={(valor) => setTipo(valor as TipoMovimiento | null)}
          />
        </Group>
        <FiltroFechas rango={rango} alCambiar={setRango} />

        {movimientos.error && <ErrorCarga mensaje={movimientos.error} alReintentar={movimientos.recargar} />}

        {lista.length === 0 && !movimientos.cargando ? (
          <PaginaVacia icono={<IconHistory size={28} />} titulo="No hay movimientos con estos filtros" />
        ) : (
          <Table.ScrollContainer minWidth={720}>
            <Table fz="sm" verticalSpacing="xs">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Fecha</Table.Th>
                  <Table.Th>Producto</Table.Th>
                  <Table.Th>Tipo</Table.Th>
                  <Table.Th ta="right">Cantidad</Table.Th>
                  <Table.Th ta="right">Queda</Table.Th>
                  <Table.Th>Quién</Table.Th>
                  <Table.Th>Detalle</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {lista.map((movimiento) => (
                  <Table.Tr key={movimiento.id}>
                    <Table.Td className="pl-numero">{formatearFechaHora(movimiento.fecha)}</Table.Td>
                    <Table.Td>{movimiento.producto}</Table.Td>
                    <Table.Td>
                      <TipoMovimientoBadge tipo={movimiento.tipo} />
                    </Table.Td>
                    <Table.Td ta="right">
                      <Cantidad valor={movimiento.cantidad} unidad={movimiento.unidad} conSigno fw={600} />
                    </Table.Td>
                    <Table.Td ta="right">
                      <Cantidad valor={movimiento.saldo_resultante} unidad={movimiento.unidad} />
                    </Table.Td>
                    <Table.Td>{movimiento.usuario}</Table.Td>
                    <Table.Td maw={220}>{origenDe(movimiento)}</Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
        {lista.length === 100 && (
          <Text size="sm" c="var(--pl-tenue)">
            Se muestran los últimos 100. Achicá el período o elegí un producto para ver los anteriores.
          </Text>
        )}
      </Stack>
    </Drawer>
  );
}
