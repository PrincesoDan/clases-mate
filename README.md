# Generador de guías de ejercicios

Convierte una guía definida en JSON en un PDF con formato académico (tipografía con
serifas, bloque de título con autor, resumen, secciones numeradas, encabezado, pie con
paginación y solucionario en apéndice).

## Instalación (una sola vez)

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## Uso

```bash
./.venv/bin/python generador_guias.py guias/divisiones-01.json -o guia-divisiones.pdf
```

Sin `-o`, el PDF se genera junto a la carpeta `guias/` con el mismo nombre del JSON.

## Crear una guía nueva

1. Copiar `guias/_plantilla.json` con un nombre nuevo.
2. Editar el contenido.
3. Ejecutar el generador.

No hay que tocar `generador_guias.py`: el estilo es siempre el mismo y vive ahí.

## Tipos de sección

| `tipo` | Para qué sirve |
|---|---|
| `texto` | Párrafos, viñetas, notas en cursiva y fórmulas centradas |
| `ejercicios` | Bloques de ejercicios con tabla para que el estudiante complete |
| `solucionario` | Tabla de respuestas; **recoge sola** todos los ejercicios del documento |

Opciones comunes a cualquier sección:

- `"salto_antes": true` — empieza en página nueva.
- `"numerar": false` — deja la sección fuera de la numeración correlativa.
  Los títulos que empiezan con «Apéndice» se detectan solos.

## Elementos de `cuerpo` (secciones de tipo `texto`)

```json
{"p": "párrafo normal"}
{"nota": "párrafo en cursiva, para glosas"}
{"vinetas": ["primer punto", "segundo punto"]}
{"formula": "expresión centrada en negrita cursiva"}
{"espacio": 0.3}
```

Dentro de cualquier texto se pueden usar `<b>negrita</b>` e `<i>cursiva</i>`.

## Respuestas automáticas

En un bloque de ejercicios, `"auto": "division"` calcula **solo** el cociente, el resto y
la verificación a partir del enunciado:

```json
{
  "titulo": "Tres dígitos por dos dígitos",
  "auto": "division",
  "items": ["187 : 15", "425 : 18"]
}
```

Esto evita el riesgo de que el solucionario se desincronice de los ejercicios: hay una sola
fuente de verdad. El generador además comprueba internamente que
`cociente × divisor + resto = dividendo` en cada ejercicio y falla si no calza.

Sin `auto`, las respuestas se escriben a mano:

```json
{"e": "2x + 6 = 14", "sol": ["x = 4"], "verif": "2 · 4 + 6 = 14"}
```

Para agregar otro cálculo automático (potencias, fracciones, ecuaciones lineales), basta con
escribir una función en `generador_guias.py` y registrarla en el diccionario `RESOLVEDORES`.

## Archivos

| Archivo | Contenido |
|---|---|
| `generador_guias.py` | Motor de generación y estilo de casa |
| `guias/_plantilla.json` | Plantilla para copiar |
| `guias/divisiones-01.json` | Guía de divisiones de dificultad progresiva |
| `guia-divisiones.pdf` | Salida generada |
| `guias/fracciones-combinadas-01.json` | Guía de operaciones combinadas con fracciones positivas y negativas (sin solucionario, con ayuda memoria) |
| `guia-fracciones-combinadas.pdf` | Salida generada |
| `guias/ecuaciones-primer-grado-01.json` | Guía de 30 ecuaciones de primer grado de dificultad progresiva (sin solucionario, con ayuda memoria) |
| `guia-ecuaciones-primer-grado.pdf` | Salida generada |
| `paes-regular-matematica1-p2025.md` | Folleto PAES Forma 113 transcrito |
| `planificacion-paes-m1.md` | Planificación de 15 clases |
