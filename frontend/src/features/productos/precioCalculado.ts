// Precio en modo margen: costo × (1 + margen / 100), redondeado al centavo como el backend (regla 10).

import { aCentavos, desdeCentavos } from "../../utilidades/decimal";

export function precioPorMargen(costo: string, margen: string): string {
  const costoCentavos = aCentavos(costo);
  const margenCentesimos = aCentavos(margen); // 35.5 % → 3550
  // costo × (10000 + margen×100) / 10000, con redondeo HALF_UP
  const escalado = costoCentavos * (10000 + margenCentesimos);
  return desdeCentavos(Math.floor((escalado + 5000) / 10000));
}
