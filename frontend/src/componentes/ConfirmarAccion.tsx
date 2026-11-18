import { Alert, Button, Group, Modal, Stack, Text, Textarea } from "@mantine/core";
import { useState, type ReactNode } from "react";
import { mensajeDe } from "../api/cliente";

interface Props {
  abierto: boolean;
  titulo: string;
  descripcion?: ReactNode;
  motivo?: "obligatorio" | "opcional" | "sin motivo";
  etiquetaMotivo?: string;
  textoConfirmar: string;
  color?: string;
  alCerrar: () => void;
  alConfirmar: (motivo: string | null) => Promise<void>;
}

// Modal para confirmar una acción que importa (observar, anular…), con un motivo si hace falta.
// Si el backend rechaza la acción, el mensaje queda en el modal y se puede corregir.
export function ConfirmarAccion({
  abierto,
  titulo,
  descripcion,
  motivo = "sin motivo",
  etiquetaMotivo = "Motivo",
  textoConfirmar,
  color = "frasco",
  alCerrar,
  alConfirmar,
}: Props) {
  const [texto, setTexto] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  function cerrar() {
    setTexto("");
    setError(null);
    alCerrar();
  }

  async function confirmar() {
    const limpio = texto.trim();
    if (motivo === "obligatorio" && limpio === "") {
      setError("Escribí el motivo para poder seguir.");
      return;
    }
    setEnviando(true);
    setError(null);
    try {
      await alConfirmar(limpio === "" ? null : limpio);
      setTexto("");
      alCerrar();
    } catch (problema) {
      setError(mensajeDe(problema));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal opened={abierto} onClose={cerrar} title={<Text fw={700} size="lg">{titulo}</Text>}>
      <Stack gap="md">
        {descripcion && <Text>{descripcion}</Text>}
        {motivo !== "sin motivo" && (
          <Textarea
            label={etiquetaMotivo}
            description={motivo === "opcional" ? "Opcional" : undefined}
            required={motivo === "obligatorio"}
            value={texto}
            onChange={(evento) => setTexto(evento.currentTarget.value)}
            maxLength={200}
            autosize
            minRows={2}
            data-autofocus
          />
        )}
        {error && <Alert color="red">{error}</Alert>}
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={cerrar}>
            Volver
          </Button>
          <Button color={color} loading={enviando} onClick={confirmar}>
            {textoConfirmar}
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
