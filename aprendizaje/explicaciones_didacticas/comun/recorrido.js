/*
 * Motor de recorridos paso a paso, compartido por todos los módulos.
 *
 * Cada módulo define sus pasos y una función que dibuja la escena de cada paso.
 * Este archivo solo maneja lo común: botones, teclado, número de paso y barra
 * de progreso. Así, todas las animaciones se usan igual.
 *
 * Se carga como script clásico y no como módulo ES (import/export), porque los
 * navegadores bloquean los módulos ES cuando el HTML se abre con doble clic
 * (direcciones file://).
 *
 * HTML esperado dentro de la raíz del recorrido:
 *   <p class="recorrido-numero"></p>
 *   <h3 class="recorrido-titulo"></h3>
 *   <div class="recorrido-texto"></div>
 *   <div class="recorrido-progreso"><span></span></div>
 *   <div class="recorrido-controles"></div>
 */
(function () {
  "use strict";

  /**
   * @param {HTMLElement} raiz      Contenedor del recorrido (con tabindex="0").
   * @param {Array} pasos           Lista de pasos; cada uno tiene { titulo, texto } y
   *                                los datos extra que necesite su escena.
   * @param {Function} alMostrar    alMostrar(paso, indice): dibuja la escena del paso.
   * @returns {{ cargar: Function }} cargar(nuevosPasos) reemplaza los pasos
   *                                (por ejemplo, al cambiar de escenario).
   */
  function crearRecorrido(raiz, pasos, alMostrar) {
    const numero = raiz.querySelector(".recorrido-numero");
    const titulo = raiz.querySelector(".recorrido-titulo");
    const texto = raiz.querySelector(".recorrido-texto");
    const barra = raiz.querySelector(".recorrido-progreso > span");
    const controles = raiz.querySelector(".recorrido-controles");

    const botonReiniciar = crearBoton("⟲ Reiniciar", "");
    const botonAnterior = crearBoton("← Anterior", "");
    const botonSiguiente = crearBoton("Siguiente →", "primario");
    const ayuda = document.createElement("span");
    ayuda.className = "ayuda-teclado";
    ayuda.textContent = "También con las flechas ← → del teclado";
    controles.append(botonReiniciar, botonAnterior, botonSiguiente, ayuda);

    let indice = 0;

    function mostrar(nuevoIndice) {
      indice = Math.max(0, Math.min(nuevoIndice, pasos.length - 1));
      const paso = pasos[indice];
      numero.textContent = `Paso ${indice + 1} de ${pasos.length}`;
      titulo.textContent = paso.titulo;
      texto.innerHTML = paso.texto;
      barra.style.width = `${((indice + 1) / pasos.length) * 100}%`;
      botonAnterior.disabled = indice === 0;
      botonSiguiente.disabled = indice === pasos.length - 1;
      alMostrar(paso, indice);
    }

    botonReiniciar.addEventListener("click", () => mostrar(0));
    botonAnterior.addEventListener("click", () => mostrar(indice - 1));
    botonSiguiente.addEventListener("click", () => mostrar(indice + 1));
    raiz.addEventListener("keydown", (evento) => {
      if (evento.key === "ArrowRight") mostrar(indice + 1);
      if (evento.key === "ArrowLeft") mostrar(indice - 1);
    });

    mostrar(0);

    return {
      cargar(nuevosPasos) {
        pasos = nuevosPasos;
        mostrar(0);
      },
    };
  }

  function crearBoton(etiqueta, variante) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = `boton ${variante}`.trim();
    boton.textContent = etiqueta;
    return boton;
  }

  /**
   * Conecta una fila de botones de escenario con un recorrido.
   * Cada botón lleva data-escenario="<clave>" y escenarios[clave] es su lista de pasos.
   */
  function conectarEscenarios(contenedor, escenarios, recorrido) {
    const botones = contenedor.querySelectorAll("[data-escenario]");
    botones.forEach((boton) => {
      boton.addEventListener("click", () => {
        botones.forEach((otro) => otro.setAttribute("aria-pressed", String(otro === boton)));
        recorrido.cargar(escenarios[boton.dataset.escenario]);
      });
    });
  }

  window.crearRecorrido = crearRecorrido;
  window.conectarEscenarios = conectarEscenarios;
})();
