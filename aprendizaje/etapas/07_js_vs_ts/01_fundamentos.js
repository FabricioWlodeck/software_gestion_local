// Etapa 07 - JavaScript moderno: lo mínimo que se usa en React.
// Ejecutar:  node 01_fundamentos.js

// ---------- Variables: const por defecto, let si el valor cambia (var no se usa) ----------
const nombreLocal = "Punto Lácteo";
let ventasDelDia = 0;
ventasDelDia += 1;

// ---------- Texto con valores: template literals (como los f-strings de Python) ----------
console.log(`${nombreLocal}: ${ventasDelDia} venta(s)`);

// ---------- Objetos y arreglos (como dict y list de Python) ----------
const productos = [
  { id: 1, nombre: "Queso cremoso", unidad: "kg", precio: 12500, stock: 2.1 },
  { id: 2, nombre: "Leche entera 1 L", unidad: "unidad", precio: 1450, stock: 24 },
  { id: 3, nombre: "Salame milán", unidad: "kg", precio: 18900, stock: 1.5 },
];

// ---------- Funciones flecha ----------
const formatearPrecio = (valor) => `$${valor.toLocaleString("es-AR")}`;
console.log(formatearPrecio(12500));

// ---------- map, filter, find y reduce en lugar de bucles ----------
const nombres = productos.map((producto) => producto.nombre);
const porKilo = productos.filter((producto) => producto.unidad === "kg");
const leche = productos.find((producto) => producto.id === 2);
const kilosEnStock = porKilo.reduce((suma, producto) => suma + producto.stock, 0);
console.log(nombres);
console.log(`${porKilo.length} productos por kg, ${kilosEnStock} kg en total; el 2 es ${leche.nombre}`);

// ---------- Desestructuración y spread: copiar cambiando algo, sin modificar el original ----------
const { nombre, precio } = leche;
const lecheConAumento = { ...leche, precio: precio * 1.1 };
console.log(`${nombre}: antes ${leche.precio}, ahora ${lecheConAumento.precio}`); // ← punto flotante
const conYogur = [...productos, { id: 4, nombre: "Yogur bebible 1 L", unidad: "unidad", precio: 2300, stock: 6 }];
console.log(`productos: ${productos.length}, con el yogur: ${conYogur.length}`);

// ---------- === compara sin convertir tipos; == convierte y por eso no se usa ----------
console.log(`"2" == 2 → ${"2" == 2}    "2" === 2 → ${"2" === 2}`);

// ---------- undefined, ?. y ?? ----------
const inexistente = productos.find((producto) => producto.id === 99); // undefined
console.log(inexistente?.nombre ?? "(no existe)");

// ---------- Código asíncrono: async / await ----------
// Simula pedirle los productos al backend; en el módulo 09 se usa fetch de verdad.
const pedirProductos = () => new Promise((resolver) => setTimeout(() => resolver(productos), 300));

async function cargar() {
  console.log("pidiendo productos...");
  const lista = await pedirProductos(); // espera sin bloquear el resto del programa
  console.log(`llegaron ${lista.length} productos`);
}

cargar();
console.log("esta línea se imprime ANTES de que lleguen los productos");
