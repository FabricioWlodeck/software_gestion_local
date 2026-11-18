import { Button, Group } from "@mantine/core";
import { DatePickerInput, type DatesRangeValue } from "@mantine/dates";
import { IconCalendar } from "@tabler/icons-react";
import { hoyIso } from "../utilidades/formato";
import { rangoDelMes, rangoDeHoy, rangoUltimosDias, type RangoFechas } from "../utilidades/rangos";

// Períodos de un clic; "hasta" siempre es hoy
const PERIODOS = [
  { texto: "Hoy", desde: () => rangoDeHoy().desde },
  { texto: "Últimos 7 días", desde: () => rangoUltimosDias(7).desde },
  { texto: "Este mes", desde: () => rangoDelMes().desde },
];

interface Props {
  rango: RangoFechas;
  alCambiar: (rango: RangoFechas) => void;
}

// Filtro por período: botones rápidos y un calendario para elegir otras fechas (ambas inclusivas).
export function FiltroFechas({ rango, alCambiar }: Props) {
  const hoy = hoyIso();

  function elegirEnCalendario([desde, hasta]: DatesRangeValue<string>) {
    // Se aplica cuando están las dos fechas (con un solo día, desde = hasta)
    if (desde && hasta) alCambiar({ desde, hasta });
  }

  return (
    <Group gap="xs" wrap="wrap">
      {PERIODOS.map((periodo) => {
        const desde = periodo.desde();
        const activo = rango.desde === desde && rango.hasta === hoy;
        return (
          <Button
            key={periodo.texto}
            size="sm"
            variant={activo ? "filled" : "default"}
            onClick={() => alCambiar({ desde, hasta: hoy })}
          >
            {periodo.texto}
          </Button>
        );
      })}
      {/* Sin controlar: guarda la primera fecha mientras se elige la segunda.
          La key lo reinicia cuando el rango cambia desde afuera (por ejemplo, con un botón). */}
      <DatePickerInput
        key={`${rango.desde}_${rango.hasta}`}
        type="range"
        aria-label="Elegir fechas"
        size="sm"
        w={230}
        leftSection={<IconCalendar size={16} aria-hidden />}
        valueFormat="DD/MM/YYYY"
        defaultValue={[rango.desde, rango.hasta]}
        onChange={elegirEnCalendario}
        allowSingleDateInRange
        maxDate={hoy}
      />
    </Group>
  );
}
