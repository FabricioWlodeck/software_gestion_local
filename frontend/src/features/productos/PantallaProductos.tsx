import { ActionIcon, Badge, Button, Group, Paper, Stack, Switch, Table, Text, TextInput } from "@mantine/core";
import { IconCheese, IconPencil, IconPlus, IconSearch } from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { Cantidad } from "../../componentes/Cantidad";
import { Dinero } from "../../componentes/Dinero";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import type { Producto } from "../../tipos";
import { formatearPorcentaje } from "../../utilidades/formato";
import { coincide } from "../ventas/productoEnVenta";
import { ModalProducto } from "./ModalProducto";

// Catálogo de productos con precios, costos y stock por sucursal (solo la dueña).
export function PantallaProductos() {
  const { nombreDe } = useSucursalActiva();
  const [inactivos, setInactivos] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  // undefined = cerrado, null = producto nuevo
  const [editando, setEditando] = useState<Producto | null | undefined>(undefined);

  const productos = usePedido(`productos-${inactivos}`, () => api.listarProductos({ incluir_inactivos: inactivos }));
  const lista = (productos.datos ?? [])
    .filter((producto) => coincide({ ...producto, stock: "0" }, busqueda))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));

  return (
    <>
      <EncabezadoPagina
        titulo="Productos y precios"
        detalle="Lo que se vende en el mostrador, con su precio y el stock de cada sucursal"
        acciones={
          <Button leftSection={<IconPlus size={18} />} onClick={() => setEditando(null)}>
            Nuevo producto
          </Button>
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
          label="Mostrar los inactivos"
          checked={inactivos}
          onChange={(evento) => setInactivos(evento.currentTarget.checked)}
        />
      </Group>

      {productos.error && <ErrorCarga mensaje={productos.error} alReintentar={productos.recargar} />}

      <Paper withBorder radius="sm">
        {lista.length === 0 && !productos.cargando ? (
          <PaginaVacia
            icono={<IconCheese size={28} />}
            titulo={busqueda ? "Ningún producto coincide con la búsqueda" : "Todavía no hay productos"}
            accion={
              !busqueda && (
                <Button leftSection={<IconPlus size={18} />} onClick={() => setEditando(null)}>
                  Nuevo producto
                </Button>
              )
            }
          />
        ) : (
          <Table.ScrollContainer minWidth={820}>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Producto</Table.Th>
                  <Table.Th ta="right">Precio</Table.Th>
                  <Table.Th>Cómo se calcula</Table.Th>
                  <Table.Th ta="right">Último costo</Table.Th>
                  <Table.Th>Stock</Table.Th>
                  <Table.Th w={52} />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {lista.map((producto) => (
                  <Table.Tr key={producto.id} style={{ opacity: producto.activo ? 1 : 0.6 }}>
                    <Table.Td>
                      <Text fw={600}>{producto.nombre}</Text>
                      <Group gap={6}>
                        <Text size="sm" c="var(--pl-tenue)">
                          Por {producto.unidad === "kg" ? "kilo" : "unidad"}
                        </Text>
                        {!producto.activo && (
                          <Badge color="gray" size="sm">
                            Inactivo
                          </Badge>
                        )}
                      </Group>
                    </Table.Td>
                    <Table.Td ta="right">
                      <Dinero valor={producto.precio} cifra fz="xl" />
                    </Table.Td>
                    <Table.Td>
                      {producto.modo_precio === "margen" && producto.margen
                        ? `Costo + ${formatearPorcentaje(producto.margen)}`
                        : "Precio fijo"}
                    </Table.Td>
                    <Table.Td ta="right">{producto.costo_ultimo ? <Dinero valor={producto.costo_ultimo} /> : "—"}</Table.Td>
                    <Table.Td>
                      <Stack gap={0}>
                        {producto.stock.map((s) => (
                          <Text key={s.sucursal_id} size="sm">
                            {nombreDe(s.sucursal_id)}:{" "}
                            <Cantidad
                              valor={s.cantidad}
                              unidad={producto.unidad}
                              fw={600}
                              c={Number(s.cantidad) < Number(s.minimo) ? "var(--pl-alerta)" : undefined}
                            />
                          </Text>
                        ))}
                      </Stack>
                    </Table.Td>
                    <Table.Td>
                      <ActionIcon color="gray" aria-label={`Editar ${producto.nombre}`} onClick={() => setEditando(producto)}>
                        <IconPencil size={18} />
                      </ActionIcon>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Paper>

      {editando !== undefined && (
        <ModalProducto
          producto={editando}
          alCerrar={() => setEditando(undefined)}
          alGuardar={() => {
            setEditando(undefined);
            productos.recargar();
          }}
        />
      )}
    </>
  );
}
