import { Badge, Group, Paper, Table, Text } from "@mantine/core";
import { IconCashRegister } from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { Dinero } from "../../componentes/Dinero";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { FiltroFechas } from "../../componentes/FiltroFechas";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { SelectSucursal } from "../../componentes/SelectSucursal";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import type { Caja } from "../../tipos";
import { aCentavos } from "../../utilidades/decimal";
import { formatearFechaHora } from "../../utilidades/formato";
import { rangoDelMes, type RangoFechas } from "../../utilidades/rangos";
import clases from "./caja.module.css";

function signoDe(caja: Caja): "cero" | "sobra" | "falta" | null {
  if (caja.diferencia === null) return null;
  const centavos = aCentavos(caja.diferencia);
  return centavos === 0 ? "cero" : centavos > 0 ? "sobra" : "falta";
}

// Cierres de caja de las sucursales (solo la dueña), con la diferencia resaltada.
export function PantallaCierres() {
  const { nombreDe } = useSucursalActiva();
  const [sucursalId, setSucursalId] = useState<number | null>(null);
  const [rango, setRango] = useState<RangoFechas>(rangoDelMes);

  const cajas = usePedido(`cajas-${sucursalId}-${rango.desde}-${rango.hasta}`, () =>
    api.listarCajas({ sucursal_id: sucursalId, desde: rango.desde, hasta: rango.hasta }),
  );
  const lista = cajas.datos ?? [];
  const conDiferencia = lista.filter((caja) => {
    const signo = signoDe(caja);
    return signo === "sobra" || signo === "falta";
  }).length;

  return (
    <>
      <EncabezadoPagina
        titulo="Cierres de caja"
        detalle={
          lista.length > 0
            ? `${lista.length} ${lista.length === 1 ? "caja" : "cajas"}, ${conDiferencia} con diferencia`
            : "Lo que se esperaba y lo que se contó al cerrar cada caja"
        }
      />
      <Group gap="sm" mb="md" wrap="wrap">
        <SelectSucursal conTodas valor={sucursalId} alCambiar={setSucursalId} size="sm" w={200} aria-label="Sucursal" />
        <FiltroFechas rango={rango} alCambiar={setRango} />
      </Group>

      {cajas.error && <ErrorCarga mensaje={cajas.error} alReintentar={cajas.recargar} />}

      <Paper withBorder radius="sm">
        {lista.length === 0 && !cajas.cargando ? (
          <PaginaVacia icono={<IconCashRegister size={28} />} titulo="No hay cajas en este período" />
        ) : (
          <Table.ScrollContainer minWidth={900}>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Sucursal</Table.Th>
                  <Table.Th>Apertura</Table.Th>
                  <Table.Th>Cierre</Table.Th>
                  <Table.Th ta="right">Fondo</Table.Th>
                  <Table.Th ta="right">Esperado</Table.Th>
                  <Table.Th ta="right">Contado</Table.Th>
                  <Table.Th ta="right">Diferencia</Table.Th>
                  <Table.Th>Observación</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {lista.map((caja) => {
                  const signo = signoDe(caja);
                  return (
                    <Table.Tr key={caja.id}>
                      <Table.Td fw={600}>{nombreDe(caja.sucursal_id)}</Table.Td>
                      <Table.Td>
                        <Text size="sm" className="pl-numero">
                          {formatearFechaHora(caja.abierta_en)}
                        </Text>
                        <Text size="sm" c="var(--pl-tenue)">
                          {caja.abierta_por}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        {caja.estado === "abierta" ? (
                          <Badge color="frasco">Abierta</Badge>
                        ) : (
                          <>
                            <Text size="sm" className="pl-numero">
                              {formatearFechaHora(caja.cerrada_en)}
                            </Text>
                            <Text size="sm" c="var(--pl-tenue)">
                              {caja.cerrada_por}
                            </Text>
                          </>
                        )}
                      </Table.Td>
                      <Table.Td ta="right">
                        <Dinero valor={caja.fondo_inicial} />
                      </Table.Td>
                      <Table.Td ta="right">{caja.efectivo_esperado ? <Dinero valor={caja.efectivo_esperado} /> : "—"}</Table.Td>
                      <Table.Td ta="right">{caja.efectivo_contado ? <Dinero valor={caja.efectivo_contado} /> : "—"}</Table.Td>
                      <Table.Td ta="right">
                        {caja.diferencia === null ? (
                          "—"
                        ) : (
                          <Text component="span" className={clases.diferencia} data-signo={signo} fw={700} py={4} px={8}>
                            <Dinero valor={caja.diferencia} />
                          </Text>
                        )}
                      </Table.Td>
                      <Table.Td maw={240}>
                        <Text size="sm">{caja.observacion ?? ""}</Text>
                      </Table.Td>
                    </Table.Tr>
                  );
                })}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Paper>
    </>
  );
}
