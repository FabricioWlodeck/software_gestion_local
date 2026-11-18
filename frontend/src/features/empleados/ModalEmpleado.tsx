import { Alert, Button, Group, Modal, PasswordInput, SegmentedControl, Stack, Switch, Text, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import { SelectSucursal } from "../../componentes/SelectSucursal";
import type { Rol, Usuario } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";
import { useUsuario } from "../auth/sesion";

interface Valores {
  nombre_usuario: string;
  nombre: string;
  contrasena: string;
  rol: Rol;
  sucursal_id: number | null;
  activo: boolean;
  telegram_id: string;
}

interface Props {
  empleado: Usuario | null; // null = usuario nuevo
  alCerrar: () => void;
  alGuardar: () => void;
}

// Alta y edición de usuarios (solo la dueña): rol, sucursal, activo y el id de Telegram para los avisos.
export function ModalEmpleado({ empleado, alCerrar, alGuardar }: Props) {
  const yo = useUsuario();
  const esYo = empleado?.id === yo.id;
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const formulario = useForm<Valores>({
    mode: "controlled",
    initialValues: {
      nombre_usuario: empleado?.nombre_usuario ?? "",
      nombre: empleado?.nombre ?? "",
      contrasena: "",
      rol: empleado?.rol ?? "empleado",
      sucursal_id: empleado?.sucursal_id ?? null,
      activo: empleado?.activo ?? true,
      telegram_id: empleado?.telegram_id ? String(empleado.telegram_id) : "",
    },
    validate: {
      nombre_usuario: (valor) =>
        empleado === null && !/^[a-z0-9._-]{3,40}$/i.test(valor.trim())
          ? "Entre 3 y 40 letras o números, sin espacios"
          : null,
      nombre: (valor) => (valor.trim() === "" ? "Escribí el nombre" : null),
      contrasena: (valor) => (empleado === null && valor.length < 6 ? "Tiene que tener al menos 6 caracteres" : null),
      sucursal_id: (valor, valores) => (valores.rol === "empleado" && valor === null ? "Elegí la sucursal donde trabaja" : null),
      telegram_id: (valor) => (valor.trim() !== "" && !/^-?\d{4,20}$/.test(valor.trim()) ? "Es un número, por ejemplo 123456789" : null),
    },
  });
  const valores = formulario.getValues();

  async function guardar(v: Valores) {
    setEnviando(true);
    setError(null);
    const sucursal_id = v.rol === "duenio" ? null : v.sucursal_id;
    try {
      if (empleado === null) {
        const nuevo = await api.crearUsuario({
          nombre_usuario: v.nombre_usuario.trim(),
          nombre: v.nombre.trim(),
          contrasena: v.contrasena,
          rol: v.rol,
          sucursal_id,
        });
        avisarExito("Usuario creado", `${nuevo.nombre} ya puede ingresar como «${nuevo.nombre_usuario}».`);
      } else {
        await api.editarUsuario(empleado.id, {
          nombre: v.nombre.trim(),
          rol: v.rol,
          sucursal_id,
          activo: v.activo,
          telegram_id: v.telegram_id.trim() === "" ? null : Number(v.telegram_id.trim()),
        });
        avisarExito("Cambios guardados", v.nombre.trim());
      }
      alGuardar();
    } catch (problema) {
      setError(mensajeDe(problema));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal
      opened
      onClose={alCerrar}
      title={
        <Text fw={700} size="lg">
          {empleado ? `Editar a ${empleado.nombre}` : "Nuevo usuario"}
        </Text>
      }
    >
      <form onSubmit={formulario.onSubmit(guardar)}>
        <Stack gap="md">
          <TextInput label="Nombre" required maxLength={80} data-autofocus {...formulario.getInputProps("nombre")} />
          {empleado === null ? (
            <>
              <TextInput
                label="Usuario para ingresar"
                description="Sin espacios, por ejemplo: bruno"
                required
                maxLength={40}
                autoCapitalize="none"
                {...formulario.getInputProps("nombre_usuario")}
              />
              <PasswordInput
                label="Contraseña"
                description="Al menos 6 caracteres. Después la puede cambiar la dueña."
                required
                size="md"
                autoComplete="new-password"
                {...formulario.getInputProps("contrasena")}
              />
            </>
          ) : (
            <Text size="sm">
              Ingresa como <b>{empleado.nombre_usuario}</b>
            </Text>
          )}

          <Stack gap={4}>
            <Text size="sm" fw={500}>
              Rol
            </Text>
            <SegmentedControl
              disabled={esYo}
              data={[
                { value: "empleado", label: "Empleado" },
                { value: "duenio", label: "Dueña" },
              ]}
              {...formulario.getInputProps("rol")}
            />
            <Text size="xs" c="var(--pl-tenue)">
              {valores.rol === "duenio"
                ? "Ve todas las sucursales, los reportes, los costos y la administración."
                : "Vende, cierra la caja y registra mermas solo en su sucursal."}
            </Text>
          </Stack>

          {valores.rol === "empleado" && (
            <SelectSucursal
              label="Sucursal"
              required
              valor={valores.sucursal_id}
              alCambiar={(id) => formulario.setFieldValue("sucursal_id", id)}
              error={formulario.errors.sucursal_id}
            />
          )}

          {empleado && (
            <>
              <TextInput
                label="Id de Telegram"
                description="Para recibir los avisos del bot. En Telegram, escribile a @userinfobot y copiá el número que responde como Id."
                inputMode="numeric"
                maxLength={20}
                {...formulario.getInputProps("telegram_id")}
              />
              <Switch
                label="Activo (puede ingresar)"
                disabled={esYo}
                description={esYo ? "No podés desactivar tu propio usuario." : undefined}
                {...formulario.getInputProps("activo", { type: "checkbox" })}
              />
            </>
          )}

          {error && <Alert color="red">{error}</Alert>}
          <Group justify="flex-end" gap="xs">
            <Button variant="default" onClick={alCerrar}>
              Volver
            </Button>
            <Button type="submit" loading={enviando}>
              {empleado ? "Guardar cambios" : "Crear usuario"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
