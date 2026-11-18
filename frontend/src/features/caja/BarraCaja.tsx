import { Box, Button, Group, Skeleton, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconLock, IconLockOpen } from "@tabler/icons-react";
import { Dinero } from "../../componentes/Dinero";
import type { CajaActual } from "../../tipos";
import { formatearHora } from "../../utilidades/formato";
import clases from "./caja.module.css";
import { ModalAbrirCaja } from "./ModalAbrirCaja";
import { ModalCerrarCaja } from "./ModalCerrarCaja";

interface Props {
  caja: CajaActual | null;
  cargando: boolean;
  sucursalId: number;
  nombreSucursal: string;
  alCambiar: () => void; // recarga la caja (y lo que dependa de ella)
}

// Estado de la caja de hoy en la sucursal activa, con los botones para abrirla o cerrarla.
export function BarraCaja({ caja, cargando, sucursalId, nombreSucursal, alCambiar }: Props) {
  const [abriendo, abrir] = useDisclosure(false);
  const [cerrando, cerrar] = useDisclosure(false);

  if (caja === null && cargando) {
    return <Skeleton h={58} radius="sm" />;
  }

  if (caja === null) {
    return (
      <Group className={clases.barra} data-estado="cerrada" justify="space-between" gap="sm">
        <Group gap="sm" wrap="nowrap">
          <IconLock size={24} aria-hidden />
          <Box className={clases.dato}>
            <Text fw={700}>La caja de {nombreSucursal} está cerrada</Text>
            <Text size="sm">Abrila para empezar a cobrar.</Text>
          </Box>
        </Group>
        <Button color="orange" onClick={abrir.open}>
          Abrir caja
        </Button>
        <ModalAbrirCaja
          abierto={abriendo}
          sucursalId={sucursalId}
          nombreSucursal={nombreSucursal}
          alCerrar={abrir.close}
          alAbrir={() => {
            abrir.close();
            alCambiar();
          }}
        />
      </Group>
    );
  }

  return (
    <Group className={clases.barra} data-estado="abierta" justify="space-between" gap="sm">
      <Group gap="lg" wrap="wrap" style={{ rowGap: 4 }}>
        <Group gap="sm" wrap="nowrap">
          <IconLockOpen size={24} color="var(--mantine-color-frasco-7)" aria-hidden />
          <Box className={clases.dato}>
            <Text fw={700}>Caja abierta</Text>
            <Text size="sm" c="var(--pl-tenue)">
              desde las {formatearHora(caja.abierta_en)}, {caja.abierta_por}
            </Text>
          </Box>
        </Group>
        <Box className={clases.dato}>
          <Text size="sm" c="var(--pl-tenue)">
            Efectivo esperado
          </Text>
          <Dinero valor={caja.efectivo_esperado_actual} fw={700} />
        </Box>
        <Box className={clases.dato}>
          <Text size="sm" c="var(--pl-tenue)">
            Ventas
          </Text>
          <Text fw={700} className="pl-numero">
            {caja.cantidad_ventas}
          </Text>
        </Box>
      </Group>
      <Button
        variant="default"
        onClick={() => {
          alCambiar(); // trae el esperado al día antes de contar
          cerrar.open();
        }}
      >
        Cerrar caja
      </Button>
      <ModalCerrarCaja
        abierto={cerrando}
        caja={caja}
        nombreSucursal={nombreSucursal}
        alCerrar={cerrar.close}
        alCerrarCaja={() => {
          cerrar.close();
          alCambiar();
        }}
      />
    </Group>
  );
}
