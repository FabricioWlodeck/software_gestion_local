// Avisos flotantes (notificaciones de Mantine) con el mismo estilo en toda la aplicación.

import { notifications } from "@mantine/notifications";
import { mensajeDe } from "../api/cliente";

export function avisarExito(titulo: string, mensaje?: string): void {
  notifications.show({ title: titulo, message: mensaje ?? "", color: "frasco", autoClose: 5000 });
}

export function avisarError(error: unknown, titulo = "No se pudo completar"): void {
  notifications.show({ title: titulo, message: mensajeDe(error), color: "red", autoClose: 8000 });
}
