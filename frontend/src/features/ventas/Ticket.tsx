import { Alert, Box, Button, Group, Kbd, SegmentedControl, Stack, Text, Title } from "@mantine/core";
import { IconAlertTriangle, IconBuildingBank, IconCash } from "@tabler/icons-react";
import { useState } from "react";
import { EntradaDinero } from "../../componentes/EntradaDinero";
import type { ItemCarrito, MedioPago, Venta } from "../../tipos";
import { aCentavos, desdeCentavos, textoDecimal } from "../../utilidades/decimal";
import { formatearPrecio } from "../../utilidades/formato";
import { LineaTicket } from "./LineaTicket";
import clases from "./venta.module.css";

interface Props {
  items: ItemCarrito[];
  totalCentavos: number;
  medioPago: MedioPago;
  cobrando: boolean;
  bloqueo: string | null; // por qué no se puede cobrar (caja cerrada, sin sucursal…)
  error: string | null; // lo que respondió el backend al intentar cobrar
  ultimaVenta: Venta | null;
  alCambiarMedio: (medio: MedioPago) => void;
  alEditar: (item: ItemCarrito) => void;
  alQuitar: (productoId: number) => void;
  alVaciar: () => void;
  alCobrar: () => void;
}

// El ticket de la venta en curso: renglones, medio de pago, total y el botón de cobrar.
export function Ticket(props: Props) {
  const { items, totalCentavos, medioPago, cobrando, bloqueo, error, ultimaVenta } = props;
  const [pagaCon, setPagaCon] = useState<string | number>("");

  const vacio = items.length === 0;
  const pagaConTexto = textoDecimal(pagaCon, 2);
  const vuelto = pagaConTexto === null ? null : aCentavos(pagaConTexto) - totalCentavos;

  return (
    <Box className={clases.ticket} id="ticket" component="section" aria-label="Ticket de la venta">
      <Stack gap="sm">
        <Group justify="space-between" align="baseline">
          <Title order={3}>Ticket</Title>
          {!vacio && (
            <Button variant="subtle" color="gray" size="xs" onClick={props.alVaciar}>
              Vaciar
            </Button>
          )}
        </Group>

        {vacio ? (
          <Text c="var(--pl-tenue)" py="md">
            Todavía no hay productos. Elegí uno a la izquierda para empezar.
          </Text>
        ) : (
          <div>
            {items.map((item) => (
              <LineaTicket key={item.producto.id} item={item} alEditar={props.alEditar} alQuitar={props.alQuitar} />
            ))}
          </div>
        )}

        <SegmentedControl
          fullWidth
          value={medioPago}
          onChange={(valor) => props.alCambiarMedio(valor as MedioPago)}
          aria-label="Medio de pago"
          data={[
            {
              value: "efectivo",
              label: (
                <Group gap={6} justify="center" wrap="nowrap">
                  <IconCash size={20} aria-hidden /> Efectivo
                </Group>
              ),
            },
            {
              value: "transferencia",
              label: (
                <Group gap={6} justify="center" wrap="nowrap">
                  <IconBuildingBank size={20} aria-hidden /> Transferencia
                </Group>
              ),
            },
          ]}
        />

        <div className={clases.total}>
          <Text fw={700} size="lg">
            Total
          </Text>
          <span className={clases.totalCifra} aria-live="polite">
            {formatearPrecio(desdeCentavos(totalCentavos))}
          </span>
        </div>

        {medioPago === "efectivo" && !vacio && (
          <Group gap="sm" align="flex-end" wrap="nowrap">
            <EntradaDinero label="Paga con" size="md" value={pagaCon} onChange={setPagaCon} style={{ flex: 1 }} />
            <Box ta="right" miw={120}>
              <Text size="sm" c="var(--pl-tenue)">
                Vuelto
              </Text>
              <Text fw={700} size="xl" className="pl-numero" c={vuelto !== null && vuelto < 0 ? "red" : undefined}>
                {vuelto === null ? "—" : vuelto < 0 ? "Falta plata" : formatearPrecio(desdeCentavos(vuelto))}
              </Text>
            </Box>
          </Group>
        )}

        {error && (
          <Alert color="red" icon={<IconAlertTriangle size={20} />} title="No se cobró">
            {error}
          </Alert>
        )}
        {bloqueo && (
          <Text c="var(--pl-alerta)" fw={600}>
            {bloqueo}
          </Text>
        )}

        <Button
          className={clases.cobrar}
          fullWidth
          disabled={vacio || bloqueo !== null}
          loading={cobrando}
          onClick={props.alCobrar}
          rightSection={
            <Kbd size="sm" visibleFrom="sm">
              F9
            </Kbd>
          }
        >
          Cobrar
        </Button>

        {ultimaVenta && (
          <Text size="sm" c="var(--pl-tenue)">
            Última venta: N.º {ultimaVenta.id}, {formatearPrecio(ultimaVenta.total)} en {ultimaVenta.medio_pago}.
          </Text>
        )}
      </Stack>
    </Box>
  );
}
