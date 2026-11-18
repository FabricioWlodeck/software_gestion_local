import { Box, Button, Group, Stack, Text } from "@mantine/core";
import { useHotkeys } from "@mantine/hooks";
import { useEffect, useRef, useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { ErrorCarga } from "../../componentes/ErrorCarga";
import { useSucursalActiva } from "../../hooks/sucursalActiva";
import { usePedido } from "../../hooks/usePedido";
import type { ItemCarrito, MedioPago, Venta } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { aMilesimas, desdeCentavos, textoDecimal } from "../../utilidades/decimal";
import { formatearCantidad, formatearPrecio } from "../../utilidades/formato";
import { BarraCaja } from "../caja/BarraCaja";
import { useCajaActual } from "../caja/useCajaActual";
import { BuscadorProductos } from "./BuscadorProductos";
import { GrillaProductos } from "./GrillaProductos";
import { PanelBalanza } from "./PanelBalanza";
import { coincide, desdeFilaStock, type ProductoEnVenta } from "./productoEnVenta";
import { Ticket } from "./Ticket";
import { useCarrito } from "./useCarrito";
import clases from "./venta.module.css";

// Pantalla principal del mostrador: buscar, pesar, sumar al ticket y cobrar.
export function PantallaVenta() {
  const { sucursalId, sucursal } = useSucursalActiva();
  const nombreSucursal = sucursal?.nombre ?? "la sucursal";

  const stock = usePedido(sucursalId === null ? null : `stock-${sucursalId}`, () => api.listarStock(sucursalId ?? 0));
  const caja = useCajaActual(sucursalId);
  const carrito = useCarrito();

  const [busqueda, setBusqueda] = useState("");
  const [resaltado, setResaltado] = useState(0);
  const [elegido, setElegido] = useState<ProductoEnVenta | null>(null);
  const [cantidad, setCantidad] = useState<string | number>("");
  const [errorCantidad, setErrorCantidad] = useState<string | null>(null);
  const [medioPago, setMedioPago] = useState<MedioPago>("efectivo");
  const [cobrando, setCobrando] = useState(false);
  const [errorCobro, setErrorCobro] = useState<string | null>(null);
  const [ultimaVenta, setUltimaVenta] = useState<Venta | null>(null);

  // El foco se mueve después de dibujar (el campo de cantidad aparece al elegir un producto)
  const refBusqueda = useRef<HTMLInputElement>(null);
  const refCantidad = useRef<HTMLInputElement>(null);
  const [foco, setFoco] = useState<{ en: "busqueda" | "cantidad"; vez: number }>({ en: "busqueda", vez: 0 });
  const enfocar = (en: "busqueda" | "cantidad") => setFoco((anterior) => ({ en, vez: anterior.vez + 1 }));

  useEffect(() => {
    const campo = foco.en === "busqueda" ? refBusqueda.current : refCantidad.current;
    campo?.focus();
    campo?.select();
  }, [foco]);

  const productos = (stock.datos ?? [])
    .map(desdeFilaStock)
    .filter((producto) => coincide(producto, busqueda))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));

  function buscar(texto: string) {
    setBusqueda(texto);
    setResaltado(0);
  }

  function mover(salto: number) {
    if (productos.length === 0) return;
    setResaltado((actual) => (actual + salto + productos.length) % productos.length);
  }

  function elegir(producto: ProductoEnVenta) {
    const enTicket = carrito.items.find((item) => item.producto.id === producto.id);
    setElegido(producto);
    setErrorCantidad(null);
    if (enTicket) {
      setCantidad(Number(enTicket.cantidad));
    } else {
      setCantidad(producto.unidad === "unidad" ? 1 : "");
    }
    enfocar("cantidad");
  }

  function elegirResaltado() {
    const producto = productos[resaltado];
    if (producto && aMilesimas(producto.stock) > 0) {
      elegir(producto);
    }
  }

  function cancelar() {
    setElegido(null);
    setErrorCantidad(null);
    enfocar("busqueda");
  }

  function agregar() {
    if (elegido === null) return;
    const texto = textoDecimal(cantidad, elegido.unidad === "kg" ? 3 : 0);
    if (texto === null || aMilesimas(texto) <= 0) {
      setErrorCantidad(elegido.unidad === "kg" ? "Ingresá el peso, por ejemplo 0,350" : "Ingresá cuántas unidades");
      return;
    }
    if (aMilesimas(texto) > aMilesimas(elegido.stock)) {
      setErrorCantidad(`Solo hay ${formatearCantidad(elegido.stock, elegido.unidad)} en ${nombreSucursal}`);
      return;
    }
    carrito.agregar(elegido, texto);
    setElegido(null);
    setErrorCantidad(null);
    setErrorCobro(null);
    buscar("");
    enfocar("busqueda");
  }

  function editar(item: ItemCarrito) {
    const producto = productos.find((p) => p.id === item.producto.id);
    elegir(producto ?? { ...item.producto, bajoMinimo: false });
  }

  // Motivo por el que no se puede cobrar, en palabras
  let bloqueo: string | null = null;
  if (sucursalId === null) bloqueo = "Elegí una sucursal arriba para poder cobrar.";
  else if (caja.error) bloqueo = "No se pudo verificar la caja. Revisá la conexión.";
  else if (caja.datos === null && !caja.cargando) bloqueo = "La caja está cerrada. Abrila para cobrar.";

  async function cobrar() {
    if (sucursalId === null || bloqueo !== null || carrito.items.length === 0 || cobrando) return;
    setCobrando(true);
    setErrorCobro(null);
    try {
      const venta = await api.registrarVenta({
        sucursal_id: sucursalId,
        medio_pago: medioPago,
        items: carrito.items.map((item) => ({ producto_id: item.producto.id, cantidad: item.cantidad })),
      });
      carrito.vaciar();
      setUltimaVenta(venta);
      setMedioPago("efectivo");
      setElegido(null);
      avisarExito(`Venta ${venta.id} cobrada`, `${formatearPrecio(venta.total)} en ${venta.medio_pago}.`);
      enfocar("busqueda");
    } catch (problema) {
      // 409 (sin stock, caja cerrada) o 422 (datos inválidos): el ticket queda como estaba
      setErrorCobro(mensajeDe(problema));
    } finally {
      // En los dos casos se trae el stock y la caja al día
      setCobrando(false);
      stock.recargar();
      caja.recargar();
    }
  }

  // F2 vuelve al buscador y F9 cobra, aunque el foco esté en un campo
  useHotkeys(
    [
      ["F2", () => enfocar("busqueda")],
      [
        "F9",
        () => {
          if (!document.querySelector("[role='dialog']")) cobrar();
        },
      ],
    ],
    [],
  );

  const enTicket = elegido !== null && carrito.items.some((item) => item.producto.id === elegido.id);

  return (
    <Stack gap="md">
      {sucursalId !== null && (
        <BarraCaja
          caja={caja.datos}
          cargando={caja.cargando}
          sucursalId={sucursalId}
          nombreSucursal={nombreSucursal}
          alCambiar={() => {
            caja.recargar();
            enfocar("busqueda"); // al abrir la caja, se sigue con el buscador
          }}
        />
      )}

      <div className={clases.pantalla}>
        <Stack gap="sm" miw={0}>
          <BuscadorProductos
            ref={refBusqueda}
            valor={busqueda}
            alCambiar={buscar}
            alMover={mover}
            alConfirmar={elegirResaltado}
          />
          <PanelBalanza
            ref={refCantidad}
            producto={elegido}
            cantidad={cantidad}
            enTicket={enTicket}
            error={errorCantidad}
            alCambiarCantidad={(valor) => {
              setCantidad(valor);
              setErrorCantidad(null);
            }}
            alAgregar={agregar}
            alCancelar={cancelar}
          />
          {stock.error ? (
            <ErrorCarga mensaje={stock.error} alReintentar={stock.recargar} />
          ) : (
            <GrillaProductos
              productos={productos}
              cargando={stock.cargando}
              busqueda={busqueda}
              resaltado={resaltado}
              items={carrito.items}
              alElegir={elegir}
            />
          )}
        </Stack>

        <Ticket
          key={ultimaVenta?.id ?? 0}
          items={carrito.items}
          totalCentavos={carrito.totalCentavos}
          medioPago={medioPago}
          cobrando={cobrando}
          bloqueo={bloqueo}
          error={errorCobro}
          ultimaVenta={ultimaVenta}
          alCambiarMedio={setMedioPago}
          alEditar={editar}
          alQuitar={carrito.quitar}
          alVaciar={() => {
            carrito.vaciar();
            setErrorCobro(null);
          }}
          alCobrar={cobrar}
        />
      </div>

      {carrito.items.length > 0 && (
        <Box className={clases.barraMovil} hiddenFrom="md">
          <Group justify="space-between" wrap="nowrap">
            <Box>
              <Text size="sm" c="var(--pl-tenue)">
                Total ({carrito.items.length} {carrito.items.length === 1 ? "producto" : "productos"})
              </Text>
              <Text className="pl-cifra" fz={28} lh={1}>
                {formatearPrecio(desdeCentavos(carrito.totalCentavos))}
              </Text>
            </Box>
            <Button onClick={() => document.getElementById("ticket")?.scrollIntoView({ behavior: "smooth" })}>
              Ver ticket
            </Button>
          </Group>
        </Box>
      )}
    </Stack>
  );
}
