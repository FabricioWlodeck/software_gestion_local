// Etapa 07 - El mismo carrito en TypeScript, con los mismos tres errores.
// Ejecutarlo:           node 03_carrito_con_errores.ts   (corre igual que el JS: los tipos se borran)
// Verificar los tipos:  npx tsc --noEmit                 (encuentra los tres errores sin ejecutar nada)

// El "contrato" de un producto: el mismo que ProductoOut en el backend.
interface Producto {
  id: number;
  nombre: string;
  unidad: "kg" | "unidad"; // como Literal["kg", "unidad"] en Pydantic
  precio: number;
}

interface ItemCarrito {
  productoId: number;
  cantidad: string; // viene de un <input>, así que es texto
}

const productos: Producto[] = [
  { id: 1, nombre: "Queso cremoso", unidad: "kg", precio: 12500 },
  { id: 2, nombre: "Leche entera 1 L", unidad: "unidad", precio: 1450 },
];

const carrito: ItemCarrito[] = [
  { productoId: 1, cantidad: "0.350" },
  { productoId: 2, cantidad: "2" },
];

function buscarProducto(id: number): Producto | undefined {
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
