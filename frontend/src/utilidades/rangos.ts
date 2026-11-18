// Períodos de fechas para los filtros (YYYY-MM-DD, ambas inclusivas, como las espera la API).

import dayjs from "dayjs";
import { hoyIso } from "./formato";

export interface RangoFechas {
  desde: string;
  hasta: string;
}

export function rangoDeHoy(): RangoFechas {
  return { desde: hoyIso(), hasta: hoyIso() };
}

export function rangoUltimosDias(dias: number): RangoFechas {
  return { desde: dayjs().subtract(dias - 1, "day").format("YYYY-MM-DD"), hasta: hoyIso() };
}

export function rangoDelMes(): RangoFechas {
  return { desde: dayjs().startOf("month").format("YYYY-MM-DD"), hasta: hoyIso() };
}
