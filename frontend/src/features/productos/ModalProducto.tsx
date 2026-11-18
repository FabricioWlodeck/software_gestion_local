import { Alert, Button, Group, Modal, NumberInput, SegmentedControl, SimpleGrid, Stack, Switch, Text, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { EntradaCantidad } from "../../componentes/EntradaCantidad";
import { EntradaDinero } from "../../componentes/EntradaDinero";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import type { DatosProducto, Minimos, ModoPrecio, Producto, Unidad } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { aCentavos, textoDecimal } from "../../utilidades/decimal";
import { formatearPrecio } from "../../utilidades/formato";
import { precioPorMargen } from "./precioCalculado";

type Numero = number | string;

interface Valores {
  nombre: string;
  unidad: Unidad;
  modo_precio: ModoPrecio;
  margen: Numero;
  costo_ultimo: Numero;
  precio: Numero;
  activo: boolean;
  minimos: Record<string, Numero>;
}

interface Props {
  producto: Producto | null; // null = producto nuevo
  alCerrar: () => void;
  alGuardar: () => void;
}

// Alta y edición de productos (solo la dueña): precio manual o calculado con margen sobre el costo.
export function ModalProducto({ producto, alCerrar, alGuardar }: Props) {
  const { sucursales } = useSucursalActiva();
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  // Modo controlado: la vista previa del precio se actualiza mientras se escribe
  const formulario = useForm<Valores>({
    mode: "controlled",
    initialValues: {
      nombre: producto?.nombre ?? "",
      unidad: producto?.unidad ?? "kg",
      modo_precio: producto?.modo_precio ?? "manual",
      margen: producto?.margen ? Number(producto.margen) : "",
      costo_ultimo: producto?.costo_ultimo ? Number(producto.costo_ultimo) : "",
      precio: producto ? Number(producto.precio) : "",
      activo: producto?.activo ?? true,
      minimos: Object.fromEntries(
        sucursales.map((s) => [String(s.id), Number(producto?.stock.find((x) => x.sucursal_id === s.id)?.minimo ?? 0)]),
      ),
    },
    validate: {
      nombre: (valor) => (valor.trim() === "" ? "Escribí el nombre" : null),
      margen: (valor, valores) =>
        valores.modo_precio === "margen" && textoDecimal(valor, 2) === null ? "Ingresá el margen en %" : null,
      precio: (valor, valores) => {
        const costoTexto = textoDecimal(valores.costo_ultimo, 2);
        if (valores.modo_precio === "margen" && costoTexto !== null && aCentavos(costoTexto) > 0) return null;
        const texto = textoDecimal(valor, 2);
        return texto === null || aCentavos(texto) <= 0 ? "Ingresá un precio mayor que cero" : null;
      },
    },
  });

  const valores = formulario.getValues();
  const margen = textoDecimal(valores.margen, 2);
  const costo = textoDecimal(valores.costo_ultimo, 2);
  // Con margen y un costo mayor que cero, el precio lo calcula el backend (si no, se pide el precio)
  const calculado =
    valores.modo_precio === "margen" && margen !== null && costo !== null && aCentavos(costo) > 0
      ? precioPorMargen(costo, margen)
      : null;

  async function guardar(v: Valores) {
    setEnviando(true);
    setError(null);
    const minimos: Minimos = {};
    for (const [id, valor] of Object.entries(v.minimos)) {
      minimos[id] = textoDecimal(valor, 3) ?? "0.000";
    }
    const datos: DatosProducto = {
      nombre: v.nombre.trim(),
      unidad: v.unidad,
      modo_precio: v.modo_precio,
      margen: v.modo_precio === "margen" ? textoDecimal(v.margen, 2) : null,
      costo_ultimo: textoDecimal(v.costo_ultimo, 2),
      // Con margen y costo, el precio lo calcula el backend
      precio: calculado === null ? textoDecimal(v.precio, 2) : null,
    };
    try {
      if (producto === null) {
        const nuevo = await api.crearProducto({ ...datos, minimos });
        avisarExito("Producto creado", `${nuevo.nombre} a ${formatearPrecio(nuevo.precio)}.`);
      } else {
        const { precio, ...resto } = datos;
        const editado = await api.editarProducto(producto.id, {
          ...resto,
          ...(precio === null ? {} : { precio }),
          activo: v.activo,
        });
        await api.guardarMinimos(producto.id, minimos);
        avisarExito("Producto guardado", `${editado.nombre} a ${formatearPrecio(editado.precio)}.`);
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
      size="lg"
      title={
        <Text fw={700} size="lg">
          {producto ? `Editar ${producto.nombre}` : "Nuevo producto"}
        </Text>
      }
    >
      <form onSubmit={formulario.onSubmit(guardar)}>
        <Stack gap="md">
          <TextInput label="Nombre" required maxLength={80} data-autofocus {...formulario.getInputProps("nombre")} />

          <SimpleGrid cols={{ base: 1, xs: 2 }}>
            <Stack gap={4}>
              <Text size="sm" fw={500}>
                Se vende por
              </Text>
              <SegmentedControl
                data={[
                  { value: "kg", label: "Kilo" },
                  { value: "unidad", label: "Unidad" },
                ]}
                {...formulario.getInputProps("unidad")}
              />
            </Stack>
            <Stack gap={4}>
              <Text size="sm" fw={500}>
                Precio
              </Text>
              <SegmentedControl
                data={[
                  { value: "manual", label: "Fijo" },
                  { value: "margen", label: "Costo + margen" },
                ]}
                {...formulario.getInputProps("modo_precio")}
              />
            </Stack>
          </SimpleGrid>

          <SimpleGrid cols={{ base: 1, xs: 3 }}>
            <EntradaDinero
              label="Último costo"
              description={valores.unidad === "kg" ? "Por kg" : "Por unidad"}
              {...formulario.getInputProps("costo_ultimo")}
            />
            {valores.modo_precio === "margen" && (
              <NumberInput
                label="Margen"
                description="Sobre el costo"
                suffix=" %"
                decimalSeparator=","
                decimalScale={2}
                allowNegative={false}
                hideControls
                {...formulario.getInputProps("margen")}
              />
            )}
            {calculado === null ? (
              <EntradaDinero
                label="Precio de venta"
                description={valores.unidad === "kg" ? "Por kg" : "Por unidad"}
                required
                {...formulario.getInputProps("precio")}
              />
            ) : (
              <Stack gap={2}>
                <Text size="sm" fw={500}>
                  Precio de venta
                </Text>
                <Text className="pl-cifra" fz={28} c="frasco.8">
                  {formatearPrecio(calculado)}
                </Text>
                <Text size="xs" c="var(--pl-tenue)">
                  Se recalcula con cada compra.
                </Text>
              </Stack>
            )}
          </SimpleGrid>

          <Stack gap={4}>
            <Text size="sm" fw={500}>
              Stock mínimo por sucursal
            </Text>
            <Text size="xs" c="var(--pl-tenue)">
              Cuando el stock baja de este número, avisa por Telegram. Con 0 no avisa.
            </Text>
            <SimpleGrid cols={{ base: 1, xs: 2 }}>
              {sucursales.map((s) => (
                <EntradaCantidad
                  key={s.id}
                  unidad={valores.unidad}
                  label={s.nombre}
                  {...formulario.getInputProps(`minimos.${s.id}`)}
                />
              ))}
            </SimpleGrid>
          </Stack>

          {producto && (
            <Switch
              label="Activo (se puede vender)"
              {...formulario.getInputProps("activo", { type: "checkbox" })}
            />
          )}

          {error && <Alert color="red">{error}</Alert>}
          <Group justify="flex-end" gap="xs">
            <Button variant="default" onClick={alCerrar}>
              Volver
            </Button>
            <Button type="submit" loading={enviando}>
              {producto ? "Guardar cambios" : "Crear producto"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
