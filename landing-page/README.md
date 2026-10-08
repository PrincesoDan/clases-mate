# Landing — Clases de Matemáticas de Daniel Andrade

Página estática hecha con Vite (sin framework) que muestra el método de trabajo y
publica las guías de ejercicios de este repo.

## Uso

```bash
cd landing-page
npm install
npm run dev       # desarrollo en http://localhost:5173
npm run build     # sitio listo para publicar en dist/
npm run preview   # revisar el build
```

## De dónde salen los documentos

`scripts/sync-docs.mjs` corre solo antes de `dev` y `build`:

1. Lee cada `../guias/*.json` (título, subtítulo, fecha, resumen, cantidad de ejercicios).
2. Busca su PDF en la raíz del repo (`guias/<tema>-01.json` → `guia-<tema>.pdf`).
3. Copia los PDFs a `public/docs/` y escribe `src/documentos.json`.

Para publicar una guía nueva basta con generarla con `generador_guias.py` y volver a
hacer `npm run build`. Las excepciones (PDF con otro nombre, guías que no se publican,
documentos que no son guías) se configuran en `documentos.config.mjs`.

Quedan fuera por defecto el folleto PAES (material del DEMRE con derechos reservados)
y la planificación (describe a una estudiante en particular).

## Contacto

Los botones de contacto se configuran en `src/main.js` (`CONTACTO`). Mientras estén
vacíos, la sección de contacto no se muestra.

## Publicar

`dist/` es un sitio estático con rutas relativas: sirve en Netlify, Vercel,
GitHub Pages o cualquier hosting de archivos.
