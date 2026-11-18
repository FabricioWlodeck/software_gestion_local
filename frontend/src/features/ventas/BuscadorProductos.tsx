import { CloseButton, Kbd, TextInput } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";
import type { KeyboardEvent, Ref } from "react";

interface Props {
  ref: Ref<HTMLInputElement>;
  valor: string;
  alCambiar: (valor: string) => void;
  alMover: (salto: number) => void; // flechas: cambia la tarjeta resaltada
  alConfirmar: () => void; // Enter: elige la tarjeta resaltada
}

// Buscador grande del mostrador: se escribe, se filtra y Enter elige el producto.
export function BuscadorProductos({ ref, valor, alCambiar, alMover, alConfirmar }: Props) {
  function teclas(evento: KeyboardEvent<HTMLInputElement>) {
    if (evento.key === "ArrowDown") {
      evento.preventDefault();
      alMover(1);
    } else if (evento.key === "ArrowUp") {
      evento.preventDefault();
      alMover(-1);
    } else if (evento.key === "Enter") {
      evento.preventDefault();
      alConfirmar();
    } else if (evento.key === "Escape") {
      alCambiar("");
    }
  }

  return (
    <TextInput
      ref={ref}
      size="lg"
      aria-label="Buscar producto por nombre"
      placeholder="Buscá un producto: queso, jamón, yogur…"
      leftSection={<IconSearch size={22} aria-hidden />}
      rightSection={
        valor ? (
          <CloseButton aria-label="Borrar la búsqueda" onClick={() => alCambiar("")} />
        ) : (
          <Kbd size="sm" visibleFrom="sm">
            F2
          </Kbd>
        )
      }
      rightSectionWidth={52}
      value={valor}
      onChange={(evento) => alCambiar(evento.currentTarget.value)}
      onKeyDown={teclas}
      autoComplete="off"
      autoFocus
    />
  );
}
