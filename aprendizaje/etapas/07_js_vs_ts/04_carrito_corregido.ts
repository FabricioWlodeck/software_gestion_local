// Etapa 07 - El carrito corregido siguiendo los avisos de TypeScript.
// Ejecutar:  node 04_carrito_corregido.ts
// Verificar: npx tsc --noEmit   (no muestra errores de este archivo)

interface Producto {
  id: number;
  nombre: string;
  unidad: "kg" | "unidad";
  precio: number;
}

interface ItemCarrito {
  productoId: number;
  cantidad: string;
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

// Corrección 1: el texto se convierte a número antes de sumar.
let cantidadTotal = 0;
for (const item of carrito) {
  cantidadTotal = cantidadTotal + Number(item.cantidad);
}
console.log("1) cantidad total:", cantidadTotal);

// Corrección 2: TypeScript sugirió el nombre correcto, y obliga a contemplar el producto inexistente.
let total = 0;
for (const item of carrito) {
  const producto = buscarProducto(item.productoId);
  if (producto === undefined) {
    throw new Error(`No existe el producto ${item.productoId}`);
  }
  total = total + producto.precio * Number(item.cantidad);
}
console.log("2) total a cobrar:", total);

// Corrección 3: se decide qué mostrar cuando no existe.
const producto = buscarProducto(99);
console.log("3) producto:", producto?.nombre ?? "(no existe)");
