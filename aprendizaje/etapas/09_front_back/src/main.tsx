// Punto de entrada: busca el <div id="root"> de index.html y le pide a React que dibuje <App /> adentro.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

// StrictMode solo actúa en desarrollo: ejecuta algunas cosas dos veces para detectar errores.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
