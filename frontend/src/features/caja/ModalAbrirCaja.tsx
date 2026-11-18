import { Alert, Button, Group, Modal, Stack, Text } from "@mantine/core";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { EntradaDinero } from "../../componentes/EntradaDinero";
import { avisarExito } from "../../utilidades/avisos";
import { textoDecimal } from "../../utilidades/decimal";
import { formatearPrecio } from "../../utilidades/formato";

interface Props {
  abierto: boolean;
  sucursalId: number;
  nombreSucursal: string;
  alCerrar: () => void;
  alAbrir: () => void;
}

// Abrir la caja del día: se cuenta el efectivo que queda en el cajón para dar vuelto.
export function ModalAbrirCaja({ abierto, sucursalId, nombreSucursal, alCerrar, alAbrir }: Props) {
  const [fondo, setFondo] = useState<string | number>("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function abrir() {
    const fondoInicial = textoDecimal(fondo, 2);
    if (fondoInicial === null) {
      setError("Ingresá el efectivo con el que arranca la caja (puede ser 0).");
      return;
    }
    setEnviando(true);
    setError(null);
    try {
      const caja = await api.abrirCaja(sucursalId, fondoInicial);
      avisarExito("Caja abierta", `${nombreSucursal}, con ${formatearPrecio(caja.fondo_inicial)} de fondo.`);
      setFondo("");
      alAbrir();
    } catch (problema) {
      setError(mensajeDe(problema));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal
      opened={abierto}
      onClose={alCerrar}
      title={
        <Text fw={700} size="lg">
          Abrir la caja de {nombreSucursal}
        </Text>
      }
    >
      <Stack gap="md">
        <EntradaDinero
          label="Fondo inicial"
          description="El efectivo que hay en el cajón antes de la primera venta."
          value={fondo}
          onChange={setFondo}
          data-autofocus
          onKeyDown={(evento) => {
            if (evento.key === "Enter") abrir();
          }}
        />
        {error && <Alert color="red">{error}</Alert>}
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={alCerrar}>
            Volver
          </Button>
          <Button loading={enviando} onClick={abrir}>
            Abrir caja
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
