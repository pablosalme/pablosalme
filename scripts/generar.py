#!/usr/bin/env python3
"""Genera los SVG animados del README en assets/ (tema oscuro y claro).

Uso: python3 scripts/generar.py   (desde la raíz del repo)

Solo biblioteca estándar. Las animaciones son SMIL: funcionan dentro de <img>,
que es como GitHub pinta los SVG de un README. Todo es un bucle con una única
duración por fichero, así que nada se desincroniza.
"""
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

TEMAS = {
    "dark": dict(bg="#0f141b", panel="#161d27", barra="#1c2530", borde="#2c3a4a",
                 texto="#e5ebf2", fuerte="#f4f7fa", suave="#8fa3bd", tenue="#556f8d",
                 acento="#d97757", ok="#7ec699", aviso="#e3b667", pizarra="#6f88a6"),
    "light": dict(bg="#f6f8fa", panel="#ffffff", barra="#e9eef4", borde="#cad5e2",
                  texto="#1c2530", fuerte="#0f141b", suave="#556f8d", tenue="#8fa3bd",
                  acento="#c2613f", ok="#2f8f5b", aviso="#b07d1a", pizarra="#6f88a6"),
}


def n(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def anim(attr, puntos, dur, discreta=False):
    """<animate> en bucle. puntos = [(t, valor), ...] con t entre 0 y 1."""
    puntos = sorted(puntos, key=lambda p: p[0])
    if puntos[0][0] > 0:
        puntos.insert(0, (0, puntos[0][1]))
    if not discreta and puntos[-1][0] < 1:
        puntos.append((1, puntos[-1][1]))
    kt = ";".join(n(t) for t, _ in puntos)
    vs = ";".join(str(v) if isinstance(v, str) else n(v) for _, v in puntos)
    modo = ' calcMode="discrete"' if discreta else ""
    return (f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite"{modo} '
            f'keyTimes="{kt}" values="{vs}"/>')


def mono(x, y, txt, size, fill, extra="", ancla="start", fijo=True):
    """Texto monoespaciado. Con fijo=True se clava el ancho para que no se salga con otra fuente."""
    largo = f' textLength="{n(len(txt) * size * 0.6)}" lengthAdjust="spacingAndGlyphs"' if fijo else ""
    return (f'<text x="{n(x)}" y="{n(y)}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{ancla}"{largo}{extra}>{txt}</text>')


def check(x, y, color, s=1.0):
    return (f'<path d="M{n(x)} {n(y)} l{n(4*s)} {n(4*s)} l{n(8*s)} {n(-9*s)}" fill="none" stroke="{color}" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')


# --------------------------------------------------------------------------- cabecera

def cabecera(c):
    W, H, T = 900, 320, 12
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
         '<title id="t">Pablo Salme, AI Engineer</title>',
         '<desc id="d">Un orquestador delega cuatro tareas en agentes de modelos distintos (claude, codex, opencode y grok), '
         'que trabajan en paralelo, se revisan entre sí y se integran en main.</desc>',
         '<defs>',
         f'<pattern id="g" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="{c["borde"]}" stroke-width="1"/></pattern>',
         '<linearGradient id="f" x1="0" y1="0" x2="1" y2="0"><stop offset="0.35" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.55"/></linearGradient>',
         f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask>',
         f'<clipPath id="k"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16"/></clipPath>',
         '</defs>',
         f'<g clip-path="url(#k)"><rect width="{W}" height="{H}" fill="{c["bg"]}"/>'
         f'<g mask="url(#m)"><rect width="{W}" height="{H}" fill="url(#g)"/></g></g>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="none" stroke="{c["borde"]}" stroke-width="1.5"/>']

    # bloque de texto
    o.append(mono(50, 98, "AI ENGINEER", 15, c["acento"], ' letter-spacing="4" font-weight="600"', fijo=False))
    o.append(f'<text x="47" y="172" font-family="{SANS}" font-size="64" font-weight="800" letter-spacing="-1.5" '
             f'fill="{c["fuerte"]}" textLength="372" lengthAdjust="spacingAndGlyphs">Pablo Salme</text>')
    o.append(mono(50, 216, "orquestación multiagente · MCP", 17, c["suave"]))
    o.append(mono(50, 243, "skills · hooks · evals · guardrails", 17, c["suave"]))

    # grafo
    ox, oy, ow, oh = 478, 136, 128, 48
    hijos = ["claude", "codex", "opencode", "grok"]
    hx, hw, hh = 712, 150, 40
    cys = [55, 125, 195, 265]
    fin = [0.52, 0.40, 0.60, 0.46]
    REV0, REV1, FIN = 0.70, 0.84, 0.97

    for i, cy in enumerate(cys):
        sale = 0.06 + 0.03 * i
        llega = sale + 0.08
        d = fin[i]
        ruta = f"M{ox+ow} {oy+oh/2:g} C{ox+ow+56} {oy+oh/2:g} {hx-56} {cy} {hx} {cy}"
        o.append(f'<path d="{ruta}" fill="none" stroke="{c["borde"]}" stroke-width="1.5"/>')
        o.append(
            f'<circle r="3.6" fill="{c["acento"]}" opacity="0">'
            + anim("opacity", [(0, 0), (sale, 1), (llega, 0), (d, 1), (d + 0.07, 0)], T, True)
            + anim("fill", [(0, c["acento"]), (d, c["ok"])], T, True)
            + f'<animateMotion dur="{T}s" repeatCount="indefinite" calcMode="linear" path="{ruta}" '
              f'keyTimes="0;{n(sale)};{n(llega)};{n(d)};{n(d+0.07)};1" keyPoints="0;0;1;1;0;0"/></circle>')
        y = cy - hh / 2
        o.append(f'<rect x="{hx}" y="{n(y)}" width="{hw}" height="{hh}" rx="8" fill="{c["panel"]}" stroke="{c["borde"]}" stroke-width="1.5">'
                 + anim("stroke", [(0, c["borde"]), (REV0, c["acento"]), (REV1, c["ok"]), (FIN, c["borde"])], T, True) + '</rect>')
        o.append(f'<circle cx="{hx+18}" cy="{cy}" r="4.5" fill="{c["tenue"]}">'
                 + anim("fill", [(0, c["tenue"]), (llega, c["aviso"]), (d, c["ok"]), (FIN, c["tenue"])], T, True) + '</circle>')
        o.append(mono(hx + 32, cy + 5, hijos[i], 15, c["texto"]))
        o.append(f'<g opacity="0">' + anim("opacity", [(0, 0), (d, 1), (FIN, 0)], T, True)
                 + check(hx + hw - 28, cy, c["ok"]) + '</g>')
        o.append(f'<rect x="{hx+10}" y="{n(y+hh-5)}" width="0" height="2" rx="1" fill="{c["aviso"]}">'
                 + anim("width", [(0, 0), (llega, 0), (d, hw - 20), (FIN, hw - 20), (1, 0)], T)
                 + anim("fill", [(0, c["aviso"]), (d, c["ok"])], T, True) + '</rect>')

    # revisión cruzada: conectores entre parejas de agentes
    for a, b in ((0, 1), (2, 3)):
        y1, y2 = cys[a] + hh / 2, cys[b] - hh / 2
        x = hx + hw / 2
        o.append(f'<path d="M{n(x)} {n(y1)} V{n(y2)}" stroke="{c["borde"]}" stroke-width="1.5" stroke-dasharray="3 4">'
                 + anim("stroke", [(0, c["borde"]), (REV0, c["acento"]), (REV1, c["borde"])], T, True) + '</path>')
        o.append(f'<circle cx="{n(x)}" cy="{n(y1)}" r="3" fill="{c["acento"]}" opacity="0">'
                 + anim("opacity", [(0, 0), (REV0, 1), (REV1, 0)], T, True)
                 + anim("cy", [(0, y1), (REV0, y1), (REV0 + 0.035, y2), (REV0 + 0.07, y1),
                               (REV0 + 0.105, y2), (REV1, y1)], T) + '</circle>')

    # orquestador
    o.append(f'<rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" rx="10" fill="{c["panel"]}" stroke="{c["acento"]}" stroke-width="1.8">'
             + anim("stroke", [(0, c["acento"]), (REV1, c["ok"]), (FIN, c["acento"])], T, True) + '</rect>')
    o.append(mono(ox + ow / 2, oy + oh / 2 + 5, "orquestador", 15, c["fuerte"], ancla="middle"))
    estados = [(0, 0.06, "plan"), (0.06, 0.26, "delega 4 tareas"), (0.26, REV0, "en paralelo"),
               (REV0, REV1, "revisión cruzada"), (REV1, FIN, "integrado en main")]
    for a, b, txt in estados:
        pts = [(0, 1 if a == 0 else 0)]
        if a > 0:
            pts.append((a, 1))
        pts.append((b, 0))
        color = c["ok"] if txt.startswith("integrado") else c["suave"]
        o.append(mono(ox + ow / 2, oy + oh + 24, txt, 13, color,
                      f' opacity="{pts[0][1]}"', ancla="middle").replace("</text>", anim("opacity", pts, T, True) + "</text>"))
    o.append('</svg>')
    return "\n".join(o)


# --------------------------------------------------------------------------- traza

def traza(c):
    W, T = 720, 14
    filas = [  # nombre, detalle, inicio, fin, color
        ("orquestador", "", 0.00, 1.00, None),
        ("claude", "feat/mcp-tools", 0.05, 0.50, c["acento"]),
        ("codex", "fix/hook-retry", 0.05, 0.38, c["acento"]),
        ("opencode", "docs/skill", 0.05, 0.44, c["acento"]),
        ("grok", "revisión cruzada", 0.52, 0.70, c["pizarra"]),
        ("evals", "+ guardrails", 0.72, 0.86, c["ok"]),
        ("integrar", "→ main", 0.88, 1.00, c["ok"]),
    ]
    y0, fh = 60, 40
    tx0, tx1 = 292, 652
    pie = y0 + fh * len(filas) + 6
    H = pie + 46
    t = lambda f: 0.04 + f * 0.74
    FADE0, FADE1 = 0.95, 0.985

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
         '<title id="t">Traza de una ejecución del orquestador</title>',
         '<desc id="d">El orquestador delega tres tareas en claude, codex y opencode, cada uno en su rama y su worktree. '
         'Después otro modelo revisa los cambios, pasan los evals y los guardrails y las ramas se integran en main.</desc>',
         f'<defs><clipPath id="k"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath></defs>',
         f'<g clip-path="url(#k)"><rect width="{W}" height="{H}" fill="{c["bg"]}"/><rect width="{W}" height="44" fill="{c["barra"]}"/></g>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="none" stroke="{c["borde"]}" stroke-width="1.5"/>',
         f'<path d="M1 44H{W-1}M1 {pie}H{W-1}" stroke="{c["borde"]}" stroke-width="1"/>',
         f'<circle cx="26" cy="22" r="4.5" fill="{c["ok"]}">' + anim("opacity", [(0, 1), (0.5, 0.35), (1, 1)], 2) + '</circle>',
         mono(42, 27, "traza · orquestador", 14, c["texto"]),
         mono(W - 24, 27, "3 agentes · 3 worktrees", 13, c["suave"], ancla="end")]

    # rejilla temporal
    for q in (0.25, 0.5, 0.75):
        x = tx0 + (tx1 - tx0) * q
        o.append(f'<path d="M{n(x)} {y0}V{pie-8}" stroke="{c["borde"]}" stroke-width="1" stroke-dasharray="2 5"/>')
    # árbol
    ym = lambda i: y0 + fh * i + fh / 2
    o.append(f'<path d="M30 {n(ym(0)+10)}V{n(ym(len(filas)-1))}" stroke="{c["borde"]}" stroke-width="1.5" fill="none"/>')
    for i in range(1, len(filas)):
        o.append(f'<path d="M30 {n(ym(i))}H42" stroke="{c["borde"]}" stroke-width="1.5"/>')

    o.append('<g>' + anim("opacity", [(0, 1), (FADE0, 1), (FADE1, 0), (1, 0)], T))
    for i, (nombre, det, a, b, color) in enumerate(filas):
        y = y0 + fh * i
        x = 24 if i == 0 else 50
        size = 14
        o.append(mono(x, y + 25, nombre, size, c["fuerte"] if i == 0 else c["texto"],
                      ' font-weight="600"' if i == 0 else ""))
        if det:
            o.append(mono(x + (len(nombre) + 1) * size * 0.6, y + 25, det, size, c["suave"]))
        bx, bw = tx0 + (tx1 - tx0) * a, (tx1 - tx0) * (b - a)
        o.append(f'<rect x="{n(bx)}" y="{y+13}" width="{n(bw)}" height="14" rx="3" fill="{c["barra"]}"/>')
        crece = anim("width", [(0, 0), (t(a), 0), (t(b), bw)], T)
        if color is None:
            o.append(f'<rect x="{n(bx)}" y="{y+13}" width="0" height="14" rx="3" fill="{c["tenue"]}" opacity="0.55">{crece}</rect>')
        else:
            o.append(f'<rect x="{n(bx)}" y="{y+13}" width="0" height="14" rx="3" fill="{color}">{crece}</rect>')
        o.append('<g opacity="0">' + anim("opacity", [(0, 0), (t(b), 1)], T, True)
                 + check(tx1 + 18, y + 20, c["ok"]) + '</g>')
    # cursor de tiempo
    o.append(f'<rect x="{tx0}" y="{y0+4}" width="1.5" height="{pie-y0-12}" fill="{c["acento"]}">'
             + anim("x", [(0, tx0), (t(0), tx0), (t(1), tx1)], T) + '</rect>')
    o.append('</g>')

    # línea de estado
    mensajes = [(0.0, 0.52, "3 agentes en paralelo, un worktree por agente"),
                (0.52, 0.72, "otro modelo revisa cada diff antes de integrar"),
                (0.72, 0.88, "evals y guardrails: sin verde no se integra"),
                (0.88, None, "ramas integradas en main")]
    o.append(mono(24, pie + 28, "›", 15, c["acento"], ' font-weight="700"', fijo=False))
    for a, b, txt in mensajes:
        ini = t(a) if a else 0.0
        fin = t(b) if b is not None else FADE0
        pts = [(0, 1 if ini == 0 else 0)] + ([(ini, 1)] if ini else []) + [(fin, 0)]
        o.append(mono(42, pie + 28, txt, 14, c["texto"], f' opacity="{pts[0][1]}"')
                 .replace("</text>", anim("opacity", pts, T, True) + "</text>"))
    o.append('</svg>')
    return "\n".join(o)


# --------------------------------------------------------------------------- stack

def stack(c):
    teselas = [("T3", "T3 Code", "orquestador"), ("Cc", "Claude Code", "agente"),
               ("Cx", "Codex", "agente"), ("Oc", "OpenCode", "agente"),
               ("Gk", "Grok", "agente"), ("Mcp", "MCP", "protocolo"),
               ("Sk", "Skills", "extensión"), ("Hk", "Hooks", "extensión"),
               ("Sa", "Subagentes", "paralelo"), ("Wt", "Git worktrees", "aislamiento"),
               ("Ev", "Evals", "calidad"), ("Gr", "Guardrails", "calidad")]
    cols, tw, th, gap, mx = 4, 164, 112, 12, 14
    filas = (len(teselas) + cols - 1) // cols
    W = mx * 2 + cols * tw + (cols - 1) * gap
    H = mx * 2 + filas * th + (filas - 1) * gap
    paso = 1.1
    T = round(paso * len(teselas), 2)
    alt = ", ".join(x[1] for x in teselas)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">',
         f'<title id="t">{alt}</title>']
    for i, (sim, nombre, cat) in enumerate(teselas):
        x = mx + (i % cols) * (tw + gap)
        y = mx + (i // cols) * (th + gap)
        a = i / len(teselas)
        b = (i + 1) / len(teselas)
        m = (a + b) / 2
        if i == 0:
            pulso = lambda base, alto: [(0, base), (m, alto), (b, base)]
        else:
            pulso = lambda base, alto: [(0, base), (a, base), (m, alto), (b, base)]
        o.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{c["panel"]}" stroke="{c["borde"]}" stroke-width="1.5">'
                 + anim("stroke", pulso(c["borde"], c["acento"]), T) + '</rect>')
        o.append(mono(x + 16, y + 26, f"{i+1:02d}", 12, c["tenue"]))
        o.append(mono(x + tw - 16, y + 26, cat, 12, c["suave"], ancla="end"))
        o.append(f'<text x="{x+15}" y="{y+70}" font-family="{MONO}" font-size="32" font-weight="700" fill="{c["fuerte"]}" '
                 f'textLength="{n(len(sim)*32*0.6)}" lengthAdjust="spacingAndGlyphs">{sim}'
                 + anim("fill", pulso(c["fuerte"], c["acento"]), T) + '</text>')
        o.append(f'<text x="{x+16}" y="{y+96}" font-family="{SANS}" font-size="15" font-weight="600" fill="{c["texto"]}">{nombre}</text>')
    o.append('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    for tema, c in TEMAS.items():
        for nombre, fn in (("cabecera", cabecera), ("traza", traza), ("stack", stack)):
            ruta = SALIDA / f"{nombre}-{tema}.svg"
            ruta.write_text(fn(c) + "\n", encoding="utf-8")
            print(ruta.relative_to(SALIDA.parent), ruta.stat().st_size, "bytes")
