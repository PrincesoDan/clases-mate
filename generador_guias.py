#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de guías de ejercicios en PDF con formato académico.

La guía se define en un archivo JSON y este script la convierte en PDF,
aplicando siempre el mismo estilo de casa (tipografía con serifas, bloque de
título, resumen, secciones numeradas, encabezado, pie con paginación y
solucionario en apéndice).

Uso:
    python3 generador_guias.py guias/divisiones-01.json
    python3 generador_guias.py guias/divisiones-01.json -o /ruta/salida.pdf

Estructura del JSON (ver guias/divisiones-01.json como ejemplo):

{
  "meta":   {"titulo", "subtitulo", "autor", "cargo", "fecha", "asunto"},
  "resumen": "texto del resumen",
  "secciones": [
    {"tipo": "texto", "titulo": "...", "cuerpo": [
        {"p": "párrafo"},
        {"nota": "párrafo en cursiva"},
        {"vinetas": ["item", "item"]},
        {"formula": "expresión centrada"},
        {"figura": {...}}          # ver _figura()
    ]},
    {"tipo": "ejercicios", "titulo": "...", "columnas": ["Cociente", "Resto"],
     "bloques": [
        {"titulo": "...", "glosa": "...", "nota": "...",
         "auto": "division",
         "items": ["48 : 2", "96 : 3"]}
     ]},
    {"tipo": "solucionario", "titulo": "Apéndice A. Solucionario",
     "intro": "...", "leyenda": "Tabla A.1. ..."}
  ]
}

Notas:
  - La numeración de los ejercicios es correlativa entre bloques.
  - Con "auto": "division" el cociente, el resto y la verificación se calculan
    solos a partir de la expresión; no hay que escribir las respuestas a mano.
  - Sin "auto", cada item se escribe como
    {"e": "enunciado", "sol": ["resp1", "resp2"], "verif": "comprobación"}.
  - La sección "solucionario" recoge automáticamente todos los ejercicios
    definidos antes en el documento.
  - Un item puede llevar "fig": {...} (ver _figura) para dibujar un triángulo
    u otra figura poligonal a la derecha del enunciado.
  - Cualquier sección acepta "salto_antes": true para empezar en página nueva.
"""

import argparse
import json
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle)
from reportlab.graphics.shapes import Drawing, Line, Polygon, String
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------------------------------------------------------------------
# Estilo de casa
# ---------------------------------------------------------------------------
INK = colors.HexColor("#111111")
RULE = colors.HexColor("#222222")
SOFT = colors.HexColor("#9a9a9a")
FILLRULE = colors.HexColor("#c8c8c8")
SHADE = colors.HexColor("#f0efec")

MARGEN = 2.4 * cm


def _estilos():
    s = {}
    s["titulo"] = ParagraphStyle("titulo", fontName="Times-Bold", fontSize=19,
                                 leading=23, alignment=TA_CENTER, textColor=INK,
                                 spaceAfter=5)
    s["subtitulo"] = ParagraphStyle("subtitulo", fontName="Times-Italic",
                                    fontSize=11.5, leading=15, alignment=TA_CENTER,
                                    textColor=colors.HexColor("#444444"))
    s["autor"] = ParagraphStyle("autor", fontName="Times-Bold", fontSize=12,
                                leading=15, alignment=TA_CENTER, textColor=INK)
    s["afil"] = ParagraphStyle("afil", fontName="Times-Roman", fontSize=10.5,
                               leading=13, alignment=TA_CENTER,
                               textColor=colors.HexColor("#444444"))
    s["resumen"] = ParagraphStyle("resumen", fontName="Times-Roman", fontSize=9.6,
                                  leading=13.2, alignment=TA_JUSTIFY, textColor=INK,
                                  leftIndent=0.9 * cm, rightIndent=0.9 * cm)
    s["resumenTit"] = ParagraphStyle("resumenTit", fontName="Times-Bold",
                                     fontSize=9.6, leading=13.2, alignment=TA_CENTER,
                                     textColor=INK, spaceAfter=4)
    s["h1"] = ParagraphStyle("h1", fontName="Times-Bold", fontSize=12.5, leading=15,
                             textColor=INK, spaceBefore=13, spaceAfter=5)
    s["h2"] = ParagraphStyle("h2", fontName="Times-Bold", fontSize=11, leading=14,
                             textColor=INK, spaceBefore=10, spaceAfter=4)
    s["body"] = ParagraphStyle("body", fontName="Times-Roman", fontSize=10.3,
                               leading=14.2, alignment=TA_JUSTIFY, textColor=INK,
                               spaceAfter=5)
    s["nota"] = ParagraphStyle("nota", fontName="Times-Italic", fontSize=9.6,
                               leading=13, alignment=TA_JUSTIFY,
                               textColor=colors.HexColor("#333333"), spaceAfter=5)
    s["li"] = ParagraphStyle("li", fontName="Times-Roman", fontSize=10.3,
                             leading=14.2, alignment=TA_JUSTIFY, textColor=INK,
                             leftIndent=0.62 * cm, bulletIndent=0.15 * cm,
                             spaceAfter=4)
    s["formula"] = ParagraphStyle("formula", fontName="Times-BoldItalic",
                                  fontSize=11, leading=15, alignment=TA_CENTER,
                                  textColor=INK, spaceBefore=4, spaceAfter=7)
    s["cap"] = ParagraphStyle("cap", fontName="Times-Italic", fontSize=9.2,
                              leading=12, alignment=TA_LEFT,
                              textColor=colors.HexColor("#444444"),
                              spaceBefore=2, spaceAfter=6)
    s["th"] = ParagraphStyle("th", fontName="Times-Bold", fontSize=9.6, leading=12,
                             alignment=TA_CENTER, textColor=INK)
    s["td"] = ParagraphStyle("td", fontName="Times-Roman", fontSize=10.2,
                             leading=13, alignment=TA_CENTER, textColor=INK)
    s["tdl"] = ParagraphStyle("tdl", fontName="Times-Roman", fontSize=9.8,
                              leading=12.8, alignment=TA_LEFT, textColor=INK)
    return s


S = _estilos()


# ---------------------------------------------------------------------------
# Cálculo automático de respuestas
# ---------------------------------------------------------------------------
def _resolver_division(expr):
    """De '947 : 36' devuelve (['26', '11'], '26 × 36 + 11 = 947')."""
    partes = re.split(r"[:/÷]", expr)
    if len(partes) != 2:
        raise ValueError("No se pudo interpretar la división %r" % expr)
    a = int(partes[0].strip().replace(".", "").replace(" ", ""))
    b = int(partes[1].strip().replace(".", "").replace(" ", ""))
    if b == 0:
        raise ValueError("División por cero en %r" % expr)
    q, r = divmod(a, b)
    if r:
        verif = "%d × %d + %d = %d" % (q, b, r, a)
    else:
        verif = "%d × %d = %d" % (q, b, a)
    if q * b + r != a:  # red de seguridad
        raise AssertionError("Verificación fallida en %r" % expr)
    return [str(q), str(r)], verif


RESOLVEDORES = {"division": _resolver_division}


def _normalizar_item(item, auto):
    """Devuelve dict con claves e / sol / verif."""
    if isinstance(item, str):
        item = {"e": item}
    else:
        item = dict(item)
    if auto and "sol" not in item:
        sol, verif = RESOLVEDORES[auto](item["e"])
        item["sol"] = sol
        item.setdefault("verif", verif)
    item.setdefault("sol", [])
    item.setdefault("verif", "")
    return item



# ---------------------------------------------------------------------------
# Figuras geométricas
# ---------------------------------------------------------------------------
# Una figura se describe con coordenadas libres (se escalan solas al tamaño
# pedido), los segmentos que se dibujan y los ángulos rectos que se marcan:
#
#   {"p": {"A": [0, 0], "B": [4, 0], "C": [0, 3]},
#    "seg": [["A", "B", "4 cm"], ["B", "C", "x"], ["C", "A", "3 cm"]],
#    "recto": [["B", "A", "C"]],          # ángulo recto en A, entre AB y AC
#    "vertices": true,                    # escribe A, B, C (o una lista: solo esos)
#    "ancho": 4.2, "alto": 3.2}           # tamaño máximo, en cm
#
# Un segmento también puede ser un dict con "punteado": true (alturas,
# diagonales auxiliares) y "lado": 1 o -1 para elegir de qué lado va la
# etiqueta cuando la regla automática (alejarse del centro) no sirve.
def _figura(fig):
    import math
    pts = {k: (float(v[0]), float(v[1])) for k, v in fig["p"].items()}
    xs = [x for x, _ in pts.values()]
    ys = [y for _, y in pts.values()]
    fs = 9.5
    # El margen lateral se ajusta a la etiqueta más ancha, para que ninguna
    # quede fuera del dibujo (y se monte sobre la columna de respuesta).
    textos = [sg.get("t", "") if isinstance(sg, dict) else (sg[2] if len(sg) > 2 else "")
              for sg in fig.get("seg", [])]
    if fig.get("vertices"):
        textos += list(_vertices_visibles(fig, pts))
    ancho_txt = max([stringWidth(t, "Times-Roman", fs) for t in textos] + [0])
    mx_, my_ = 10.0 + ancho_txt, 16.0
    w_max = fig.get("ancho", 4.2) * cm - 2 * mx_
    h_max = fig.get("alto", 3.2) * cm - 2 * my_
    dx = (max(xs) - min(xs)) or 1.0
    dy = (max(ys) - min(ys)) or 1.0
    esc = min(w_max / dx, h_max / dy)
    W = dx * esc + 2 * mx_
    H = dy * esc + 2 * my_

    def T(k):
        x, y = pts[k]
        return (mx_ + (x - min(xs)) * esc, my_ + (y - min(ys)) * esc)

    cx = sum(T(k)[0] for k in pts) / len(pts)
    cy = sum(T(k)[1] for k in pts) / len(pts)
    d = Drawing(W, H)

    def etiqueta(txt, x, y, fuente="Times-Roman"):
        d.add(String(x, y - fs / 3.0, txt, fontName=fuente, fontSize=fs,
                     fillColor=INK, textAnchor="middle"))

    for seg in fig.get("seg", []):
        if isinstance(seg, dict):
            a, b, txt = seg["de"], seg["a"], seg.get("t", "")
            punteado, lado = seg.get("punteado", False), seg.get("lado")
        else:
            a, b = seg[0], seg[1]
            txt = seg[2] if len(seg) > 2 else ""
            punteado, lado = False, None
        (x1, y1), (x2, y2) = T(a), T(b)
        ln = Line(x1, y1, x2, y2, strokeColor=INK, strokeWidth=0.9)
        if punteado:
            ln.strokeDashArray = [3, 2]
            ln.strokeWidth = 0.7
        d.add(ln)
        if txt:
            mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            L = math.hypot(x2 - x1, y2 - y1) or 1.0
            nx, ny = -(y2 - y1) / L, (x2 - x1) / L
            if lado is None:
                lado = 1 if (mx - cx) * nx + (my - cy) * ny >= 0 else -1
            off = 5 + stringWidth(txt, "Times-Roman", fs) / 2.0 * abs(nx) + fs / 2.0 * abs(ny)
            etiqueta(txt, mx + lado * nx * off, my + lado * ny * off)

    for p, v, q in fig.get("recto", []):
        (vx, vy), (px, py), (qx, qy) = T(v), T(p), T(q)
        lp = math.hypot(px - vx, py - vy)
        lq = math.hypot(qx - vx, qy - vy)
        s = min(7.0, 0.22 * min(lp, lq))
        ux, uy = (px - vx) / lp * s, (py - vy) / lp * s
        wx, wy = (qx - vx) / lq * s, (qy - vy) / lq * s
        d.add(Polygon([vx, vy, vx + ux, vy + uy, vx + ux + wx, vy + uy + wy,
                       vx + wx, vy + wy], strokeColor=INK, strokeWidth=0.6,
                      fillColor=None))

    for k in _vertices_visibles(fig, pts):
        x, y = T(k)
        L = math.hypot(x - cx, y - cy) or 1.0
        ux, uy = (x - cx) / L, (y - cy) / L
        off = 6 + stringWidth(k, "Times-Italic", fs) / 2.0 * abs(ux) + fs / 2.0 * abs(uy)
        etiqueta(k, x + ux * off, y + uy * off, "Times-Italic")
    return d


def _vertices_visibles(fig, pts):
    """'vertices': true nombra todos los puntos; una lista nombra solo esos."""
    v = fig.get("vertices")
    if v is True:
        return list(pts)
    return list(v or [])


def _celda_con_figura(texto, fig, ancho, estilo):
    """Enunciado a la izquierda y figura a la derecha, dentro de una celda."""
    dib = _figura(fig)
    w_fig = max(dib.width, ancho * 0.40)
    w_txt = ancho - w_fig
    if not texto:
        t = Table([[dib]], colWidths=[ancho])
    else:
        t = Table([[Paragraph(texto, estilo), dib]], colWidths=[w_txt, w_fig])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (-1, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------
def _tabla_ejercicios(items, cols_resp, ancho, etiqueta_enunciado,
                      frac_enunciado=0.35, alineacion="centro", alto_fila=1.0):
    """Tabla en blanco para que el estudiante complete.

    frac_enunciado: ancho de la columna del enunciado, como fracción del total.
                    Conviene subirlo (0.55-0.65) cuando son problemas con texto.
    alineacion:     'centro' para expresiones breves, 'izquierda' para enunciados largos.
    alto_fila:      alto mínimo de cada fila, en cm. Si el enunciado es largo la fila
                    crece sola.
    """
    est = S["tdl"] if alineacion == "izquierda" else S["td"]
    cab = [Paragraph("N.º", S["th"]), Paragraph(etiqueta_enunciado, S["th"])]
    cab += [Paragraph(c, S["th"]) for c in cols_resp]
    data = [cab]
    w_num = 1.5 * cm
    w_enun = ancho * frac_enunciado
    for it in items:
        if it.get("fig"):
            enun = _celda_con_figura(it["e"], it["fig"], w_enun - 12, est)
        else:
            enun = Paragraph(it["e"], est)
        data.append([Paragraph(str(it["n"]), S["td"]), enun] + [""] * len(cols_resp))
    if any(it.get("fig") for it in items):
        alineacion = "izquierda"   # las filas con figura crecen solas
    w_resp = (ancho - w_num - w_enun) / max(1, len(cols_resp))
    anchos = [w_num, w_enun] + [w_resp] * len(cols_resp)

    if alineacion == "izquierda":
        # El enunciado ocupa varias lineas: la fila crece sola y el espacio para
        # escribir se consigue con relleno vertical.
        alturas = None
        relleno = 9
    else:
        alturas = [0.72 * cm] + [alto_fila * cm] * len(items)
        relleno = 3
    t = Table(data, colWidths=anchos, rowHeights=alturas)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.55, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, FILLRULE),
        ("TOPPADDING", (0, 0), (-1, -1), relleno),
        ("BOTTOMPADDING", (0, 0), (-1, -1), relleno),
    ]
    for c in range(2, 2 + len(cols_resp)):
        estilo.append(("LINEBEFORE", (c, 1), (c, -1), 0.3, FILLRULE))
    t.setStyle(TableStyle(estilo))
    return t


def _tabla_solucionario(items, cols_resp, ancho, etiqueta_enunciado, cortes):
    cab = [Paragraph("N.º", S["th"]), Paragraph(etiqueta_enunciado, S["th"])]
    cab += [Paragraph(c, S["th"]) for c in cols_resp]
    hay_verif = any(it["verif"] for it in items)
    if hay_verif:
        cab.append(Paragraph("Verificación", S["th"]))
    data = [cab]
    for it in items:
        fila = [Paragraph(str(it["n"]), S["td"]), Paragraph(it["e"], S["td"])]
        for j in range(len(cols_resp)):
            val = it["sol"][j] if j < len(it["sol"]) else ""
            fila.append(Paragraph("<b>%s</b>" % val, S["td"]))
        if hay_verif:
            fila.append(Paragraph(it["verif"], S["td"]))
        data.append(fila)

    w_num = 1.3 * cm
    if hay_verif:
        w_verif = ancho * 0.36
        w_enun = ancho * 0.23
    else:
        w_verif = 0
        w_enun = ancho * 0.35
    w_resp = (ancho - w_num - w_enun - w_verif) / max(1, len(cols_resp))
    anchos = [w_num, w_enun] + [w_resp] * len(cols_resp)
    if hay_verif:
        anchos.append(w_verif)

    t = Table(data, colWidths=anchos, repeatRows=1)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.55, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for corte in cortes:
        if 0 < corte < len(items):
            estilo.append(("LINEBELOW", (0, corte), (-1, corte), 0.3, FILLRULE))
    t.setStyle(TableStyle(estilo))
    return t


def _tabla_info(spec, ancho):
    """Tabla informativa (no rellenable) dentro de una sección de texto."""
    cab = [Paragraph(c, S["th"]) for c in spec.get("cabecera", [])]
    data = [cab] if cab else []
    for fila in spec.get("filas", []):
        data.append([Paragraph(str(c), S["td"]) for c in fila])
    n = max(len(f) for f in data)
    t = Table(data, colWidths=[ancho / n] * n)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if cab:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), SHADE),
                   ("LINEBELOW", (0, 0), (-1, 0), 0.55, RULE)]
    t.setStyle(TableStyle(estilo))
    return t


# ---------------------------------------------------------------------------
# Encabezado y pie
# ---------------------------------------------------------------------------
class _Numerado(rl_canvas.Canvas):
    encabezado = ""
    autor = ""
    cargo = ""

    def __init__(self, *a, **kw):
        rl_canvas.Canvas.__init__(self, *a, **kw)
        self._paginas = []

    def showPage(self):
        self._paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas)
        for estado in self._paginas:
            self.__dict__.update(estado)
            self._decorar(total)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _decorar(self, total):
        w, h = A4
        n = self._pageNumber
        if n > 1:
            self.setFont("Times-Italic", 8.6)
            self.setFillColor(SOFT)
            self.drawString(MARGEN, h - 1.55 * cm, self.encabezado)
            self.drawRightString(w - MARGEN, h - 1.55 * cm, self.autor)
            self.setStrokeColor(FILLRULE)
            self.setLineWidth(0.4)
            self.line(MARGEN, h - 1.75 * cm, w - MARGEN, h - 1.75 * cm)
        self.setStrokeColor(FILLRULE)
        self.setLineWidth(0.4)
        self.line(MARGEN, 1.75 * cm, w - MARGEN, 1.75 * cm)
        self.setFont("Times-Roman", 8.6)
        self.setFillColor(SOFT)
        pie = self.autor
        if self.cargo:
            pie += " · " + self.cargo
        self.drawString(MARGEN, 1.32 * cm, pie)
        self.drawRightString(w - MARGEN, 1.32 * cm, "Página %d de %d" % (n, total))


# ---------------------------------------------------------------------------
# Control de glifos
# ---------------------------------------------------------------------------
# Las fuentes Times integradas en el PDF usan codificación WinAnsi. Un carácter
# fuera de ese repertorio (flechas dobles, símbolos matemáticos poco comunes)
# no falla: se dibuja como un cuadrado negro, que pasa inadvertido hasta que la
# guía ya está impresa. Por eso se avisa antes de generar.
# \u221a (raiz) no esta en cp1252, pero reportlab la dibuja con la fuente Symbol,
# asi que no produce cuadrado negro y se admite.
_PERMITIDOS_EXTRA = set("\u2192\u00b7\u2264\u2265\u2260\u00a0\u221a")


def revisar_glifos(spec):
    """Devuelve la lista de caracteres no representables encontrados."""
    malos = {}

    def mirar(v):
        if isinstance(v, str):
            for ch in v:
                if ch in _PERMITIDOS_EXTRA:
                    continue
                try:
                    ch.encode("cp1252")
                except UnicodeEncodeError:
                    malos.setdefault(ch, 0)
                    malos[ch] += 1
        elif isinstance(v, dict):
            for x in v.values():
                mirar(x)
        elif isinstance(v, list):
            for x in v:
                mirar(x)

    mirar(spec)
    return sorted(malos.items(), key=lambda kv: -kv[1])


# ---------------------------------------------------------------------------
# Construcción del documento
# ---------------------------------------------------------------------------
def _cuerpo(bloques_cuerpo, flow, ancho=None):
    """Renderiza la lista 'cuerpo' de una sección de texto."""
    for b in bloques_cuerpo:
        if "p" in b:
            flow.append(Paragraph(b["p"], S["body"]))
        elif "nota" in b:
            flow.append(Paragraph(b["nota"], S["nota"]))
        elif "formula" in b:
            flow.append(Paragraph(b["formula"], S["formula"]))
        elif "vinetas" in b:
            for v in b["vinetas"]:
                flow.append(Paragraph(v, S["li"], bulletText="•"))
        elif "tabla" in b:
            flow.append(Spacer(1, 0.10 * cm))
            flow.append(_tabla_info(b["tabla"], ancho))
            if b["tabla"].get("leyenda"):
                flow.append(Paragraph(b["tabla"]["leyenda"], S["cap"]))
            flow.append(Spacer(1, 0.12 * cm))
        elif "figura" in b:
            fig = dict(b["figura"])
            t = Table([[_figura(fig)]])
            t.hAlign = "CENTER"
            flow.append(t)
            if fig.get("leyenda"):
                flow.append(Paragraph(fig["leyenda"], S["cap"]))
        elif "espacio" in b:
            flow.append(Spacer(1, float(b["espacio"]) * cm))


def construir(spec, salida):
    problemas = revisar_glifos(spec)
    if problemas:
        detalle = ", ".join("%r (x%d)" % (ch, n) for ch, n in problemas)
        sys.stderr.write(
            "AVISO: hay caracteres que la fuente no puede representar y saldrán "
            "como cuadrados negros en el PDF: %s\n" % detalle)

    meta = spec.get("meta", {})
    autor = meta.get("autor", "")
    cargo = meta.get("cargo", "")
    titulo = meta.get("titulo", "Guía de ejercicios")

    doc = BaseDocTemplate(
        salida, pagesize=A4,
        leftMargin=MARGEN, rightMargin=MARGEN,
        topMargin=2.2 * cm, bottomMargin=2.3 * cm,
        title=titulo, author=autor,
        subject=meta.get("asunto", ""),
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="cuerpo", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="normal", frames=[frame])])

    F = []

    # --- bloque de título
    F.append(Spacer(1, 0.15 * cm))
    F.append(Paragraph(titulo, S["titulo"]))
    if meta.get("subtitulo"):
        F.append(Paragraph(meta["subtitulo"], S["subtitulo"]))
    F.append(Spacer(1, 0.42 * cm))
    if autor:
        F.append(Paragraph(autor, S["autor"]))
    if cargo:
        F.append(Paragraph(cargo, S["afil"]))
    if meta.get("fecha"):
        F.append(Paragraph(meta["fecha"], S["afil"]))
    F.append(Spacer(1, 0.34 * cm))
    F.append(HRFlowable(width="100%", thickness=0.9, color=RULE, spaceAfter=8))

    # --- resumen
    if spec.get("resumen"):
        F.append(Paragraph("Resumen", S["resumenTit"]))
        F.append(Paragraph(spec["resumen"], S["resumen"]))
        F.append(Spacer(1, 0.18 * cm))
        F.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=4))

    # --- secciones
    todos_items = []      # para el solucionario
    cortes = []           # separadores por bloque
    cols_resp_glob = ["Respuesta"]
    etiqueta_glob = "Enunciado"
    n_sec = 0

    for sec in spec.get("secciones", []):
        if sec.get("salto_antes"):
            F.append(PageBreak())

        tipo = sec.get("tipo", "texto")

        if tipo == "solucionario":
            F.append(Paragraph(sec.get("titulo", "Apéndice A. Solucionario"), S["h1"]))
            if sec.get("intro"):
                F.append(Paragraph(sec["intro"], S["body"]))
            F.append(Spacer(1, 0.16 * cm))
            F.append(_tabla_solucionario(todos_items, cols_resp_glob, doc.width,
                                         etiqueta_glob, cortes))
            if sec.get("leyenda"):
                F.append(Paragraph(sec["leyenda"], S["cap"]))
            continue

        # Los apéndices no entran en la numeración correlativa de secciones.
        tit = sec.get("titulo", "")
        numerar = sec.get("numerar", not tit.lower().startswith("apéndice"))
        if numerar:
            n_sec += 1
            F.append(Paragraph("%d. %s" % (n_sec, tit), S["h1"]))
        else:
            F.append(Paragraph(tit, S["h1"]))

        if tipo == "texto":
            _cuerpo(sec.get("cuerpo", []), F, doc.width)

        elif tipo == "ejercicios":
            cols_resp_glob = sec.get("columnas", ["Respuesta"])
            etiqueta_glob = sec.get("etiqueta_enunciado", "Enunciado")
            if sec.get("intro"):
                F.append(Paragraph(sec["intro"], S["body"]))
            n_item = len(todos_items)
            for i, bl in enumerate(sec.get("bloques", []), start=1):
                auto = bl.get("auto")
                items = []
                for raw in bl.get("items", []):
                    n_item += 1
                    it = _normalizar_item(raw, auto)
                    it["n"] = n_item
                    items.append(it)
                todos_items.extend(items)
                cortes.append(len(todos_items))

                grupo = [Paragraph("%d.%d. %s" % (n_sec, i, bl.get("titulo", "")), S["h2"])]
                if bl.get("glosa"):
                    grupo.append(Paragraph(bl["glosa"], S["nota"]))
                if bl.get("nota"):
                    grupo.append(Paragraph(bl["nota"], S["body"]))
                grupo.append(Spacer(1, 0.12 * cm))
                grupo.append(_tabla_ejercicios(
                    items, cols_resp_glob, doc.width, etiqueta_glob,
                    frac_enunciado=bl.get("ancho_enunciado", 0.35),
                    alineacion=bl.get("alineacion", "centro"),
                    alto_fila=bl.get("alto_fila", 1.0)))
                F.append(KeepTogether(grupo))
                F.append(Spacer(1, 0.30 * cm))
            cortes = cortes[:-1] if cortes else cortes  # el último corte sobra

    _Numerado.encabezado = meta.get("encabezado", titulo)
    _Numerado.autor = autor
    _Numerado.cargo = cargo
    doc.build(F, canvasmaker=_Numerado)
    return salida


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Genera una guía de ejercicios en PDF a partir de un JSON.")
    ap.add_argument("json", help="archivo .json con la definición de la guía")
    ap.add_argument("-o", "--salida", help="ruta del PDF de salida")
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as fh:
        spec = json.load(fh)

    salida = args.salida
    if not salida:
        base = os.path.splitext(os.path.basename(args.json))[0]
        salida = os.path.join(os.path.dirname(os.path.abspath(args.json)) or ".",
                              "..", base + ".pdf")
        salida = os.path.normpath(salida)

    construir(spec, salida)
    print("PDF generado: %s" % salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
