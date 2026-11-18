import { Alert, Button, Group, Modal, Select, SimpleGrid, Stack, Text, Textarea } from "@mantine/core";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { EntradaCantidad } from "../../componentes/EntradaCantidad";
import { SelectSucursal } from "../../componentes/SelectSucursal";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import { avisarExito } from "../../utilidades/avisos";
import { aMilesimas, textoDecimal } from "../../utilidades/decimal";
import { formatearCantidad } from "../../utilidades/formato";

interface Props {
  productoInicial: number | null;
  origenInicial: number;
  alCerrar: () => void;
  alGuardar: () => void;
}

// Traspaso entre sucursales (solo la dueña): sale del origen y entra en el destino en un solo paso.
export function ModalTraspaso({ productoInicial, origenInicial, alCerrar, alGuardar }: Props) {
  const { sucursales, nombreDe } = useSucursalActiva();
  // GET /productos (versión dueña) trae el stock de cada sucursal
  const productos = usePedido("productos-activos", () => api.listarProductos());

  const [productoId, setProductoId] = useState<number | null>(productoInicial);
  const [origen, setOrigen] = useState<number | null>(origenInicial);
  const [destino, setDestino] = useState<number | null>(
    sucursales.find((s) => s.activa && s.id !== origenInicial)?.id ?? null,
  );
  const [cantidad, setCantidad] = useState<string | number>("");
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const producto = productos.datos?.find((p) => p.id === productoId) ?? null;
  const enOrigen = producto?.stock.find((s) => s.sucursal_id === origen)?.cantidad ?? null;
  const cantidadTexto = producto ? textoDecimal(cantidad, producto.unidad === "kg" ? 3 : 0) : null;

  async function guardar() {
    if (producto === null || origen === null || destino === null) return setError("Elegí el producto, el origen y el destino.");
    if (origen === destino) return setError("El origen y el destino tienen que ser sucursales distintas.");
    if (cantidadTexto === null || aMilesimas(cantidadTexto) <= 0) return setError("Ingresá una cantidad mayor que cero.");
    if (enOrigen !== null && aMilesimas(cantidadTexto) > aMilesimas(enOrigen))
      return setError(`En ${nombreDe(origen)} hay ${formatearCantidad(enOrigen, producto.unidad)}.`);

    setEnviando(true);
    setError(null);
    try {
      await api.registrarTraspaso({
        producto_id: producto.id,
        origen_id: origen,
        destino_id: destino,
        cantidad: cantidadTexto,
        motivo: motivo.trim() || null,
      });
      avisarExito(
        "Traspaso registrado",
        `${formatearCantidad(cantidadTexto, producto.unidad)} de ${producto.nombre}: ${nombreDe(origen)} a ${nombreDe(destino)}.`,
      );
      alGuardar();
    } catch (problema) {
      setError(mensajeDe(problema));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal opened onClose={alCerrar} title={<Text fw={700} size="lg">Traspasar entre sucursales</Text>}>
      <Stack gap="md">
        <Select
          label="Producto"
          placeholder={productos.cargando ? "Cargando productos…" : "Buscá el producto"}
          searchable
          data={(productos.datos ?? []).map((p) => ({ value: String(p.id), label: p.nombre }))}
          value={productoId === null ? null : String(productoId)}
          onChange={(valor) => setProductoId(valor ? Number(valor) : null)}
          nothingFoundMessage="No hay productos con ese nombre"
          error={productos.error}
        />
        <SimpleGrid cols={{ base: 1, xs: 2 }}>
          <SelectSucursal label="Sale de" valor={origen} alCambiar={setOrigen} />
          <SelectSucursal label="Entra en" valor={destino} alCambiar={setDestino} excluir={origen} />
        </SimpleGrid>
        {producto && (
          <EntradaCantidad
            unidad={producto.unidad}
            label="Cantidad"
            description={enOrigen !== null ? `En ${nombreDe(origen)} hay ${formatearCantidad(enOrigen, producto.unidad)}.` : undefined}
            value={cantidad}
            onChange={setCantidad}
          />
        )}
        <Textarea
          label="Motivo"
          description="Opcional"
          value={motivo}
          onChange={(evento) => setMotivo(evento.currentTarget.value)}
          maxLength={200}
          autosize
          minRows={2}
        />
        {error && <Alert color="red">{error}</Alert>}
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={alCerrar}>
            Volver
          </Button>
          <Button loading={enviando} onClick={guardar}>
            Traspasar
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
