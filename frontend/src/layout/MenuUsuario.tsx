import { Avatar, Box, Menu, Text, UnstyledButton, useMantineColorScheme } from "@mantine/core";
import { IconLogout, IconMoon, IconSun } from "@tabler/icons-react";
import { useUsuario, useSesion } from "../features/auth/sesion";

// Nombre y rol de quien está usando la caja, con el modo oscuro y la salida.
export function MenuUsuario() {
  const usuario = useUsuario();
  const { cerrarSesion } = useSesion();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const rol = usuario.rol === "duenio" ? "Dueña" : "Empleado";
  const iniciales = usuario.nombre
    .split(" ")
    .map((parte) => parte[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <Menu position="bottom-end" width={220} withinPortal>
      <Menu.Target>
        <UnstyledButton aria-label={`${usuario.nombre}, ${rol}. Abrir menú`}>
          <Box style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Avatar color="frasco" radius="xl" size={38}>
              {iniciales}
            </Avatar>
            <Box visibleFrom="sm" style={{ lineHeight: 1.15 }}>
              <Text fw={600} size="md">
                {usuario.nombre}
              </Text>
              <Text size="sm" c="var(--pl-tenue)">
                {rol}
              </Text>
            </Box>
          </Box>
        </UnstyledButton>
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Label hiddenFrom="sm">
          {usuario.nombre} ({rol})
        </Menu.Label>
        <Menu.Item
          leftSection={colorScheme === "dark" ? <IconSun size={18} /> : <IconMoon size={18} />}
          onClick={toggleColorScheme}
        >
          {colorScheme === "dark" ? "Modo claro" : "Modo oscuro"}
        </Menu.Item>
        <Menu.Divider />
        <Menu.Item color="red" leftSection={<IconLogout size={18} />} onClick={cerrarSesion}>
          Cerrar sesión
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
}
