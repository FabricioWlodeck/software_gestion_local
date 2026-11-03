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

  /**
   * Crea la función que dibuja un diagrama SVG con nodos y un "paquete" que viaja entre ellos.
   * - svg: elemento <svg> con nodos <g class="nodo" id="n-<nombre>"> y un <g class="paquete">
   *   que contiene un <rect> y un <text>.
   * - posiciones: { nombre: [x, y] }, el punto donde se ubica el paquete en cada lugar.
   * Cada paso puede indicar nodos { nombre: "activo" | "ok" | "error" } y
   * paquete { en: nombre, etiqueta, tipo?: "ok" | "error" }; sin paquete, se oculta.
   */
  function crearDiagrama(svg, posiciones) {
    const nodos = svg.querySelectorAll(".nodo");
    const paquete = svg.querySelector(".paquete");
    const fondo = paquete.querySelector("rect");
    const texto = paquete.querySelector("text");

    return function dibujar(paso) {
      nodos.forEach((nodo) => {
        nodo.classList.remove("activo", "ok", "error");
        const estado = (paso.nodos || {})[nodo.id.replace(/^n-/, "")];
        if (estado) nodo.classList.add(estado);
      });

      if (!paso.paquete) {
        paquete.style.opacity = "0";
        return;
      }
      paquete.style.opacity = "1";
      texto.textContent = paso.paquete.etiqueta;
      const ancho = texto.getComputedTextLength() + 28;
      fondo.setAttribute("width", ancho);
      fondo.setAttribute("x", -ancho / 2);
      paquete.classList.remove("ok", "error");
      if (paso.paquete.tipo) paquete.classList.add(paso.paquete.tipo);
      const [x, y] = posiciones[paso.paquete.en];
      paquete.style.transform = `translate(${x}px, ${y}px)`;
    };
  }

  /**
   * Escribe un código línea por línea dentro de un <code> (con número de línea)
   * y resalta las líneas indicadas; si hay alguna resaltada, las demás se atenúan.
   * primeraLinea permite mostrar un fragmento con la numeración real del archivo.
   * Pasar [0] como lineasActivas atenúa todo (sirve para mostrar código que no se ejecuta).
   */
  function escribirCodigo(elemento, texto, lineasActivas = [], primeraLinea = 1) {
    elemento.replaceChildren();
    elemento.classList.add("codigo-lineas");
    texto.split("\n").forEach((linea, i) => {
      const numero = primeraLinea + i;
      const span = document.createElement("span");
      span.className = "linea";
      if (lineasActivas.length) span.classList.add(lineasActivas.includes(numero) ? "activa" : "apagada");
      span.dataset.numero = numero;
      span.textContent = linea || " ";
      elemento.append(span);
    });

    // Si el bloque tiene altura limitada, se desplaza solo el bloque (no la página) hasta la primera línea resaltada.
    const primera = elemento.querySelector(".linea.activa");
    const contenedor = elemento.closest("pre");
    if (primera && contenedor && contenedor.scrollHeight > contenedor.clientHeight) {
      const destino = primera.getBoundingClientRect().top - contenedor.getBoundingClientRect().top + contenedor.scrollTop - 48;
      contenedor.scrollTo({ top: destino, behavior: "smooth" });
    }
  }

  /**
   * Marca como "activo" los elementos con data-clave incluidos en `claves`
   * (por ejemplo, archivos de un árbol o etapas de un proceso) y desmarca el resto.
   */
  function marcarActivos(contenedor, claves = []) {
    contenedor.querySelectorAll("[data-clave]").forEach((elemento) => {
      elemento.classList.toggle("activo", claves.includes(elemento.dataset.clave));
    });
  }

  /** Muestra el título y el código del panel de detalle de un recorrido. */
  function mostrarDetalle(raiz, detalle) {
    const contenedor = raiz.querySelector(".detalle");
    if (!detalle) {
      contenedor.hidden = true;
      return;
    }
    contenedor.hidden = false;
    contenedor.querySelector(".detalle-titulo").textContent = detalle.titulo;
    contenedor.querySelector("code").textContent = detalle.codigo;
  }

  window.crearRecorrido = crearRecorrido;
  window.conectarEscenarios = conectarEscenarios;
  window.crearDiagrama = crearDiagrama;
  window.escribirCodigo = escribirCodigo;
  window.marcarActivos = marcarActivos;
  window.mostrarDetalle = mostrarDetalle;
})();
