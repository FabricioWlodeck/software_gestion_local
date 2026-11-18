import { Badge, Button, Group, Menu, ActionIcon, Paper, Stack, Table, Text } from "@mantine/core";
import { IconBrandTelegram, IconDots, IconKey, IconPencil, IconPlus, IconUsers } from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import type { Usuario } from "../../tipos";
import { useUsuario } from "../auth/sesion";
import { ModalContrasena } from "./ModalContrasena";
import { ModalEmpleado } from "./ModalEmpleado";
import { SeccionSucursales } from "./SeccionSucursales";

// Usuarios del sistema (solo la dueña): alta, rol, sucursal, activo, contraseña y Telegram.
export function PantallaEmpleados() {
  const yo = useUsuario();
  const { nombreDe } = useSucursalActiva();
  const usuarios = usePedido("usuarios", api.listarUsuarios);
  const [editando, setEditando] = useState<Usuario | null | undefined>(undefined);
  const [cambiandoClave, setCambiandoClave] = useState<Usuario | null>(null);

  // Primero los activos; dentro de cada grupo, por nombre
  const lista = [...(usuarios.datos ?? [])].sort(
    (a, b) => Number(b.activo) - Number(a.activo) || a.nombre.localeCompare(b.nombre, "es"),
  );

  return (
    <Stack gap="lg">
      <div>
        <EncabezadoPagina
          titulo="Empleados"
          detalle="Quién puede ingresar y en qué sucursal trabaja"
          acciones={
            <Button leftSection={<IconPlus size={18} />} onClick={() => setEditando(null)}>
              Nuevo usuario
            </Button>
          }
        />

        {usuarios.error && <ErrorCarga mensaje={usuarios.error} alReintentar={usuarios.recargar} />}

        <Paper withBorder radius="sm">
          {lista.length === 0 && !usuarios.cargando ? (
            <PaginaVacia icono={<IconUsers size={28} />} titulo="No hay usuarios para mostrar" />
          ) : (
            <Table.ScrollContainer minWidth={680}>
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Nombre</Table.Th>
                    <Table.Th>Usuario</Table.Th>
                    <Table.Th>Rol</Table.Th>
                    <Table.Th>Sucursal</Table.Th>
                    <Table.Th>Avisos</Table.Th>
                    <Table.Th w={52} />
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {lista.map((usuario) => (
                    <Table.Tr key={usuario.id} style={{ opacity: usuario.activo ? 1 : 0.6 }}>
                      <Table.Td>
                        <Group gap={6}>
                          <Text fw={600}>{usuario.nombre}</Text>
                          {usuario.id === yo.id && (
                            <Badge size="sm" color="queso" variant="filled" c="dark.9">
                              Vos
                            </Badge>
                          )}
                          {!usuario.activo && (
                            <Badge size="sm" color="gray">
                              Inactivo
                            </Badge>
                          )}
                        </Group>
                      </Table.Td>
                      <Table.Td>{usuario.nombre_usuario}</Table.Td>
                      <Table.Td>{usuario.rol === "duenio" ? "Dueña" : "Empleado"}</Table.Td>
                      <Table.Td>{usuario.rol === "duenio" ? "Todas" : nombreDe(usuario.sucursal_id)}</Table.Td>
                      <Table.Td>
                        {usuario.telegram_id ? (
                          <Group gap={4} wrap="nowrap">
                            <IconBrandTelegram size={18} color="var(--mantine-color-blue-6)" aria-hidden />
                            <Text size="sm">Telegram</Text>
                          </Group>
                        ) : (
                          <Text size="sm" c="var(--pl-tenue)">
                            Sin Telegram
                          </Text>
                        )}
                      </Table.Td>
                      <Table.Td>
                        <Menu position="bottom-end" withinPortal>
                          <Menu.Target>
                            <ActionIcon color="gray" aria-label={`Acciones de ${usuario.nombre}`}>
                              <IconDots size={20} />
                            </ActionIcon>
                          </Menu.Target>
                          <Menu.Dropdown>
                            <Menu.Item leftSection={<IconPencil size={16} />} onClick={() => setEditando(usuario)}>
                              Editar
                            </Menu.Item>
                            <Menu.Item leftSection={<IconKey size={16} />} onClick={() => setCambiandoClave(usuario)}>
                              Cambiar contraseña
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
      </div>

      <SeccionSucursales />

      {editando !== undefined && (
        <ModalEmpleado
          empleado={editando}
          alCerrar={() => setEditando(undefined)}
          alGuardar={() => {
            setEditando(undefined);
            usuarios.recargar();
          }}
        />
      )}
      {cambiandoClave && <ModalContrasena empleado={cambiandoClave} alCerrar={() => setCambiandoClave(null)} />}
    </Stack>
  );
}
