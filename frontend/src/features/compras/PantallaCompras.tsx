import { ActionIcon, Button, Group, Paper, Select, Table, Text } from "@mantine/core";
import { IconChevronDown, IconChevronRight, IconPlus, IconTruckDelivery } from "@tabler/icons-react";
import { Fragment, useState } from "react";
import { api } from "../../api/cliente";
import { Cantidad } from "../../componentes/Cantidad";
import { Dinero } from "../../componentes/Dinero";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { FiltroFechas } from "../../componentes/FiltroFechas";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { SelectSucursal } from "../../componentes/SelectSucursal";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import { desdeCentavos, sumarCentavos } from "../../utilidades/decimal";
import { formatearFechaHora, formatearPrecio } from "../../utilidades/formato";
import { rangoDelMes, type RangoFechas } from "../../utilidades/rangos";
import { ModalNuevaCompra } from "./ModalNuevaCompra";

// Compras a proveedores (solo la dueña): listado por período y alta de compras nuevas.
export function PantallaCompras() {
  const { nombreDe } = useSucursalActiva();
  const [sucursalId, setSucursalId] = useState<number | null>(null);
  const [proveedorId, setProveedorId] = useState<number | null>(null);
  const [rango, setRango] = useState<RangoFechas>(rangoDelMes);
  const [desplegada, setDesplegada] = useState<number | null>(null);
  const [nueva, setNueva] = useState(false);

  const proveedores = usePedido("proveedores-filtro", () => api.listarProveedores(true));
  const compras = usePedido(`compras-${sucursalId}-${proveedorId}-${rango.desde}-${rango.hasta}`, () =>
    api.listarCompras({ sucursal_id: sucursalId, proveedor_id: proveedorId, desde: rango.desde, hasta: rango.hasta }),
  );
  const lista = compras.datos ?? [];
  const total = sumarCentavos(lista.map((compra) => compra.total));

  return (
    <>
      <EncabezadoPagina
        titulo="Compras"
        detalle={lista.length > 0 ? `${lista.length} ${lista.length === 1 ? "compra" : "compras"} por ${formatearPrecio(desdeCentavos(total))}` : "Mercadería que entra de los proveedores"}
        acciones={
          <Button leftSection={<IconPlus size={18} />} onClick={() => setNueva(true)}>
            Nueva compra
          </Button>
        }
      />
      <Group gap="sm" mb="md" wrap="wrap">
        <SelectSucursal conTodas valor={sucursalId} alCambiar={setSucursalId} size="sm" w={200} aria-label="Sucursal" />
        <Select
          aria-label="Proveedor"
          size="sm"
          w={220}
          data={[
            { value: "", label: "Todos los proveedores" },
            ...(proveedores.datos ?? []).map((p) => ({ value: String(p.id), label: p.nombre })),
          ]}
          value={proveedorId === null ? "" : String(proveedorId)}
          onChange={(valor) => setProveedorId(valor ? Number(valor) : null)}
        />
        <FiltroFechas rango={rango} alCambiar={setRango} />
      </Group>

      {compras.error && <ErrorCarga mensaje={compras.error} alReintentar={compras.recargar} />}

      <Paper withBorder radius="sm">
        {lista.length === 0 && !compras.cargando ? (
          <PaginaVacia
            icono={<IconTruckDelivery size={28} />}
            titulo="No hay compras en este período"
            accion={
              <Button variant="default" leftSection={<IconPlus size={18} />} onClick={() => setNueva(true)}>
                Registrar una compra
              </Button>
            }
          />
        ) : (
          <Table.ScrollContainer minWidth={720}>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th />
                  <Table.Th>Fecha</Table.Th>
                  <Table.Th>Proveedor</Table.Th>
                  <Table.Th>Sucursal</Table.Th>
                  <Table.Th>Comprobante</Table.Th>
                  <Table.Th ta="right">Total</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {lista.map((compra) => (
                  <Fragment key={compra.id}>
                    <Table.Tr>
                      <Table.Td w={44}>
                        <ActionIcon
                          color="gray"
                          aria-expanded={desplegada === compra.id}
                          aria-label={`Ver los productos de la compra ${compra.id}`}
                          onClick={() => setDesplegada(desplegada === compra.id ? null : compra.id)}
                        >
                          {desplegada === compra.id ? <IconChevronDown size={18} /> : <IconChevronRight size={18} />}
                        </ActionIcon>
                      </Table.Td>
                      <Table.Td className="pl-numero">{formatearFechaHora(compra.fecha)}</Table.Td>
                      <Table.Td fw={600}>{compra.proveedor}</Table.Td>
                      <Table.Td>{nombreDe(compra.sucursal_id)}</Table.Td>
                      <Table.Td>{compra.comprobante ?? "—"}</Table.Td>
                      <Table.Td ta="right">
                        <Dinero valor={compra.total} fw={700} />
                      </Table.Td>
                    </Table.Tr>
                    {desplegada === compra.id && (
                      <Table.Tr>
                        <Table.Td />
                        <Table.Td colSpan={5}>
                          <Table withRowBorders={false} verticalSpacing={4} highlightOnHover={false} fz="sm">
                            <Table.Tbody>
                              {compra.items.map((item) => (
                                <Table.Tr key={item.producto_id}>
                                  <Table.Td>{item.producto}</Table.Td>
                                  <Table.Td ta="right">
                                    <Cantidad valor={item.cantidad} unidad={item.unidad} />
                                  </Table.Td>
                                  <Table.Td ta="right">
                                    <Dinero valor={item.costo_unitario} />
                                  </Table.Td>
                                  <Table.Td ta="right">
                                    <Dinero valor={item.subtotal} />
                                  </Table.Td>
                                </Table.Tr>
                              ))}
                            </Table.Tbody>
                          </Table>
                          <Text size="sm" c="var(--pl-tenue)">
                            Cargada por {compra.usuario}.
                          </Text>
                        </Table.Td>
                      </Table.Tr>
                    )}
                  </Fragment>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Paper>

      {nueva && (
        <ModalNuevaCompra
          alCerrar={() => setNueva(false)}
          alGuardar={() => {
            setNueva(false);
            compras.recargar();
          }}
        />
      )}
    </>
  );
}
