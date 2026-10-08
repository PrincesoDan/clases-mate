import "./style.css";
import documentos from "./documentos.json";

// Datos de contacto. Los botones solo aparecen si el campo tiene valor.
const CONTACTO = {
  email: "",      // p. ej. "nombre@correo.cl"
  whatsapp: "",   // solo dígitos con código de país, p. ej. "56912345678"
  linkedin: "https://www.linkedin.com/in/danielandradesch/",   // URL completa del perfil, p. ej. "https://www.linkedin.com/in/usuario"
};

const $ = (sel) => document.querySelector(sel);
const fmt = new Intl.NumberFormat("es-CL");

// ---------------------------------------------------------------- cifras
const totalEjercicios = documentos.reduce((n, d) => n + d.ejercicios, 0);
const niveles = [...new Set(documentos.map((d) => d.nivel))];
$("#cifras").innerHTML = [
  [documentos.length, documentos.length === 1 ? "documento" : "documentos"],
  [fmt.format(totalEjercicios), "ejercicios"],
  [niveles.length, niveles.length === 1 ? "nivel" : "niveles"],
].map(([n, t]) => `<div><dt>${n}</dt><dd>${t}</dd></div>`).join("");

// ---------------------------------------------------------------- filtros
const estado = { nivel: "Todos", eje: "Todos", texto: "" };

function chips(contenedor, clave, valores) {
  const el = $(contenedor);
  el.innerHTML = ["Todos", ...valores].map((v) =>
    `<button type="button" class="chip" data-valor="${v}" aria-pressed="${v === estado[clave]}">${v}</button>`
  ).join("");
  el.addEventListener("click", (e) => {
    const b = e.target.closest(".chip");
    if (!b) return;
    estado[clave] = b.dataset.valor;
    el.querySelectorAll(".chip").forEach((c) =>
      c.setAttribute("aria-pressed", String(c === b)));
    pintar();
  });
}

const ordenNivel = ["PAES M1", "PAES M2", "8.º básico", "Fundamentos"];
const ordenEje = ["Números", "Álgebra", "Geometría", "Datos y azar", "Todos los ejes"];
const porOrden = (orden) => (a, b) =>
  (orden.indexOf(a) + 99 * (orden.indexOf(a) < 0)) - (orden.indexOf(b) + 99 * (orden.indexOf(b) < 0));

chips("#filtro-nivel", "nivel", niveles.sort(porOrden(ordenNivel)));
chips("#filtro-eje", "eje", [...new Set(documentos.map((d) => d.eje))].sort(porOrden(ordenEje)));

const normalizar = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
$("#buscar").addEventListener("input", (e) => {
  estado.texto = normalizar(e.target.value.trim());
  pintar();
});

// ---------------------------------------------------------------- catálogo
const escapar = (s) => s.replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function tarjeta(d) {
  const extension = d.url.split(".").pop().toUpperCase();
  const archivo = d.url.split("/").pop();
  const meta = [
    d.fecha,
    d.ejercicios ? `${d.ejercicios} ejercicios` : d.tipo,
    `${extension} · ${d.kb} KB`,
  ].filter(Boolean).join(" · ");
  return `
    <article class="tarjeta" data-nivel="${escapar(d.nivel)}">
      <div class="tarjeta__etiquetas">
        <span class="etiqueta etiqueta--nivel">${escapar(d.nivel)}</span>
        <span class="etiqueta">${escapar(d.eje)}</span>
      </div>
      <h3>${escapar(d.titulo)}</h3>
      <p class="tarjeta__sub">${escapar(d.subtitulo)}</p>
      <p class="tarjeta__meta">${escapar(meta)}</p>
      ${d.resumen ? `<details><summary>Qué contiene</summary><p>${escapar(d.resumen)}</p></details>` : ""}
      <div class="tarjeta__acciones">
        <a class="boton boton--primario boton--chico" href="${d.url}" target="_blank" rel="noopener">Ver ${extension}</a>
        <a class="boton boton--chico" href="${d.url}" download="${archivo}">Descargar</a>
      </div>
      ${d.fuente ? `<a class="tarjeta__fuente" href="${d.fuente}" target="_blank" rel="noopener">Fuente: demre.cl</a>` : ""}
    </article>`;
}

function pintar() {
  const visibles = documentos.filter((d) =>
    (estado.nivel === "Todos" || d.nivel === estado.nivel) &&
    (estado.eje === "Todos" || d.eje === estado.eje) &&
    (!estado.texto || normalizar(`${d.titulo} ${d.subtitulo} ${d.resumen} ${d.eje} ${d.nivel}`).includes(estado.texto)));

  $("#conteo").textContent = visibles.length === documentos.length
    ? `${documentos.length} documentos`
    : `${visibles.length} de ${documentos.length} documentos`;
  $("#catalogo").innerHTML = visibles.length
    ? visibles.map(tarjeta).join("")
    : `<p class="vacio">No hay guías que coincidan. Prueba con otro filtro o búsqueda.</p>`;
}
pintar();

// ---------------------------------------------------------------- contacto
const acciones = [];
if (CONTACTO.whatsapp) {
  acciones.push(`<a class="boton boton--claro" href="https://wa.me/${CONTACTO.whatsapp}" target="_blank" rel="noopener">Escribir por WhatsApp</a>`);
}
if (CONTACTO.email) {
  acciones.push(`<a class="boton boton--borde-claro" href="mailto:${CONTACTO.email}?subject=Clases%20de%20matem%C3%A1ticas">Escribir un correo</a>`);
}
if (CONTACTO.linkedin) {
  acciones.push(`<a class="boton boton--borde-claro" href="${CONTACTO.linkedin}" target="_blank" rel="noopener">Ver perfil en LinkedIn</a>`);
  $("#pie-linkedin").innerHTML = `<a href="${CONTACTO.linkedin}" target="_blank" rel="noopener">LinkedIn</a>`;
}
if (acciones.length) {
  $("#contacto-acciones").innerHTML = acciones.join("");
} else {
  $("#contacto-acciones").hidden = true;
  document.querySelectorAll('a[href="#contacto"]').forEach((a) => a.remove());
  $("#contacto").hidden = true;
}

$("#anio").textContent = new Date().getFullYear();
