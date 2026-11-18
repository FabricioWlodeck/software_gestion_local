import { Box, Text, Tooltip, VisuallyHidden } from "@mantine/core";
import dayjs from "dayjs";
import type { VentaDiaria } from "../../tipos";
import { aCentavos, desdeCentavos } from "../../utilidades/decimal";
import { formatearFecha, formatearPrecio } from "../../utilidades/formato";
import clases from "./reportes.module.css";

interface Dia {
  fecha: string;
  centavos: number;
  cantidad: number;
}

// Suma las filas de cada día (llegan separadas por sucursal) y completa los días sin ventas con cero.
function agrupar(filas: VentaDiaria[], desde: string, hasta: string): Dia[] {
  const porDia = new Map<string, Dia>();
  for (let dia = dayjs(desde); !dia.isAfter(hasta, "day"); dia = dia.add(1, "day")) {
    const fecha = dia.format("YYYY-MM-DD");
    porDia.set(fecha, { fecha, centavos: 0, cantidad: 0 });
  }
  for (const fila of filas) {
    const dia = porDia.get(fila.fecha) ?? { fecha: fila.fecha, centavos: 0, cantidad: 0 };
    dia.centavos += aCentavos(fila.total);
    dia.cantidad += fila.cantidad;
    porDia.set(fila.fecha, dia);
  }
  return [...porDia.values()].sort((a, b) => a.fecha.localeCompare(b.fecha));
}

interface Props {
  filas: VentaDiaria[];
  desde: string;
  hasta: string;
}

// Barras de ventas válidas por día, sin librería de gráficos. Cada barra muestra el detalle al pasar el mouse.
export function GraficoVentasDiarias({ filas, desde, hasta }: Props) {
  const dias = agrupar(filas, desde, hasta);
  const maximo = Math.max(...dias.map((dia) => dia.centavos), 1);
  // Con muchos días, se rotulan solo algunos para que no se encimen
  const cadaCuanto = Math.ceil(dias.length / 10);

  return (
    <Box>
      <div className={clases.grafico} role="img" aria-label="Ventas por día">
        {dias.map((dia, indice) => (
          <div key={dia.fecha} className={clases.columna}>
            <Tooltip
              label={`${formatearFecha(dia.fecha)}: ${formatearPrecio(desdeCentavos(dia.centavos))} en ${dia.cantidad} ${dia.cantidad === 1 ? "venta" : "ventas"}`}
              withArrow
            >
              <div className={clases.zonaBarra}>
                <div className={clases.barra} style={{ height: `${(dia.centavos / maximo) * 100}%` }} />
              </div>
            </Tooltip>
            <Text size="xs" c="var(--pl-tenue)" className={clases.etiqueta}>
              {indice % cadaCuanto === 0 ? dayjs(dia.fecha).format("DD/MM") : ""}
            </Text>
          </div>
        ))}
      </div>
      {/* La misma información en una tabla para lectores de pantalla */}
      <VisuallyHidden>
        <table>
          <tbody>
            {dias.map((dia) => (
              <tr key={dia.fecha}>
                <td>{formatearFecha(dia.fecha)}</td>
                <td>{formatearPrecio(desdeCentavos(dia.centavos))}</td>
                <td>{dia.cantidad} ventas</td>
              </tr>
            ))}
          </tbody>
        </table>
      </VisuallyHidden>
    </Box>
  );
}
