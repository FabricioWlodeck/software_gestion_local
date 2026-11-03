// Funciones de formato. No son componentes: son TypeScript común, reutilizable en cualquier pantalla.

const moneda = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });

export function formatearPrecio(valor: string | number): string {
  return moneda.format(Number(valor));
}

export function formatearCantidad(cantidad: string, unidad: "kg" | "unidad"): string {
  const numero = Number(cantidad).toLocaleString("es-AR");
  return unidad === "kg" ? `${numero} kg` : `${numero} u.`;
}

// Estimación para mostrar en pantalla. El total que vale es el que calcula el backend con Decimal.
export function calcularSubtotal(precio: string, cantidad: string): number {
  return Math.round(Number(precio) * Number(cantidad) * 100) / 100;
}
