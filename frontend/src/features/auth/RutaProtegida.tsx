import { Center, Loader } from "@mantine/core";
import { Navigate, Outlet, useLocation } from "react-router";
import { useSesion } from "./sesion";

interface Props {
  soloDuenia?: boolean;
}

// Deja pasar solo con sesión iniciada; con soloDuenia, además exige el rol de dueña.
// Ocultar no es proteger: el backend igual responde 403 a un empleado.
export function RutaProtegida({ soloDuenia = false }: Props) {
  const { usuario, esDuenia, verificando } = useSesion();
  const ubicacion = useLocation();

  if (verificando) {
    return (
      <Center h="100dvh">
        <Loader aria-label="Verificando la sesión" />
      </Center>
    );
  }
  if (usuario === null) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />;
  }
  if (soloDuenia && !esDuenia) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
