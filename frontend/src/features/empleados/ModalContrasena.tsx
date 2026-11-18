import { Alert, Button, Group, Modal, PasswordInput, Stack, Text } from "@mantine/core";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import type { Usuario } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";

interface Props {
  empleado: Usuario;
  alCerrar: () => void;
}

// La dueña le asigna una contraseña nueva a un usuario (por ejemplo, si se la olvidó).
export function ModalContrasena({ empleado, alCerrar }: Props) {
  const [contrasena, setContrasena] = useState("");
  const [repetida, setRepetida] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function guardar() {
    if (contrasena.length < 6) return setError("Tiene que tener al menos 6 caracteres.");
    if (contrasena !== repetida) return setError("Las dos contraseñas no coinciden.");
    setEnviando(true);
    setError(null);
    try {
      await api.cambiarContrasena(empleado.id, contrasena);
      avisarExito("Contraseña cambiada", `Avisale a ${empleado.nombre} la contraseña nueva.`);
      alCerrar();
    } catch (problema) {
      setError(mensajeDe(problema));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal
      opened
      onClose={alCerrar}
      title={
        <Text fw={700} size="lg">
          Nueva contraseña para {empleado.nombre}
        </Text>
      }
    >
      <Stack gap="md">
        <PasswordInput
          label="Contraseña nueva"
          size="md"
          autoComplete="new-password"
          value={contrasena}
          onChange={(evento) => setContrasena(evento.currentTarget.value)}
          data-autofocus
        />
        <PasswordInput
          label="Repetila"
          size="md"
          autoComplete="new-password"
          value={repetida}
          onChange={(evento) => setRepetida(evento.currentTarget.value)}
        />
        {error && <Alert color="red">{error}</Alert>}
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={alCerrar}>
            Volver
          </Button>
          <Button loading={enviando} onClick={guardar}>
            Cambiar contraseña
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
