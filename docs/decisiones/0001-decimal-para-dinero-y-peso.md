# 0001. Dinero y cantidades como DECIMAL, nunca como FLOAT

- **Estado:** Aceptada
- **Fecha:** 2026-11-03 (módulo 04)

## Contexto

Punto Lácteo vende por peso y por unidad. Los precios están en pesos con centavos y las cantidades en kilogramos con precisión de gramos. Las ventas se suman para el total del día y el stock se descuenta en cada venta, así que cualquier error de redondeo se acumula.

Un `FLOAT` guarda los números en binario y no puede representar exactamente valores como 0,1 o 0,35. La suma de muchos valores así no da el resultado exacto.

## Opciones consideradas

1. **FLOAT o DOUBLE.** Es el tipo numérico por defecto en muchos lenguajes y ocupa poco, pero es inexacto para decimales.
2. **Enteros en la unidad mínima** (centavos y gramos). Son exactos y rápidos, pero obligan a convertir en cada lugar donde se muestra o se recibe un valor.
3. **DECIMAL con escala fija.** Es exacto y se lee igual que en la balanza o en el ticket.

## Decisión

Se usa `DECIMAL(10, 2)` para precios, `DECIMAL(12, 2)` para totales y `DECIMAL(10, 3)` para cantidades y stock. En Python se usa `Decimal` y en el JSON los valores viajan como texto (`"0.350"`).

## Consecuencias

- Las sumas y los descuentos de stock son exactos.
- El frontend recibe texto y usa `Number` solo para mostrar estimaciones; el total válido es el que calcula el backend.
- Hay que redondear de forma explícita (`quantize`) al multiplicar cantidad por precio.
