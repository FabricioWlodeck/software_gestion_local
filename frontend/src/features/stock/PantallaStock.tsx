import { ActionIcon, Badge, Button, Group, Menu, Paper, Switch, Table, TextInput } from "@mantine/core";
import {
  IconAdjustments,
  IconArrowsExchange,
  IconDots,
  IconHistory,
  IconPackages,
  IconSearch,
  IconTrash,
} from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { Cantidad } from "../../componentes/Cantidad";
import { Dinero } from "../../componentes/Dinero";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import { useSesion } from "../auth/sesion";
import { coincide } from "../ventas/productoEnVenta";
import { DrawerMovimientos } from "./DrawerMovimientos";
import { ModalMovimientoStock, type TipoCorreccion } from "./ModalMovimientoStock";
import { ModalTraspaso } from "./ModalTraspaso";
import clases from "./stock.module.css";

type Dialogo =
  | { tipo: "correccion"; inicial: TipoCorreccion; productoId: number | null }
  | { tipo: "traspaso"; productoId: number | null }
  | { tipo: "movimientos"; productoId: number | null };

// Stock de la sucursal activa: cuánto hay, el mínimo y las correcciones (merma, ajuste, traspaso).
export function PantallaStock() {
  const { esDuenia } = useSesion();
  const { sucursalId, sucursal } = useSucursalActiva();
  const nombreSucursal = sucursal?.nombre ?? "la sucursal";
  const stock = usePedido(sucursalId === null ? null : `stock-${sucursalId}`, () => api.listarStock(sucursalId ?? 0));

  const [busqueda, setBusqueda] = useState("");
  const [soloBajos, setSoloBajos] = useState(false);
  const [dialogo, setDialogo] = useState<Dialogo | null>(null);
  // El drawer se monta de nuevo cada vez que se abre, con el producto elegido
  const [vezDrawer, setVezDrawer] = useState(0);

  const filas = stock.datos ?? [];
  const bajos = filas.filter((fila) => fila.bajo_minimo).length;
  const visibles = filas
    .filter((fila) => (!soloBajos || fila.bajo_minimo) && coincide({ ...fila, id: fila.producto_id, stock: fila.cantidad }, busqueda))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));

  function abrirMovimientos(productoId: number | null) {
    setVezDrawer((vez) => vez + 1);
    setDialogo({ tipo: "movimientos", productoId });
  }

  const alGuardar = () => {
    setDialogo(null);
    stock.recargar();
  };

  return (
    <>
      <EncabezadoPagina
        titulo="Stock"
        detalle={
          bajos > 0
            ? `${nombreSucursal}: ${bajos} ${bajos === 1 ? "producto está" : "productos están"} por debajo del mínimo`
            : nombreSucursal
        }
        acciones={
          <>
            <Button
              variant="default"
              leftSection={<IconTrash size={18} />}
              onClick={() => setDialogo({ tipo: "correccion", inicial: "merma", productoId: null })}
            >
              Merma o ajuste
            </Button>
            {esDuenia && (
              <Button
                variant="default"
                leftSection={<IconArrowsExchange size={18} />}
                onClick={() => setDialogo({ tipo: "traspaso", productoId: null })}
              >
                Traspaso
              </Button>
            )}
            <Button variant="default" leftSection={<IconHistory size={18} />} onClick={() => abrirMovimientos(null)}>
              Movimientos
            </Button>
          </>
        }
      />

      <Group gap="md" mb="md" wrap="wrap">
        <TextInput
          aria-label="Buscar producto"
          placeholder="Buscar producto"
          size="sm"
          w={260}
          leftSection={<IconSearch size={16} aria-hidden />}
          value={busqueda}
          onChange={(evento) => setBusqueda(evento.currentTarget.value)}
        />
        <Switch
          label={`Solo bajo mínimo (${bajos})`}
          checked={soloBajos}
          onChange={(evento) => setSoloBajos(evento.currentTarget.checked)}
          color="orange"
        />
      </Group>

      {stock.error && <ErrorCarga mensaje={stock.error} alReintentar={stock.recargar} />}

      <Paper withBorder radius="sm">
        {visibles.length === 0 && !stock.cargando ? (
          <PaginaVacia
            icono={<IconPackages size={28} />}
            titulo={soloBajos ? "Ningún producto está por debajo del mínimo" : "No hay productos para mostrar"}
            descripcion={busqueda ? "Probá con otra palabra del nombre." : undefined}
          />
        ) : (
          <Table.ScrollContainer minWidth={640}>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Producto</Table.Th>
                  <Table.Th ta="right">Hay</Table.Th>
                  <Table.Th ta="right">Mínimo</Table.Th>
                  <Table.Th ta="right">Precio</Table.Th>
                  <Table.Th />
                  <Table.Th w={52} />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {visibles.map((fila) => (
                  <Table.Tr key={fila.producto_id} className={fila.bajo_minimo ? clases.bajo : undefined}>
                    <Table.Td fw={600}>{fila.nombre}</Table.Td>
                    <Table.Td ta="right">
                      <Cantidad valor={fila.cantidad} unidad={fila.unidad} fw={700} />
                    </Table.Td>
                    <Table.Td ta="right">
                      <Cantidad valor={fila.minimo} unidad={fila.unidad} c="var(--pl-tenue)" />
                    </Table.Td>
                    <Table.Td ta="right">
                      <Dinero valor={fila.precio} />
                    </Table.Td>
                    <Table.Td>
                      {fila.bajo_minimo && (
                        <Badge color="orange" variant="filled">
                          Reponer
                        </Badge>
                      )}
                    </Table.Td>
                    <Table.Td>
                      <Menu position="bottom-end" withinPortal>
                        <Menu.Target>
                          <ActionIcon color="gray" aria-label={`Acciones de ${fila.nombre}`}>
                            <IconDots size={20} />
                          </ActionIcon>
                        </Menu.Target>
                        <Menu.Dropdown>
                          <Menu.Item
                            leftSection={<IconTrash size={16} />}
                            onClick={() => setDialogo({ tipo: "correccion", inicial: "merma", productoId: fila.producto_id })}
                          >
                            Registrar merma
                          </Menu.Item>
                          <Menu.Item
                            leftSection={<IconAdjustments size={16} />}
                            onClick={() => setDialogo({ tipo: "correccion", inicial: "ajuste", productoId: fila.producto_id })}
                          >
                            Ajustar por conteo
                          </Menu.Item>
                          {esDuenia && (
                            <Menu.Item
                              leftSection={<IconArrowsExchange size={16} />}
                              onClick={() => setDialogo({ tipo: "traspaso", productoId: fila.producto_id })}
                            >
                              Traspasar
                            </Menu.Item>
                          )}
                          <Menu.Item leftSection={<IconHistory size={16} />} onClick={() => abrirMovimientos(fila.producto_id)}>
                            Ver movimientos
                          </Menu.Item>
                        </Menu.Dropdown>
                      </Menu>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Paper>

      {sucursalId !== null && dialogo?.tipo === "correccion" && (
        <ModalMovimientoStock
          tipoInicial={dialogo.inicial}
          productoInicial={dialogo.productoId}
          filas={filas}
          sucursalId={sucursalId}
          nombreSucursal={nombreSucursal}
          alCerrar={() => setDialogo(null)}
          alGuardar={alGuardar}
        />
      )}
      {sucursalId !== null && dialogo?.tipo === "traspaso" && (
        <ModalTraspaso
          productoInicial={dialogo.productoId}
          origenInicial={sucursalId}
          alCerrar={() => setDialogo(null)}
          alGuardar={alGuardar}
        />
      )}
      {sucursalId !== null && (
        <DrawerMovimientos
          key={vezDrawer}
          abierto={dialogo?.tipo === "movimientos"}
          sucursalId={sucursalId}
          nombreSucursal={nombreSucursal}
          filas={filas}
          productoInicial={dialogo?.tipo === "movimientos" ? dialogo.productoId : null}
          alCerrar={() => setDialogo(null)}
        />
      )}
    </>
  );
}
