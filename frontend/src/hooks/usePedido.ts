import { useCallback, useEffect, useEffectEvent, useState } from "react";
import { mensajeDe } from "../api/cliente";

// Resultado del último pedido que terminó
interface Resultado<T> {
  clave: string | null; // de qué pedido son los datos
  version: number;
  datos: T | null;
  error: string | null;
}

// Pide datos a la API cada vez que cambia la clave (por ejemplo "stock-1" → "stock-2").
// Con clave null no pide nada (falta algún dato, como la sucursal).
// Si llega una respuesta vieja después de cambiar la clave, se descarta.
export function usePedido<T>(clave: string | null, pedir: () => Promise<T>) {
  const [resultado, setResultado] = useState<Resultado<T>>({ clave: null, version: -1, datos: null, error: null });
  const [version, setVersion] = useState(0);

  // useEffectEvent: el efecto usa siempre la última versión de pedir() sin depender de ella
  const ejecutar = useEffectEvent(() => pedir());

  useEffect(() => {
    if (clave === null) {
      return;
    }
    let vigente = true;
    ejecutar()
      .then((datos) => {
        if (vigente) setResultado({ clave, version, datos, error: null });
      })
      .catch((error: unknown) => {
        // Si falla una recarga, se siguen mostrando los datos anteriores de la misma clave
        if (vigente)
          setResultado((anterior) => ({
            clave,
            version,
            datos: anterior.clave === clave ? anterior.datos : null,
            error: mensajeDe(error),
          }));
      });
    return () => {
      vigente = false;
    };
  }, [clave, version]);

  const recargar = useCallback(() => setVersion((numero) => numero + 1), []);

  // Los datos de otra clave (otra sucursal, otras fechas) no se muestran mientras carga la nueva
  const mismaClave = resultado.clave === clave;
  return {
    datos: mismaClave ? resultado.datos : null,
    error: mismaClave ? resultado.error : null,
    cargando: clave !== null && (!mismaClave || resultado.version !== version),
    recargar,
  };
}
