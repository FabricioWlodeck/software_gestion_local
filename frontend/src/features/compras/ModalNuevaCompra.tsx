import { Alert, Button, Divider, Group, Modal, Select, SimpleGrid, Stack, Text, TextInput } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconPlus } from "@tabler/icons-react";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { SelectSucursal } from "../../componentes/SelectSucursal";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import type { CompraNueva } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { aCentavos, aMilesimas, desdeCentavos, subtotalEnCentavos, textoDecimal } from "../../utilidades/decimal";
import { formatearPrecio } from "../../utilidades/formato";
import { LineaCompra, type Linea } from "./LineaCompra";

interface Props {
  alCerrar: () => void;
  alGuardar: () => void;
}

let proximaClave = 1;
const lineaVacia = (): Linea => ({ clave: proximaClave++, productoId: null, cantidad: "", costo: "" });

// Registrar una compra a un proveedor (solo la dueña): suma stock y actualiza costos y precios con margen.
export function ModalNuevaCompra({ alCerrar, alGuardar }: Props) {
  const { sucursalId: sucursalActiva } = useSucursalActiva();
  const pantallaChica = useMediaQuery("(max-width: 48em)");
  const productos = usePedido("productos-compra", () => api.listarProductos());
  const proveedores = usePedido("proveedores-compra", () => api.listarProveedores());

  const [proveedorId, setProveedorId] = useState<number | null>(null);
  const [sucursalId, setSucursalId] = useState<number | null>(sucursalActiva);
  const [comprobante, setComprobante] = useState("");
  const [lineas, setLineas] = useState<Linea[]>(() => [lineaVacia()]);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const listaProductos = productos.datos ?? [];

  // Cantidad y costo en el formato de la API, o null si todavía no son válidos
  function datosDe(linea: Linea) {
    const producto = listaProductos.find((p) => p.id === linea.productoId);
    if (!producto) return null;
    const cantidad = textoDecimal(linea.cantidad, producto.unidad === "kg" ? 3 : 0);
    const costo = textoDecimal(linea.costo, 2);
    if (cantidad === null || costo === null || aMilesimas(cantidad) <= 0) return null;
    return { producto, cantidad, costo };
  }

  const subtotales = lineas.map((linea) => {
    const datos = datosDe(linea);
    return datos ? subtotalEnCentavos(datos.costo, datos.cantidad) : null;
  });
  const total = subtotales.reduce<number>((suma, subtotal) => suma + (subtotal ?? 0), 0);

  function cambiar(clave: number, cambios: Partial<Linea>) {
    setLineas((actuales) => actuales.map((linea) => (linea.clave === clave ? { ...linea, ...cambios } : linea)));
  }

  async function guardar() {
    if (proveedorId === null || sucursalId === null) return setError("Elegí el proveedor y la sucursal que recibe la mercadería.");
    const items: CompraNueva["items"] = [];
    const vistos = new Set<number>();
    for (const linea of lineas) {
      const datos = datosDe(linea);
      if (datos === null) return setError("Completá producto, cantidad y costo en todas las líneas (o quitá las vacías).");
      if (vistos.has(datos.producto.id)) return setError(`${datos.producto.nombre} está dos veces: dejalo en una sola línea.`);
      vistos.add(datos.producto.id);
      items.push({ producto_id: datos.producto.id, cantidad: datos.cantidad, costo_unitario: datos.costo });
    }

    setEnviando(true);
    setError(null);
    const preciosAntes = new Map(listaProductos.map((p) => [p.id, p.precio]));
    try {
      const compra = await api.registrarCompra({
        proveedor_id: proveedorId,
        sucursal_id: sucursalId,
        comprobante: comprobante.trim() || null,
        items,
      });
      avisarExito(`Compra ${compra.id} registrada`, `${formatearPrecio(compra.total)} a ${compra.proveedor}. El stock ya se actualizó.`);

      // Los productos con margen recalculan el precio con el costo nuevo: se avisa cuáles cambiaron
      const despues = await api.listarProductos().catch(() => []);
      const cambios = despues
        .filter((p) => vistos.has(p.id) && preciosAntes.has(p.id) && aCentavos(preciosAntes.get(p.id) ?? "0") !== aCentavos(p.precio))
        .map((p) => `${p.nombre}: ${formatearPrecio(preciosAntes.get(p.id) ?? "0")} → ${formatearPrecio(p.precio)}`);
      if (cambios.length > 0) {
        notifications.show({ title: "Precios actualizados por el margen", message: cambios.join(". "), color: "queso", autoClose: 12000 });
      }
      alGuardar();
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
      size="xl"
      fullScreen={pantallaChica}
      title={
        <Text fw={700} size="lg">
          Nueva compra
        </Text>
      }
    >
      <Stack gap="md">
        <SimpleGrid cols={{ base: 1, sm: 3 }}>
          <Select
            label="Proveedor"
            placeholder={proveedores.cargando ? "Cargando…" : "Elegí el proveedor"}
            searchable
            data={(proveedores.datos ?? []).map((p) => ({ value: String(p.id), label: p.nombre }))}
            value={proveedorId === null ? null : String(proveedorId)}
            onChange={(valor) => setProveedorId(valor ? Number(valor) : null)}
            nothingFoundMessage="No hay proveedores con ese nombre"
            error={proveedores.error}
          />
          <SelectSucursal label="Recibe" valor={sucursalId} alCambiar={setSucursalId} />
          <TextInput
            label="Comprobante"
            placeholder="Remito o factura"
            maxLength={40}
            value={comprobante}
            onChange={(evento) => setComprobante(evento.currentTarget.value)}
          />
        </SimpleGrid>

        <Divider label="Mercadería" labelPosition="left" />
        {productos.error && <Alert color="red">{productos.error}</Alert>}
        <Stack gap="sm">
          {lineas.map((linea, indice) => (
            <LineaCompra
              key={linea.clave}
              linea={linea}
              productos={listaProductos}
              subtotalCentavos={subtotales[indice]}
              puedeQuitar={lineas.length > 1}
              alCambiar={(cambios) => cambiar(linea.clave, cambios)}
              alQuitar={() => setLineas((actuales) => actuales.filter((l) => l.clave !== linea.clave))}
            />
          ))}
        </Stack>
        <Group justify="space-between">
          <Button variant="default" leftSection={<IconPlus size={18} />} onClick={() => setLineas((actuales) => [...actuales, lineaVacia()])}>
            Agregar producto
          </Button>
          <Group gap="sm" align="baseline">
            <Text fw={600}>Total</Text>
            <Text className="pl-cifra" fz={32}>
              {formatearPrecio(desdeCentavos(total))}
            </Text>
          </Group>
        </Group>

        {error && <Alert color="red">{error}</Alert>}
        <Group justify="flex-end" gap="xs">
          <Button variant="default" onClick={alCerrar}>
            Volver
          </Button>
          <Button loading={enviando} onClick={guardar}>
            Registrar compra
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
