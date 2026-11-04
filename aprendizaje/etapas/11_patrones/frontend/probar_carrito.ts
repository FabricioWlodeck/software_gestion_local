// Prueba del reducer sin React ni navegador. Ejecutar desde la carpeta de la etapa:
//   node frontend/probar_carrito.ts
// Node 24 quita los tipos y ejecuta el archivo; no los verifica (eso lo hace tsc, módulo 07).

import assert from "node:assert/strict";
import { carritoReducer } from "./carritoReducer.ts";
import type { ItemCarrito, Producto } from "./tipos.ts";

const queso: Producto = { id: 1, nombre: "Queso cremoso", unidad: "kg", precio: "12500.00", stock: "2.100" };
const leche: Producto = { id: 2, nombre: "Leche entera 1 L", unidad: "unidad", precio: "1450.00", stock: "24" };

function mostrar(paso: string, items: ItemCarrito[]): void {
  const lineas = items.map((item) => `${item.producto.nombre} × ${item.cantidad}`).join(", ") || "(vacío)";
  console.log(`${paso.padEnd(28)} → ${lineas}`);
}

const inicial: ItemCarrito[] = [];
mostrar("Estado inicial", inicial);

const conQueso = carritoReducer(inicial, { tipo: "agregar", producto: queso, cantidad: "0.350" });
mostrar("agregar queso 0.350", conQueso);

const conLeche = carritoReducer(conQueso, { tipo: "agregar", producto: leche, cantidad: "2" });
mostrar("agregar leche 2", conLeche);

const corregido = carritoReducer(conLeche, { tipo: "agregar", producto: queso, cantidad: "0.500" });
mostrar("agregar queso 0.500 otra vez", corregido);

const sinLeche = carritoReducer(corregido, { tipo: "quitar", productoId: 2 });
mostrar("quitar leche", sinLeche);

const vacio = carritoReducer(sinLeche, { tipo: "vaciar" });
mostrar("vaciar", vacio);

// Las comprobaciones: si alguna falla, Node se detiene con un error que dice cuál.
assert.equal(corregido.length, 2, "agregar un producto repetido no duplica la línea");
assert.equal(corregido.find((item) => item.producto.id === 1)?.cantidad, "0.500", "la cantidad se reemplaza");
assert.deepEqual(sinLeche.map((item) => item.producto.id), [1]);
assert.deepEqual(vacio, []);
assert.equal(conQueso.length, 1, "el estado anterior no se modificó: el reducer devuelve uno nuevo");
assert.notEqual(conQueso, conLeche);

console.log("\nTodas las comprobaciones pasaron.");
