// Tema de Mantine con los colores del logo: el verde del frasco y el amarillo del queso.
// Tipografía: Barlow para la interfaz y Barlow Condensed para precios, totales y títulos,
// como los carteles de precios del mostrador.

import {
  ActionIcon,
  Badge,
  Button,
  createTheme,
  Modal,
  NumberInput,
  SegmentedControl,
  Select,
  Table,
  TextInput,
  type MantineColorsTuple,
} from "@mantine/core";

// Verde del frasco; el tono 7 (#1F7A33) es el principal en modo claro.
const frasco: MantineColorsTuple = [
  "#eaf6ec",
  "#d3ebd7",
  "#a6d6ae",
  "#76c084",
  "#4fad61",
  "#36a04b",
  "#2a8c3d",
  "#1f7a33",
  "#186429",
  "#114e1f",
];

// Amarillo del queso; el tono 5 (#F2B705) es el del total del ticket.
const queso: MantineColorsTuple = [
  "#fff9e1",
  "#fff0b8",
  "#ffe58a",
  "#fcd95c",
  "#f6c744",
  "#f2b705",
  "#d9a300",
  "#b38600",
  "#8c6900",
  "#664c00",
];

// Grises con un toque verde, como los azulejos de la cámara de frío (reemplaza al gris azulado).
const gray: MantineColorsTuple = [
  "#f6f7f4",
  "#eef1ea",
  "#e2e6dd",
  "#d5dace",
  "#b9c0b2",
  "#9aa294",
  "#7a8475",
  "#5e6b62",
  "#434c45",
  "#2b322d",
];

export const tema = createTheme({
  primaryColor: "frasco",
  primaryShade: { light: 7, dark: 6 },
  colors: { frasco, queso, gray },
  black: "#1b2620",
  fontFamily: "Barlow, system-ui, 'Segoe UI', sans-serif",
  headings: {
    fontFamily: "'Barlow Condensed', Barlow, system-ui, sans-serif",
    fontWeight: "700",
    sizes: {
      h1: { fontSize: "2.4375rem", lineHeight: "1.1" }, // 39 px
      h2: { fontSize: "1.9375rem", lineHeight: "1.15" }, // 31 px
      h3: { fontSize: "1.5625rem", lineHeight: "1.2" }, // 25 px
      h4: { fontSize: "1.25rem", lineHeight: "1.25" }, // 20 px
    },
  },
  fontSizes: {
    xs: "0.8125rem", // 13
    sm: "0.875rem", // 14
    md: "1rem", // 16
    lg: "1.25rem", // 20
    xl: "1.5625rem", // 25
  },
  defaultRadius: "sm",
  cursorType: "pointer",
  focusRing: "auto",
  components: {
    Button: Button.extend({ defaultProps: { size: "md" } }),
    ActionIcon: ActionIcon.extend({ defaultProps: { variant: "subtle", size: "lg" } }),
    TextInput: TextInput.extend({ defaultProps: { size: "md" } }),
    NumberInput: NumberInput.extend({ defaultProps: { size: "md" } }),
    Select: Select.extend({ defaultProps: { size: "md", allowDeselect: false } }),
    SegmentedControl: SegmentedControl.extend({ defaultProps: { size: "md" } }),
    // Etiquetas en minúscula: más fáciles de leer que en mayúsculas
    Badge: Badge.extend({
      defaultProps: { variant: "light", radius: "sm", size: "md" },
      styles: { root: { textTransform: "none", fontWeight: 600 } },
    }),
    Modal: Modal.extend({ defaultProps: { radius: "md", centered: true } }),
    Table: Table.extend({ defaultProps: { verticalSpacing: "sm", highlightOnHover: true } }),
  },
});
