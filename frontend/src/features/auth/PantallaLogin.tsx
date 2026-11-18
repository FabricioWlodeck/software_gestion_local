import { Alert, Box, Button, Center, Image, Paper, PasswordInput, Stack, Text, TextInput, Title } from "@mantine/core";
import { IconAlertTriangle } from "@tabler/icons-react";
import { useState, type FormEvent } from "react";
import { Navigate, useLocation } from "react-router";
import { mensajeDe } from "../../api/cliente";
import { useSesion } from "./sesion";

// Formulario de inicio de sesión. Si sale bien, vuelve a la pantalla que se quería abrir.
export function PantallaLogin() {
  const { usuario, iniciarSesion } = useSesion();
  const ubicacion = useLocation();
  const [nombre, setNombre] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (usuario !== null) {
    const desde = (ubicacion.state as { desde?: string } | null)?.desde ?? "/";
    return <Navigate to={desde} replace />;
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault(); // evita que el navegador recargue la página
    setEnviando(true);
    setError(null);
    try {
      await iniciarSesion(nombre.trim(), contrasena);
    } catch (problema) {
      setError(mensajeDe(problema));
      setEnviando(false);
    }
  }

  return (
    <Center mih="100dvh" p="md">
      <Paper
        component="form"
        onSubmit={enviar}
        w="100%"
        maw={380}
        p="xl"
        withBorder
        style={{ borderTop: "6px solid var(--mantine-color-queso-5)" }}
      >
        <Stack gap="md">
          <Image src="/logo.png" alt="Punto Lácteo" w={132} h={132} mx="auto" />
          <Box>
            <Title order={2}>Ingresá a la caja</Title>
            <Text c="var(--pl-tenue)">Usá el usuario y la contraseña que te dio la dueña.</Text>
          </Box>
          <TextInput
            label="Usuario"
            value={nombre}
            onChange={(evento) => setNombre(evento.currentTarget.value)}
            autoComplete="username"
            autoCapitalize="none"
            autoFocus
            required
          />
          <PasswordInput
            label="Contraseña"
            size="md"
            value={contrasena}
            onChange={(evento) => setContrasena(evento.currentTarget.value)}
            autoComplete="current-password"
            required
          />
          {error && (
            <Alert color="red" icon={<IconAlertTriangle size={20} />} role="alert">
              {error}
            </Alert>
          )}
          <Button type="submit" size="lg" loading={enviando} fullWidth>
            Ingresar
          </Button>
          <Text size="sm" c="var(--pl-tenue)">
            ¿Te olvidaste la contraseña? Pedile a la dueña que te asigne una nueva.
          </Text>
        </Stack>
      </Paper>
    </Center>
  );
}
