import { Alert, Box, Button, Group, Modal, Stack, Text, Textarea } from "@mantine/core";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { Dinero } from "../../componentes/Dinero";
import { EntradaDinero } from "../../componentes/EntradaDinero";
import type { CajaActual } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { aCentavos, desdeCentavos, textoDecimal } from "../../utilidades/decimal";
import { formatearHora, formatearPrecio } from "../../utilidades/formato";
import clases from "./caja.module.css";

interface Props {
  abierto: boolean;
  caja: CajaActual;
  nombreSucursal: string;
  alCerrar: () => void;
  alCerrarCaja: () => void;
}

// Cierre de caja: muestra cuánto efectivo debería haber y la diferencia con lo contado antes de confirmar.
export function ModalCerrarCaja({ abierto, caja, nombreSucursal, alCerrar, alCerrarCaja }: Props) {
  const [contado, setContado] = useState<string | number>("");
  const [observacion, setObservacion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  // Diferencia = contado − esperado, en centavos enteros (el backend guarda la oficial)
  const contadoTexto = textoDecimal(contado, 2);
  const diferencia =
    contadoTexto === null ? null : aCentavos(contadoTexto) - aCentavos(caja.efectivo_esperado_actual);
  const signo = diferencia === null ? null : diferencia === 0 ? "cero" : diferencia > 0 ? "sobra" : "falta";

  async function cerrar() {
    if (contadoTexto === null) {
      setError("Contá el efectivo del cajón e ingresá el total.");
      return;
    }
    setEnviando(true);
    setError(null);
    try {
      const cerrada = await api.cerrarCaja(caja.id, contadoTexto, observacion.trim() || null);
      const sinDiferencia = aCentavos(cerrada.diferencia ?? "0") === 0;
      avisarExito(
        "Caja cerrada",
        sinDiferencia
          ? `${nombreSucursal}: sin diferencia.`
          : `${nombreSucursal}: diferencia de ${formatearPrecio(cerrada.diferencia ?? "0")}.`,
      );
      setContado("");
      setObservacion("");
      alCerrarCaja();
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
          Cerrar la caja de {nombreSucursal}
        </Text>
      }
    >
      <Stack gap="md">
        <Box>
          <Text size="sm" c="var(--pl-tenue)">
            Abierta a las {formatearHora(caja.abierta_en)} por {caja.abierta_por}, con {caja.cantidad_ventas}{" "}
            {caja.cantidad_ventas === 1 ? "venta" : "ventas"}.
          </Text>
          <div className={clases.renglon}>
            <Text>Fondo inicial</Text>
            <Dinero valor={caja.fondo_inicial} />
          </div>
          <div className={clases.renglon}>
            <Text>Ventas en efectivo</Text>
            <Dinero valor={caja.ventas_efectivo} />
          </div>
          <div className={clases.renglon}>
            <Text fw={700}>Tiene que haber en el cajón</Text>
            <Dinero valor={caja.efectivo_esperado_actual} cifra fz="xl" />
          </div>
          <div className={clases.renglon}>
            <Text c="var(--pl-tenue)">Transferencias (no están en el cajón)</Text>
            <Dinero valor={caja.ventas_transferencia} c="var(--pl-tenue)" />
          </div>
        </Box>

        <EntradaDinero
          label="Efectivo contado"
          description="Contá los billetes y monedas del cajón, incluido el fondo."
          value={contado}
          onChange={setContado}
          size="lg"
          data-autofocus
        />

        {diferencia !== null && (
          <Group className={clases.diferencia} data-signo={signo} justify="space-between" aria-live="polite">
            <Text fw={700}>
              {signo === "cero" ? "Sin diferencia" : signo === "sobra" ? "Sobra efectivo" : "Falta efectivo"}
            </Text>
            <Dinero valor={desdeCentavos(diferencia)} cifra fz="xl" />
          </Group>
        )}

        <Textarea
          label="Observación"
          description={diferencia ? "Si hay diferencia, anotá qué pudo haber pasado." : "Opcional"}
          value={observacion}
          onChange={(evento) => setObservacion(evento.currentTarget.value)}
          maxLength={200}
          autosize
          minRows={2}
        />
        {error && <Alert color="red">{error}</Alert>}
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={alCerrar}>
            Volver
          </Button>
          <Button color="red" loading={enviando} onClick={cerrar}>
            Cerrar caja
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
