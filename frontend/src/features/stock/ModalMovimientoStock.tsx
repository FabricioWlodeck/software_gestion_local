import { Alert, Button, Group, Modal, SegmentedControl, Select, Stack, Text, Textarea } from "@mantine/core";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { EntradaCantidad } from "../../componentes/EntradaCantidad";
import type { FilaStock } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { aMilesimas, textoDecimal } from "../../utilidades/decimal";
import { formatearCantidad } from "../../utilidades/formato";

export type TipoCorreccion = "merma" | "ajuste";

interface Props {
  tipoInicial: TipoCorreccion;
  productoInicial: number | null;
  filas: FilaStock[];
  sucursalId: number;
  nombreSucursal: string;
  alCerrar: () => void;
  alGuardar: () => void;
}

// Merma (lo que se tira: vencido, roto) o ajuste (corrige el stock después de contar). Motivo obligatorio.
export function ModalMovimientoStock({ tipoInicial, productoInicial, filas, sucursalId, nombreSucursal, alCerrar, alGuardar }: Props) {
  const [tipo, setTipo] = useState<TipoCorreccion>(tipoInicial);
  const [productoId, setProductoId] = useState<number | null>(productoInicial);
  const [sentido, setSentido] = useState<"sumar" | "restar">("restar");
  const [cantidad, setCantidad] = useState<string | number>("");
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const fila = filas.find((f) => f.producto_id === productoId) ?? null;
  const cantidadTexto = fila ? textoDecimal(cantidad, fila.unidad === "kg" ? 3 : 0) : null;
  const resta = tipo === "merma" || sentido === "restar";
  const queda = fila && cantidadTexto ? aMilesimas(fila.cantidad) + (resta ? -1 : 1) * aMilesimas(cantidadTexto) : null;

  async function guardar() {
    if (fila === null) return setError("Elegí el producto.");
    if (cantidadTexto === null || aMilesimas(cantidadTexto) <= 0) return setError("Ingresá una cantidad mayor que cero.");
    if (motivo.trim() === "") return setError("Escribí el motivo: por ejemplo, vencido o conteo del viernes.");
    if (queda !== null && queda < 0) return setError(`No alcanza: hay ${formatearCantidad(fila.cantidad, fila.unidad)}.`);

    setEnviando(true);
    setError(null);
    try {
      // La merma va positiva; el ajuste lleva el signo (contrato, regla 8)
      const enviada = tipo === "ajuste" && resta ? `-${cantidadTexto}` : cantidadTexto;
      await api.registrarMovimiento({ sucursal_id: sucursalId, producto_id: fila.producto_id, tipo, cantidad: enviada, motivo: motivo.trim() });
      avisarExito(tipo === "merma" ? "Merma registrada" : "Ajuste registrado", `${fila.nombre} en ${nombreSucursal}.`);
      alGuardar();
    } catch (problema) {
      setError(mensajeDe(problema));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal opened onClose={alCerrar} title={<Text fw={700} size="lg">Corregir stock en {nombreSucursal}</Text>}>
      <Stack gap="md">
        <SegmentedControl
          fullWidth
          value={tipo}
          onChange={(valor) => setTipo(valor as TipoCorreccion)}
          data={[
            { value: "merma", label: "Merma" },
            { value: "ajuste", label: "Ajuste por conteo" },
          ]}
        />
        <Text size="sm" c="var(--pl-tenue)">
          {tipo === "merma"
            ? "Lo que se descarta: vencido, roto, mal estado. Se descuenta del stock."
            : "Para corregir el stock cuando lo contado no coincide con el sistema."}
        </Text>
        <Select
          label="Producto"
          placeholder="Buscá el producto"
          searchable
          data={filas.map((f) => ({ value: String(f.producto_id), label: f.nombre }))}
          value={productoId === null ? null : String(productoId)}
          onChange={(valor) => setProductoId(valor ? Number(valor) : null)}
          nothingFoundMessage="No hay productos con ese nombre"
        />
        {fila && (
          <>
            {tipo === "ajuste" && (
              <SegmentedControl
                value={sentido}
                onChange={(valor) => setSentido(valor as "sumar" | "restar")}
                data={[
                  { value: "restar", label: "Hay menos (restar)" },
                  { value: "sumar", label: "Hay más (sumar)" },
                ]}
              />
            )}
            <EntradaCantidad
              unidad={fila.unidad}
              label="Cantidad"
              description={`Hay ${formatearCantidad(fila.cantidad, fila.unidad)}.`}
              value={cantidad}
              onChange={setCantidad}
            />
            {queda !== null && (
              <Text>
                Va a quedar en <b className="pl-numero">{formatearCantidad(String(queda / 1000), fila.unidad)}</b>
              </Text>
            )}
          </>
        )}
        <Textarea
          label="Motivo"
          required
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
          <Button color={tipo === "merma" ? "red" : "frasco"} loading={enviando} onClick={guardar}>
            {tipo === "merma" ? "Registrar merma" : "Registrar ajuste"}
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
