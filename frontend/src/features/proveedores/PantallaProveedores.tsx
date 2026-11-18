import { ActionIcon, Badge, Button, Group, Paper, Switch, Table, Text } from "@mantine/core";
import { IconBuildingWarehouse, IconPencil, IconPlus } from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { usePedido } from "../../hooks/usePedido";
import type { Proveedor } from "../../tipos";
import { ModalProveedor } from "./ModalProveedor";

// Proveedores de mercadería (solo la dueña).
export function PantallaProveedores() {
  const [inactivos, setInactivos] = useState(false);
  const [editando, setEditando] = useState<Proveedor | null | undefined>(undefined);
  const proveedores = usePedido(`proveedores-${inactivos}`, () => api.listarProveedores(inactivos));
  const lista = [...(proveedores.datos ?? [])].sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));

  return (
    <>
      <EncabezadoPagina
        titulo="Proveedores"
        detalle="A quién se le compra la mercadería"
        acciones={
          <Button leftSection={<IconPlus size={18} />} onClick={() => setEditando(null)}>
            Nuevo proveedor
          </Button>
        }
      />
      <Switch
        mb="md"
        label="Mostrar los inactivos"
        checked={inactivos}
        onChange={(evento) => setInactivos(evento.currentTarget.checked)}
      />

      {proveedores.error && <ErrorCarga mensaje={proveedores.error} alReintentar={proveedores.recargar} />}

      <Paper withBorder radius="sm">
        {lista.length === 0 && !proveedores.cargando ? (
          <PaginaVacia
            icono={<IconBuildingWarehouse size={28} />}
            titulo="Todavía no hay proveedores"
            descripcion="Cargalos para poder registrar las compras."
          />
        ) : (
          <Table.ScrollContainer minWidth={640}>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Nombre</Table.Th>
                  <Table.Th>Teléfono</Table.Th>
                  <Table.Th>Email</Table.Th>
                  <Table.Th>Notas</Table.Th>
                  <Table.Th w={52} />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {lista.map((proveedor) => (
                  <Table.Tr key={proveedor.id} style={{ opacity: proveedor.activo ? 1 : 0.6 }}>
                    <Table.Td>
                      <Group gap={6}>
                        <Text fw={600}>{proveedor.nombre}</Text>
                        {!proveedor.activo && (
                          <Badge color="gray" size="sm">
                            Inactivo
                          </Badge>
                        )}
                      </Group>
                    </Table.Td>
                    <Table.Td>{proveedor.telefono ?? "—"}</Table.Td>
                    <Table.Td>{proveedor.email ?? "—"}</Table.Td>
                    <Table.Td maw={280}>
                      <Text size="sm">{proveedor.notas ?? ""}</Text>
                    </Table.Td>
                    <Table.Td>
                      <ActionIcon color="gray" aria-label={`Editar ${proveedor.nombre}`} onClick={() => setEditando(proveedor)}>
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
        <ModalProveedor
          proveedor={editando}
          alCerrar={() => setEditando(undefined)}
          alGuardar={() => {
            setEditando(undefined);
            proveedores.recargar();
          }}
        />
      )}
    </>
  );
}
