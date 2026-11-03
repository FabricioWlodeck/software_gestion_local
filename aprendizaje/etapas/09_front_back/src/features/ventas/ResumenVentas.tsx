import { useEffect, useState } from "react";
import { api, ErrorApi } from "../../api/cliente";
import type { Venta } from "../../tipos";
import { formatearPrecio } from "../../utilidades/formato";

// Resumen para el rol dueño: GET /ventas, que el backend solo responde a ese rol.
export function ResumenVentas() {
  const [ventas, setVentas] = useState<Venta[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listarVentas()
      .then(setVentas)
      .catch((problema: ErrorApi) => setError(problema.message));
  }, []);

  if (error) {
    return <p className="error">{error}</p>;
  }
  if (ventas === null) {
    return <p>Cargando ventas…</p>;
  }

  const total = ventas.reduce((suma, venta) => suma + Number(venta.total), 0);
  return (
    <section className="resumen-ventas">
      <h2>Ventas registradas (solo dueño)</h2>
      <p>
        {ventas.length} ventas · {formatearPrecio(total)} en total. Se actualiza al recargar la página.
      </p>
    </section>
  );
}
