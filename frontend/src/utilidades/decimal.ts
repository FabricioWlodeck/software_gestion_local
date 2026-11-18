// Cuentas con dinero sin errores de coma flotante: los importes se pasan a centavos enteros
// y las cantidades a milésimas enteras. Sirven para estimaciones en pantalla; el total que vale
// es el que devuelve el backend con Decimal.

// "7275.5" → 727550 centavos. Acepta signo y hasta 2 decimales (redondea si vienen más).
export function aCentavos(texto: string): number {
  return aEnteroEscalado(texto, 2);
}

// "0.350" → 350 milésimas
export function aMilesimas(texto: string): number {
  return aEnteroEscalado(texto, 3);
}

function aEnteroEscalado(texto: string, decimales: number): number {
  const limpio = texto.trim();
  const negativo = limpio.startsWith("-");
  const [entera = "0", fraccion = ""] = limpio.replace(/^[-+]/, "").split(".");
  const relleno = (fraccion + "0".repeat(decimales + 1)).slice(0, decimales + 1);
  const base = Number(entera || "0") * 10 ** decimales + Number(relleno.slice(0, decimales));
  const redondeo = Number(relleno[decimales]) >= 5 ? 1 : 0; // ROUND_HALF_UP
  const valor = base + redondeo;
  return negativo ? -valor : valor;
}

// 727550 → "7275.50"
export function desdeCentavos(centavos: number): string {
  const signo = centavos < 0 ? "-" : "";
  const absoluto = Math.abs(centavos);
  const entera = Math.floor(absoluto / 100);
  const fraccion = String(absoluto % 100).padStart(2, "0");
  return `${signo}${entera}.${fraccion}`;
}

// Subtotal de una línea en centavos: precio × cantidad, redondeado como el backend (HALF_UP).
export function subtotalEnCentavos(precio: string, cantidad: string): number {
  const producto = aCentavos(precio) * aMilesimas(cantidad); // escala: centavos × 1000
  return Math.floor((producto + 500) / 1000);
}

// Suma una lista de importes en texto. Devuelve centavos.
export function sumarCentavos(importes: string[]): number {
  return importes.reduce((total, importe) => total + aCentavos(importe), 0);
}

// Convierte lo que escribe el usuario ("0,350", "1.5", "2") al formato del backend ("0.350").
// Devuelve null si no es un número válido mayor o igual a cero.
export function normalizarDecimal(texto: string | number, decimales: number): string | null {
  const crudo = String(texto).trim().replace(",", ".");
  const patron = new RegExp(`^\\d+(\\.\\d{0,${decimales}})?$`);
  if (!patron.test(crudo)) {
    return null;
  }
  const [entera, fraccion = ""] = crudo.split(".");
  return decimales === 0 ? String(Number(entera)) : `${Number(entera)}.${fraccion.padEnd(decimales, "0")}`;
}

// true si la cantidad en texto es mayor que cero
export function esPositivo(texto: string): boolean {
  return aMilesimas(texto) > 0;
}

// Valor de un NumberInput de Mantine (number, o string mientras se escribe) → texto para la API.
export function textoDecimal(valor: string | number | null | undefined, decimales: number): string | null {
  if (valor === null || valor === undefined || valor === "") {
    return null;
  }
  return normalizarDecimal(typeof valor === "number" ? valor.toFixed(decimales) : valor, decimales);
}
