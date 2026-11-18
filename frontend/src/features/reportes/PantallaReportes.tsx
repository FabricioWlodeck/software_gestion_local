import { Badge, Group, Paper, SimpleGrid, Skeleton, Stack, Table, Text, Title } from "@mantine/core";
import { useState, type ReactNode } from "react";
import { api } from "../../api/cliente";
import { Cantidad } from "../../componentes/Cantidad";
import { Dinero } from "../../componentes/Dinero";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { FiltroFechas } from "../../componentes/FiltroFechas";
import { SelectSucursal } from "../../componentes/SelectSucursal";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import { aCentavos, desdeCentavos } from "../../utilidades/decimal";
import { formatearFecha, formatearFechaHora, formatearPrecio } from "../../utilidades/formato";
import { rangoUltimosDias, type RangoFechas } from "../../utilidades/rangos";
import { GraficoVentasDiarias } from "./GraficoVentasDiarias";
import clases from "./reportes.module.css";

function Seccion({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <Paper withBorder radius="sm" p="md">
      <Title order={4} mb="sm">
        {titulo}
      </Title>
      {children}
    </Paper>
  );
}

function Cifra({ texto, children, principal = false }: { texto: string; children: ReactNode; principal?: boolean }) {
  return (
    <div className={`${clases.cifra} ${principal ? clases.cifraPrincipal : ""}`}>
      <Text size="sm" c={principal ? undefined : "var(--pl-tenue)"}>
        {texto}
      </Text>
      <Text className="pl-cifra" fz={principal ? 34 : 26} lh={1.15}>
        {children}
      </Text>
    </div>
  );
}

// Reportes del negocio (solo la dueña). Los totales cuentan solo las ventas válidas.
export function PantallaReportes() {
  const { nombreDe } = useSucursalActiva();
  const [rango, setRango] = useState<RangoFechas>(() => rangoUltimosDias(7));
  const [sucursalId, setSucursalId] = useState<number | null>(null);

  const filtro = { desde: rango.desde, hasta: rango.hasta, sucursal_id: sucursalId };
  const clave = `${rango.desde}-${rango.hasta}-${sucursalId}`;
  const resumen = usePedido(`resumen-${clave}`, () => api.resumen(filtro));
  const diarias = usePedido(`diarias-${clave}`, () => api.ventasDiarias(filtro));
  const r = resumen.datos;

  const promedio = r && r.cantidad_ventas > 0 ? desdeCentavos(Math.round(aCentavos(r.total) / r.cantidad_ventas)) : null;

  return (
    <Stack gap="md">
      <EncabezadoPagina
        titulo="Reportes"
        detalle={`${sucursalId === null ? "Todas las sucursales" : nombreDe(sucursalId)}, del ${formatearFecha(rango.desde)} al ${formatearFecha(rango.hasta)}`}
      />
      <Group gap="sm" wrap="wrap">
        <FiltroFechas rango={rango} alCambiar={setRango} />
        <SelectSucursal conTodas valor={sucursalId} alCambiar={setSucursalId} size="sm" w={200} aria-label="Sucursal" />
      </Group>

      {resumen.error && <ErrorCarga mensaje={resumen.error} alReintentar={resumen.recargar} />}

      {r === null ? (
        resumen.cargando && <Skeleton h={84} radius="sm" />
      ) : (
        <div className={clases.cifras}>
          <Cifra texto="Total vendido" principal>
            {formatearPrecio(r.total)}
          </Cifra>
          <Cifra texto="Ventas">{r.cantidad_ventas}</Cifra>
          <Cifra texto="Ticket promedio">{promedio ? formatearPrecio(promedio) : "—"}</Cifra>
          <Cifra texto="En efectivo">{formatearPrecio(r.por_medio.efectivo ?? "0")}</Cifra>
          <Cifra texto="Por transferencia">{formatearPrecio(r.por_medio.transferencia ?? "0")}</Cifra>
        </div>
      )}
      {r && (r.ventas_observadas > 0 || r.ventas_anuladas > 0) && (
        <Text>
          No entran en el total: {r.ventas_observadas} {r.ventas_observadas === 1 ? "venta observada" : "ventas observadas"} y{" "}
          {r.ventas_anuladas} {r.ventas_anuladas === 1 ? "anulada" : "anuladas"}. Se revisan en Ventas.
        </Text>
      )}

      <Seccion titulo="Ventas por día">
        {diarias.error ? (
          <ErrorCarga mensaje={diarias.error} alReintentar={diarias.recargar} />
        ) : diarias.datos ? (
          <GraficoVentasDiarias filas={diarias.datos} desde={rango.desde} hasta={rango.hasta} />
        ) : (
          <Skeleton h={220} />
        )}
      </Seccion>

      {r && (
        <>
          <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="md">
            <Seccion titulo="Por sucursal">
              <Table.ScrollContainer minWidth={320}>
                <Table>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Sucursal</Table.Th>
                      <Table.Th ta="right">Ventas</Table.Th>
                      <Table.Th ta="right">Total</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {r.por_sucursal.map((fila) => (
                      <Table.Tr key={fila.sucursal_id}>
                        <Table.Td fw={600}>{fila.nombre}</Table.Td>
                        <Table.Td ta="right" className="pl-numero">
                          {fila.cantidad_ventas}
                        </Table.Td>
                        <Table.Td ta="right">
                          <Dinero valor={fila.total} fw={700} />
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            </Seccion>

            <Seccion titulo="Lo más vendido">
              {r.top_productos.length === 0 ? (
                <Text c="var(--pl-tenue)">No hubo ventas en el período.</Text>
              ) : (
                <Table.ScrollContainer minWidth={360}>
                  <Table>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Producto</Table.Th>
                        <Table.Th ta="right">Cantidad</Table.Th>
                        <Table.Th ta="right">Total</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {r.top_productos.map((fila) => (
                        <Table.Tr key={fila.producto_id}>
                          <Table.Td fw={600}>{fila.nombre}</Table.Td>
                          <Table.Td ta="right">
                            <Cantidad valor={fila.cantidad} unidad={fila.unidad} />
                          </Table.Td>
                          <Table.Td ta="right">
                            <Dinero valor={fila.total} />
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                </Table.ScrollContainer>
              )}
            </Seccion>
          </SimpleGrid>

          <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="md">
            <Seccion titulo="Mermas y ajustes">
              {r.mermas_y_ajustes.length === 0 ? (
                <Text c="var(--pl-tenue)">No hubo mermas ni ajustes en el período.</Text>
              ) : (
                <Table.ScrollContainer minWidth={520}>
                  <Table fz="sm">
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Fecha</Table.Th>
                        <Table.Th>Producto</Table.Th>
                        <Table.Th ta="right">Cantidad</Table.Th>
                        <Table.Th>Quién y por qué</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {r.mermas_y_ajustes.map((fila, indice) => (
                        <Table.Tr key={`${fila.fecha}-${indice}`}>
                          <Table.Td className="pl-numero">{formatearFechaHora(fila.fecha)}</Table.Td>
                          <Table.Td>
                            <Text size="sm" fw={600}>
                              {fila.producto}
                            </Text>
                            <Group gap={4}>
                              <Badge size="sm" color={fila.tipo === "merma" ? "red" : "grape"}>
                                {fila.tipo === "merma" ? "Merma" : "Ajuste"}
                              </Badge>
                              <Text size="xs" c="var(--pl-tenue)">
                                {nombreDe(fila.sucursal_id)}
                              </Text>
                            </Group>
                          </Table.Td>
                          <Table.Td ta="right">
                            <Cantidad valor={fila.cantidad} unidad={fila.unidad} conSigno />
                          </Table.Td>
                          <Table.Td>
                            {fila.usuario}
                            {fila.motivo ? `: ${fila.motivo}` : ""}
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                </Table.ScrollContainer>
              )}
            </Seccion>

            <Seccion titulo="Diferencias de caja">
              {r.diferencias_caja.length === 0 ? (
                <Text c="var(--pl-tenue)">Todas las cajas cerraron sin diferencia.</Text>
              ) : (
                <Table fz="sm">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Cierre</Table.Th>
                      <Table.Th>Sucursal</Table.Th>
                      <Table.Th ta="right">Diferencia</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {r.diferencias_caja.map((fila) => (
                      <Table.Tr key={fila.caja_id}>
                        <Table.Td className="pl-numero">{formatearFechaHora(fila.cerrada_en)}</Table.Td>
                        <Table.Td>{nombreDe(fila.sucursal_id)}</Table.Td>
                        <Table.Td ta="right">
                          <Dinero valor={fila.diferencia} fw={700} c={aCentavos(fila.diferencia) < 0 ? "red" : undefined} />
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              )}
            </Seccion>
          </SimpleGrid>
        </>
      )}
    </Stack>
  );
}
