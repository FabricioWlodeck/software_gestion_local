import type { TipoMovimiento } from "../../tipos";

// Nombre y color de cada tipo de movimiento de stock
export const TIPOS_MOVIMIENTO: Record<TipoMovimiento, { texto: string; color: string }> = {
  compra: { texto: "Compra", color: "frasco" },
  venta: { texto: "Venta", color: "gray" },
  merma: { texto: "Merma", color: "red" },
  ajuste: { texto: "Ajuste", color: "grape" },
  traspaso_salida: { texto: "Traspaso enviado", color: "blue" },
  traspaso_entrada: { texto: "Traspaso recibido", color: "cyan" },
  anulacion: { texto: "Anulación", color: "orange" },
};

export const OPCIONES_TIPO = Object.entries(TIPOS_MOVIMIENTO).map(([value, { texto }]) => ({ value, label: texto }));
