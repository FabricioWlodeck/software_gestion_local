import { AppShell, Burger, Center, Group, Image, Loader, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Suspense } from "react";
import { Link, Outlet } from "react-router";
import { SelectorSucursal } from "../componentes/SelectorSucursal";
import { SucursalActivaProvider } from "../hooks/SucursalActivaProvider";
import clases from "./Marco.module.css";
import { MenuNavegacion } from "./MenuNavegacion";
import { MenuUsuario } from "./MenuUsuario";

// Estructura de todas las pantallas con sesión: encabezado, menú lateral y contenido.
export function Marco() {
  const [menuAbierto, { toggle, close }] = useDisclosure(false);

  return (
    <SucursalActivaProvider>
      <AppShell
        header={{ height: 68 }}
        navbar={{ width: 240, breakpoint: "sm", collapsed: { mobile: !menuAbierto } }}
        padding={{ base: "sm", sm: "lg" }}
      >
        <AppShell.Header className={clases.encabezado}>
          <Group h="100%" px={{ base: "xs", sm: "md" }} justify="space-between" wrap="nowrap" gap="xs">
            <Group gap="xs" wrap="nowrap">
              <Burger opened={menuAbierto} onClick={toggle} hiddenFrom="sm" size="sm" aria-label="Abrir el menú" />
              <Link to="/" aria-label="Punto Lácteo, ir a vender" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none" }}>
                <Image src="/logo.png" alt="" w={44} h={44} />
                <Text component="span" className={clases.marca} visibleFrom="xs">
                  Punto Lácteo
                </Text>
              </Link>
            </Group>
            <Group gap="sm" wrap="nowrap">
              <SelectorSucursal />
              <MenuUsuario />
            </Group>
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="sm" className={clases.navegacion}>
          <MenuNavegacion alNavegar={close} />
        </AppShell.Navbar>

        <AppShell.Main className={clases.principal}>
          {/* Suspense: muestra un indicador mientras se descarga una pantalla de la dueña */}
          <Suspense
            fallback={
              <Center py="xl">
                <Loader aria-label="Cargando la pantalla" />
              </Center>
            }
          >
            <Outlet />
          </Suspense>
        </AppShell.Main>
      </AppShell>
    </SucursalActivaProvider>
  );
}
