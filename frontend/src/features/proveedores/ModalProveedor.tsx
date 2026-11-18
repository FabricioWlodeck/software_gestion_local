import { Alert, Button, Group, Modal, Stack, Switch, Text, TextInput, Textarea } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";
import { api, mensajeDe } from "../../api/cliente";
import type { DatosProveedor, Proveedor } from "../../tipos";
import { avisarExito } from "../../utilidades/avisos";

interface Valores {
  nombre: string;
  telefono: string;
  email: string;
  notas: string;
  activo: boolean;
}

interface Props {
  proveedor: Proveedor | null; // null = proveedor nuevo
  alCerrar: () => void;
  alGuardar: () => void;
}

const vacioANull = (texto: string) => (texto.trim() === "" ? null : texto.trim());

// Alta y edición de proveedores (solo la dueña).
export function ModalProveedor({ proveedor, alCerrar, alGuardar }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const formulario = useForm<Valores>({
    mode: "controlled",
    initialValues: {
      nombre: proveedor?.nombre ?? "",
      telefono: proveedor?.telefono ?? "",
      email: proveedor?.email ?? "",
      notas: proveedor?.notas ?? "",
      activo: proveedor?.activo ?? true,
    },
    validate: {
      nombre: (valor) => (valor.trim() === "" ? "Escribí el nombre" : null),
      email: (valor) => (valor.trim() !== "" && !/^\S+@\S+\.\S+$/.test(valor.trim()) ? "El email no parece válido" : null),
    },
  });

  async function guardar(v: Valores) {
    setEnviando(true);
    setError(null);
    const datos: DatosProveedor = {
      nombre: v.nombre.trim(),
      telefono: vacioANull(v.telefono),
      email: vacioANull(v.email),
      notas: vacioANull(v.notas),
    };
    try {
      if (proveedor === null) {
        await api.crearProveedor(datos);
        avisarExito("Proveedor creado", datos.nombre);
      } else {
        await api.editarProveedor(proveedor.id, { ...datos, activo: v.activo });
        avisarExito("Proveedor guardado", datos.nombre);
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
          {proveedor ? `Editar ${proveedor.nombre}` : "Nuevo proveedor"}
        </Text>
      }
    >
      <form onSubmit={formulario.onSubmit(guardar)}>
        <Stack gap="md">
          <TextInput label="Nombre" required maxLength={80} data-autofocus {...formulario.getInputProps("nombre")} />
          <TextInput label="Teléfono" maxLength={40} inputMode="tel" {...formulario.getInputProps("telefono")} />
          <TextInput label="Email" maxLength={120} inputMode="email" {...formulario.getInputProps("email")} />
          <Textarea
            label="Notas"
            description="Por ejemplo, qué días entrega o con quién hablar"
            maxLength={200}
            autosize
            minRows={2}
            {...formulario.getInputProps("notas")}
          />
          {proveedor && <Switch label="Activo" {...formulario.getInputProps("activo", { type: "checkbox" })} />}
          {error && <Alert color="red">{error}</Alert>}
          <Group justify="flex-end" gap="xs">
            <Button variant="default" onClick={alCerrar}>
              Volver
            </Button>
            <Button type="submit" loading={enviando}>
              {proveedor ? "Guardar cambios" : "Crear proveedor"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
