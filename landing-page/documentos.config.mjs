// Qué documentos del repo publica la landing y cómo se clasifican.
//
// Las guías se descubren solas: cada guias/*.json con su PDF generado en la
// raíz del repo aparece en el catálogo. Este archivo solo sirve para los casos
// que la detección automática no resuelve.

// Nombre del PDF cuando no sigue la regla guias/<tema>-01.json → guia-<tema>.pdf
export const pdfPorGuia = {
  "fracciones-multiplicacion-division-01": "guia-fracciones-mult-div.pdf",
};

// Guías que no se publican (por nombre del JSON, sin extensión).
export const guiasExcluidas = ["_plantilla"];

// Documentos que no son guías. Quedan fuera por defecto:
//  - El folleto PAES es material del DEMRE con derechos reservados
//    («Prohibida su reproducción total o parcial»); la landing enlaza a demre.cl.
//  - La planificación describe el caso de una estudiante en particular.
// Para publicar alguno, cambiar "publicar" a true.
export const otrosDocumentos = [
  {
    // Documento público del DEMRE (sin restricción de reproducción); se cita la fuente.
    archivo: "temario-paes-regular-m2-admision-2027.pdf",
    publicar: true,
    titulo: "Temario PAES M2 — Admisión 2027",
    subtitulo: "Documento oficial del DEMRE para la PAES regular de fines de 2026",
    resumen: "Temario oficial de la prueba de Competencia Matemática 2. Incluye todo lo de M1 y agrega: números reales, matemática financiera y logaritmos; sistemas 2×2, funciones potencia, exponencial, logarítmica, seno y coseno; homotecia, razones trigonométricas, circunferencia, esfera y rectas en el plano; dispersión, probabilidad condicional, combinatoria y modelos binomial y normal. Son 55 preguntas en 2 horas y 20 minutos, incluidas preguntas de suficiencia de datos.",
    fecha: "19 de marzo de 2026",
    nivel: "PAES M2",
    eje: "Todos los ejes",
    tipo: "Temario oficial",
    fuente: "https://demre.cl/publicaciones/2027/2027-26-03-19-temario-paes-regular-m2",
  },
  {
    archivo: "planificacion-paes-m1.md",
    publicar: false,
    titulo: "Planificación PAES M1",
    subtitulo: "Calendario de clases, estructura de cada sesión y seguimiento",
    nivel: "PAES M1",
    eje: "Todos los ejes",
    tipo: "Planificación",
  },
  {
    archivo: "paes-regular-matematica1-p2025.pdf",
    publicar: false,
    titulo: "Folleto PAES M1 — Forma 113 (Admisión 2025)",
    subtitulo: "Prueba oficial DEMRE",
    nivel: "PAES M1",
    eje: "Todos los ejes",
    tipo: "Ensayo oficial",
  },
];

// Eje temático, deducido de palabras clave del título y el asunto.
export const ejes = [
  ["Geometría", /pit[aá]goras|geometr|área|volumen/i],
  ["Álgebra", /[aá]lgebra|ecuaci|factoriz|funci/i],
  ["Datos y azar", /estad[ií]stic|probabil/i],
  ["Números", /.*/],
];
