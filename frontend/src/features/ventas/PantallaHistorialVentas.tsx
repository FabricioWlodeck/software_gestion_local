import { Group, Paper, Select, Table, Text } from "@mantine/core";
import { IconReceipt } from "@tabler/icons-react";
import { useState } from "react";
import { api } from "../../api/cliente";
import { ConfirmarAccion } from "../../componentes/ConfirmarAccion";
import { EncabezadoPagina } from "../../componentes/EncabezadoPagina";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { FiltroFechas } from "../../componentes/FiltroFechas";
import { rangoDeHoy, type RangoFechas } from "../../utilidades/rangos";
import { PaginaVacia } from "../../componentes/PaginaVacia";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import type { EstadoVenta, Venta } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { desdeCentavos, sumarCentavos } from "../../utilidades/decimal";
import { formatearFecha, formatearPrecio } from "../../utilidades/formato";
import { useSesion } from "../auth/sesion";
import { FilaVenta, type AccionVenta } from "./FilaVenta";

const TEXTOS_ACCION: Record<AccionVenta, { titulo: string; boton: string; color: string; motivo: "obligatorio" | "opcional" }> = {
  observar: { titulo: "Observar la venta", boton: "Observar", color: "orange", motivo: "obligatorio" },
  confirmar: { titulo: "Confirmar la venta", boton: "Confirmar", color: "frasco", motivo: "opcional" },
  anular: { titulo: "Anular la venta", boton: "Anular", color: "red", motivo: "obligatorio" },
};

const DESCRIPCIONES: Record<AccionVenta, string> = {
  observar: "Queda marcada para que la dueña la revise. No cambia el stock ni la caja.",
  confirmar: "Vuelve a contar como válida en los totales.",
  anular: "Deja de contar en los totales y los productos vuelven al stock. No se puede deshacer.",
};

// Ventas de la sucursal activa. El empleado ve solo las de hoy; la dueña elige el período.
export function PantallaHistorialVentas() {
  const { esDuenia } = useSesion();
  const { sucursalId, sucursal } = useSucursalActiva();
  const [rango, setRango] = useState<RangoFechas>(rangoDeHoy);
  const [estado, setEstado] = useState<EstadoVenta | null>(null);
  const [desplegadas, setDesplegadas] = useState<Set<number>>(new Set());
  const [accion, setAccion] = useState<{ tipo: AccionVenta; venta: Venta } | null>(null);

  // El empleado siempre pide hoy (el backend igual se lo limita)
  const periodo = esDuenia ? rango : rangoDeHoy();
  const clave = sucursalId === null ? null : `ventas-${sucursalId}-${periodo.desde}-${periodo.hasta}-${estado}`;
  const ventas = usePedido(clave, () =>
    api.listarVentas({ sucursal_id: sucursalId ?? 0, desde: periodo.desde, hasta: periodo.hasta, estado, limite: 200 }),
  );

  const lista = ventas.datos ?? [];
  const validas = lista.filter((venta) => venta.estado === "valida");
  const observadas = lista.filter((venta) => venta.estado === "observada").length;
  const anuladas = lista.filter((venta) => venta.estado === "anulada").length;

  function alternar(id: number) {
    setDesplegadas((anteriores) => {
      const nuevas = new Set(anteriores);
      if (nuevas.has(id)) nuevas.delete(id);
      else nuevas.add(id);
      return nuevas;
    });
  }

  async function ejecutar(motivo: string | null) {
    if (accion === null) return;
    const { tipo, venta } = accion;
    if (tipo === "observar") await api.observarVenta(venta.id, motivo ?? "");
    if (tipo === "confirmar") await api.confirmarVenta(venta.id, motivo);
    if (tipo === "anular") await api.anularVenta(venta.id, motivo ?? "");
    const hechos = { observar: "observada", confirmar: "confirmada", anular: "anulada" };
    avisarExito(`Venta ${venta.id} ${hechos[tipo]}`);
    ventas.recargar();
  }

  const detalle = esDuenia
    ? `${sucursal?.nombre ?? ""}, del ${formatearFecha(periodo.desde)} al ${formatearFecha(periodo.hasta)}`
    : `${sucursal?.nombre ?? ""}, hoy`;

  return (
    <>
      <EncabezadoPagina titulo="Ventas" detalle={detalle} />

      <Group gap="sm" mb="md" align="flex-end" wrap="wrap">
        {esDuenia && <FiltroFechas rango={rango} alCambiar={setRango} />}
        <Select
          aria-label="Filtrar por estado"
          size="sm"
          w={180}
          data={[
            { value: "", label: "Todos los estados" },
            { value: "valida", label: "Válidas" },
            { value: "observada", label: "Observadas" },
            { value: "anulada", label: "Anuladas" },
          ]}
          value={estado ?? ""}
          onChange={(valor) => setEstado((valor || null) as EstadoVenta | null)}
        />
      </Group>

      {ventas.error && <ErrorCarga mensaje={ventas.error} alReintentar={ventas.recargar} />}

      {lista.length > 0 && (
        <Text mb="xs">
          <b>
            {validas.length} {validas.length === 1 ? "venta válida" : "ventas válidas"} por{" "}
            {formatearPrecio(desdeCentavos(sumarCentavos(validas.map((venta) => venta.total))))}
          </b>
          {observadas > 0 && `, ${observadas} observada${observadas === 1 ? "" : "s"}`}
          {anuladas > 0 && `, ${anuladas} anulada${anuladas === 1 ? "" : "s"}`}.
        </Text>
      )}

      <Paper withBorder radius="sm">
        {lista.length === 0 && !ventas.cargando ? (
          <PaginaVacia
            icono={<IconReceipt size={28} />}
            titulo="No hay ventas en este período"
            descripcion={esDuenia ? "Probá con otras fechas u otra sucursal." : "Las ventas que cobres hoy aparecen acá."}
          />
        ) : (
          <Table.ScrollContainer minWidth={760}>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th />
                  <Table.Th>N.º</Table.Th>
                  <Table.Th>{esDuenia ? "Fecha" : "Hora"}</Table.Th>
                  <Table.Th>Vendió</Table.Th>
                  <Table.Th>Medio</Table.Th>
                  <Table.Th ta="right">Total</Table.Th>
                  <Table.Th>Estado</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {lista.map((venta) => (
                  <FilaVenta
                    key={venta.id}
                    venta={venta}
                    desplegada={desplegadas.has(venta.id)}
                    soloHora={!esDuenia}
                    esDuenia={esDuenia}
                    alDesplegar={() => alternar(venta.id)}
                    alAccion={(tipo, elegida) => setAccion({ tipo, venta: elegida })}
                  />
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Paper>

      {accion && (
        <ConfirmarAccion
          abierto
          titulo={`${TEXTOS_ACCION[accion.tipo].titulo} N.º ${accion.venta.id}`}
          descripcion={`${formatearPrecio(accion.venta.total)} cobrada por ${accion.venta.usuario}. ${DESCRIPCIONES[accion.tipo]}`}
          motivo={TEXTOS_ACCION[accion.tipo].motivo}
          etiquetaMotivo={accion.tipo === "observar" ? "¿Qué pasó con esta venta?" : "Motivo"}
          textoConfirmar={TEXTOS_ACCION[accion.tipo].boton}
          color={TEXTOS_ACCION[accion.tipo].color}
          alCerrar={() => setAccion(null)}
          alConfirmar={ejecutar}
        />
      )}
    </>
  );
}
