import { ActionIcon, Button, Group, Table } from "@mantine/core";
import { IconChevronDown, IconChevronRight } from "@tabler/icons-react";
import { Dinero } from "../../componentes/Dinero";
import { EstadoVentaBadge } from "../../componentes/EstadoVentaBadge";
import type { Venta } from "../../tipos";
import { formatearFechaHora, formatearHora } from "../../utilidades/formato";
import { DetalleVenta } from "./DetalleVenta";

export type AccionVenta = "observar" | "confirmar" | "anular";

interface Props {
  venta: Venta;
  desplegada: boolean;
  soloHora: boolean;
  esDuenia: boolean;
  alDesplegar: () => void;
  alAccion: (accion: AccionVenta, venta: Venta) => void;
}

const COLUMNAS = 7;

// Una venta del historial. Observada: en gris. Anulada: tachada. Se despliega para ver los productos.
export function FilaVenta({ venta, desplegada, soloHora, esDuenia, alDesplegar, alAccion }: Props) {
  // El tachado va celda por celda: si se pone en la fila, también tacharía el estado y los botones
  const gris = { color: venta.estado === "valida" ? undefined : "var(--pl-tenue)" };
  const tachado = { textDecoration: venta.estado === "anulada" ? "line-through" : undefined };

  return (
    <>
      <Table.Tr style={gris}>
        <Table.Td w={44}>
          <ActionIcon
            color="gray"
            onClick={alDesplegar}
            aria-expanded={desplegada}
            aria-label={desplegada ? `Ocultar los productos de la venta ${venta.id}` : `Ver los productos de la venta ${venta.id}`}
          >
            {desplegada ? <IconChevronDown size={18} /> : <IconChevronRight size={18} />}
          </ActionIcon>
        </Table.Td>
        <Table.Td className="pl-numero" style={tachado}>
          {venta.id}
        </Table.Td>
        <Table.Td className="pl-numero" style={tachado}>{soloHora ? formatearHora(venta.fecha) : formatearFechaHora(venta.fecha)}</Table.Td>
        <Table.Td style={tachado}>{venta.usuario}</Table.Td>
        <Table.Td style={tachado}>{venta.medio_pago === "efectivo" ? "Efectivo" : "Transferencia"}</Table.Td>
        <Table.Td ta="right" style={tachado}>
          <Dinero valor={venta.total} fw={600} />
        </Table.Td>
        <Table.Td>
          <Group gap="xs" wrap="nowrap" justify="space-between">
            <EstadoVentaBadge estado={venta.estado} />
            <Group gap={4} wrap="nowrap">
              {venta.estado === "valida" && (
                <Button size="xs" variant="light" color="orange" onClick={() => alAccion("observar", venta)}>
                  Observar
                </Button>
              )}
              {esDuenia && venta.estado === "observada" && (
                <Button size="xs" variant="light" onClick={() => alAccion("confirmar", venta)}>
                  Confirmar
                </Button>
              )}
              {esDuenia && venta.estado !== "anulada" && (
                <Button size="xs" variant="light" color="red" onClick={() => alAccion("anular", venta)}>
                  Anular
                </Button>
              )}
            </Group>
          </Group>
        </Table.Td>
      </Table.Tr>
      {desplegada && (
        <Table.Tr>
          <Table.Td />
          <Table.Td colSpan={COLUMNAS - 1}>
            <DetalleVenta venta={venta} />
          </Table.Td>
        </Table.Tr>
      )}
    </>
  );
}
