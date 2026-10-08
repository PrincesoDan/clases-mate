// Lee las guías del repo (../guias/*.json + PDFs en la raíz), copia los PDFs a
// public/docs/ y escribe src/documentos.json con lo que muestra la landing.
// Corre solo antes de `npm run dev` y `npm run build`.
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync,
         statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { ejes, guiasExcluidas, otrosDocumentos, pdfPorGuia } from "../documentos.config.mjs";

const aqui = dirname(fileURLToPath(import.meta.url));
const raiz = join(aqui, "..", "..");
const destino = join(aqui, "..", "public", "docs");

const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
               "agosto", "septiembre", "octubre", "noviembre", "diciembre"];

// "8 de octubre de 2026" → "2026-10-08" (para ordenar)
function fechaISO(texto = "") {
  const m = texto.match(/(\d{1,2}) de (\w+) de (\d{4})/i);
  if (!m) return "";
  const mes = meses.indexOf(m[2].toLowerCase()) + 1;
  return mes ? `${m[3]}-${String(mes).padStart(2, "0")}-${m[1].padStart(2, "0")}` : "";
}

const sinHtml = (s = "") =>
  s.replace(/<super>(.*?)<\/super>/g, "^$1").replace(/<[^>]+>/g, "")
   .replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").trim();

function nivelDe(asunto) {
  if (/PAES/i.test(asunto)) return "PAES M1";
  if (/b[aá]sico/i.test(asunto)) return "8.º básico";
  return "Fundamentos";
}

const ejeDe = (texto) => ejes.find(([, re]) => re.test(texto))[0];

function contarEjercicios(spec) {
  return spec.secciones
    .filter((s) => s.tipo === "ejercicios")
    .flatMap((s) => s.bloques)
    .reduce((n, b) => n + (b.items?.length ?? 0), 0);
}

rmSync(destino, { recursive: true, force: true });
mkdirSync(destino, { recursive: true });

const documentos = [];
const avisos = [];

for (const archivo of readdirSync(join(raiz, "guias")).sort()) {
  if (!archivo.endsWith(".json")) continue;
  const id = archivo.replace(/\.json$/, "");
  if (guiasExcluidas.includes(id)) continue;

  const pdf = pdfPorGuia[id] ?? `guia-${id.replace(/-\d+$/, "")}.pdf`;
  if (!existsSync(join(raiz, pdf))) {
    avisos.push(`${archivo}: no se encontró ${pdf} (¿falta generar el PDF?)`);
    continue;
  }

  const spec = JSON.parse(readFileSync(join(raiz, "guias", archivo), "utf8"));
  const meta = spec.meta ?? {};
  const asunto = meta.asunto ?? "";
  const titulo = (meta.titulo ?? id).replace(/^Guía de ejercicios:\s*/i, "");
  copyFileSync(join(raiz, pdf), join(destino, pdf));

  documentos.push({
    id,
    tipo: "Guía de ejercicios",
    titulo: titulo.charAt(0).toUpperCase() + titulo.slice(1),
    subtitulo: sinHtml(meta.subtitulo),
    resumen: sinHtml(spec.resumen),
    fecha: meta.fecha ?? "",
    orden: fechaISO(meta.fecha),
    nivel: nivelDe(asunto),
    eje: ejeDe(`${titulo} ${asunto}`),
    ejercicios: contarEjercicios(spec),
    url: `docs/${pdf}`,
    kb: Math.round(statSync(join(raiz, pdf)).size / 1024),
  });
}

for (const doc of otrosDocumentos) {
  if (!doc.publicar) continue;
  if (!existsSync(join(raiz, doc.archivo))) {
    avisos.push(`${doc.archivo}: no existe`);
    continue;
  }
  copyFileSync(join(raiz, doc.archivo), join(destino, doc.archivo));
  const { publicar, archivo, ...resto } = doc;
  documentos.push({
    id: archivo, resumen: "", fecha: "", ejercicios: 0, ...resto,
    orden: fechaISO(resto.fecha),
    url: `docs/${archivo}`,
    kb: Math.round(statSync(join(raiz, archivo)).size / 1024),
  });
}

documentos.sort((a, b) => b.orden.localeCompare(a.orden));
writeFileSync(join(aqui, "..", "src", "documentos.json"),
              JSON.stringify(documentos, null, 2) + "\n");

console.log(`sync-docs: ${documentos.length} documentos publicados en public/docs/`);
for (const a of avisos) console.warn(`sync-docs: AVISO ${a}`);
