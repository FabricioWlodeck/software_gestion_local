import type { Producto } from "../tipos";

// Datos fijos para practicar sin backend. En el módulo 09 se reemplazan por GET /productos.
const PRODUCTOS: Producto[] = [
  { id: 1, nombre: "Queso cremoso", unidad: "kg", precio: "12500.00", stock: "2.100" },
  { id: 2, nombre: "Leche entera 1 L", unidad: "unidad", precio: "1450.00", stock: "24.000" },
  { id: 3, nombre: "Salame milán", unidad: "kg", precio: "18900.00", stock: "1.500" },
  { id: 4, nombre: "Yogur bebible 1 L", unidad: "unidad", precio: "2300.00", stock: "6.000" },
  { id: 5, nombre: "Queso rallado 150 g", unidad: "unidad", precio: "3100.00", stock: "0.000" },
];

// Simula la demora de pedirle los productos al backend.
export function cargarProductosDePrueba(): Promise<Producto[]> {
  return new Promise((resolver) => setTimeout(() => resolver(PRODUCTOS), 600));
}
