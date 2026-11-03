// Etapa 07 - Un carrito en JavaScript con tres errores que JavaScript no avisa.
// Ejecutar:  node 02_carrito.js

const productos = [
  { id: 1, nombre: "Queso cremoso", unidad: "kg", precio: 12500 },
  { id: 2, nombre: "Leche entera 1 L", unidad: "unidad", precio: 1450 },
];

// Las cantidades llegan de un <input>: siempre son texto, aunque se escriban números.
const carrito = [
  { productoId: 1, cantidad: "0.350" },
  { productoId: 2, cantidad: "2" },
];

function buscarProducto(id) {
  return productos.find((producto) => producto.id === id);
}

// Error 1: se suma texto a un número.
let cantidadTotal = 0;
for (const item of carrito) {
  cantidadTotal = cantidadTotal + item.cantidad;
}
console.log("1) cantidad total:", cantidadTotal);

// Error 2: el nombre de la propiedad está mal escrito.
let total = 0;
for (const item of carrito) {
  const producto = buscarProducto(item.productoId);
  total = total + producto.precioo * item.cantidad;
}
console.log("2) total a cobrar:", total);

// Error 3: un producto que no existe.
const producto = buscarProducto(99);
console.log("3) producto:", producto.nombre);
