#!/usr/bin/env python3
"""Genera assets/actividad-{dark,light}.svg a partir del calendario público de contribuciones.

Uso: python3 scripts/actividad.py [usuario] [carpeta_salida]   (desde la raíz del repo)

Solo biblioteca estándar y sin token: lee https://github.com/users/<usuario>/contributions.
Si la página cambia y no se puede leer, falla sin escribir nada.
"""
import datetime
import html
import re
import sys
import urllib.request
from pathlib import Path

USUARIO = sys.argv[1] if len(sys.argv) > 1 else "pablosalme"
SALIDA = Path(sys.argv[2] if len(sys.argv) > 2 else "assets")
SEMANAS = 26

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
NARANJA = "#d97757"
TEMAS = {
    "dark": dict(niveles=["#1c2530", "#374759", "#556f8d", "#8fa3bd", "#e5ebf2"],
                 texto="#f4f7fa", suave="#a4b6ca", borde="#374759"),
    "light": dict(niveles=["#e5ebf2", "#cad5e2", "#a4b6ca", "#6f88a6", "#374759"],
                  texto="#1c2530", suave="#556f8d", borde="#cad5e2"),
}


def leer():
    req = urllib.request.Request(f"https://github.com/users/{USUARIO}/contributions",
                                 headers={"User-Agent": "Mozilla/5.0 (perfil-readme)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        pagina = r.read().decode("utf-8")
    celdas = {}
    for td in re.findall(r"<td[^>]*data-date=[^>]*>", pagina):
        fecha = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', td)
        ident = re.search(r'\bid="([^"]+)"', td)
        nivel = re.search(r'data-level="(\d)"', td)
        if fecha and ident and nivel:
            celdas[ident.group(1)] = [datetime.date.fromisoformat(fecha.group(1)), int(nivel.group(1)), 0]
    for ident, texto in re.findall(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)', pagina):
        if ident in celdas:
            n = re.match(r"\s*([\d,]+) contribution", html.unescape(texto))
            celdas[ident][2] = int(n.group(1).replace(",", "")) if n else 0
    dias = sorted(celdas.values())
    if len(dias) < 300 or sum(d[2] for d in dias) == 0 and any(d[1] for d in dias):
        sys.exit("No se ha podido leer el calendario de contribuciones")
    return dias


def rachas(dias):
    mejor = actual = 0
    for _, _, n in dias:
        actual = actual + 1 if n else 0
        mejor = max(mejor, actual)
    # la racha en curso no se rompe por un "hoy" todavía vacío
    resto = dias[:-1] if dias[-1][2] == 0 else dias
    en_curso = 0
    for _, _, n in reversed(resto):
        if not n:
            break
        en_curso += 1
    return en_curso, mejor


def miles(n):
    return f"{n:,}".replace(",", ".")


def svg(dias, tema):
    c = TEMAS[tema]
    total = sum(d[2] for d in dias)
    en_curso, mejor = rachas(dias)
    hoy = dias[-1][0]

    paso, lado, x0, y0 = 22, 18, 15, 124
    ancho = x0 * 2 + SEMANAS * paso - (paso - lado)
    alto = y0 + 7 * paso + 34
    # columnas: semanas de domingo a sábado, la última es la de hoy
    inicio = hoy - datetime.timedelta(days=(hoy.weekday() + 1) % 7 + 7 * (SEMANAS - 1))
    celdas = ""
    for fecha, nivel, _ in dias:
        if fecha < inicio:
            continue
        col = (fecha - inicio).days // 7
        fila = (fecha.weekday() + 1) % 7
        celdas += (f'<rect class="n{nivel} c{col}" x="{x0 + col * paso}" y="{y0 + fila * paso}" '
                   f'width="{lado}" height="{lado}" rx="4.5"/>')

    estilos = "".join(f".n{i}{{fill:{col}}}" for i, col in enumerate(c["niveles"]))
    estilos += ("rect[class]{animation:ola 5.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
                ".n0{animation-name:ola0}"
                "@keyframes ola{0%,24%,100%{opacity:1;transform:scale(1)}12%{opacity:.55;transform:scale(.72)}}"
                "@keyframes ola0{0%,24%,100%{opacity:1}12%{opacity:.5}}"
                "@media (prefers-reduced-motion:reduce){rect[class]{animation:none}}")
    estilos += "".join(f".c{i}{{animation-delay:{i * 0.09:.2f}s}}" for i in range(SEMANAS))

    datos = [(miles(total), "contribuciones en un año"),
             (f"{en_curso}", "días de racha" if en_curso != 1 else "día de racha"),
             (f"{mejor}", "días, la racha más larga")]
    tercio = (ancho - 2 * x0) / 3
    bloques = ""
    for i, (num, etiqueta) in enumerate(datos):
        cx = x0 + tercio * i + tercio / 2
        color = NARANJA if i == 1 else c["texto"]
        bloques += (f'<text x="{cx:.1f}" y="58" text-anchor="middle" font-family="{SANS}" font-size="42" '
                    f'font-weight="800" fill="{color}">{num}</text>'
                    f'<text x="{cx:.1f}" y="86" text-anchor="middle" font-family="{SANS}" font-size="15" '
                    f'fill="{c["suave"]}">{etiqueta}</text>')
        if i:
            x = x0 + tercio * i
            bloques += f'<path d="M{x:.1f} 26 V92" stroke="{c["borde"]}" stroke-width="1.5"/>'

    barrido = (f'<rect x="0" y="{y0 - 6}" width="3" height="{7 * paso + 8}" rx="1.5" fill="{NARANJA}" opacity="0.8">'
               f'<animate attributeName="x" from="{x0 - 6}" to="{ancho - x0 + 3}" dur="5.2s" repeatCount="indefinite"/>'
               f'</rect>')
    resumen = (f"{miles(total)} contribuciones en un año, {en_curso} días de racha "
               f"y {mejor} días la racha más larga. Dato del {hoy.isoformat()}.")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" role="img" aria-labelledby="t d">
<title id="t">Actividad en GitHub</title>
<desc id="d">{resumen}</desc>
<style>{estilos}</style>
{bloques}
{celdas}
{barrido}
<text x="{ancho / 2:.1f}" y="{alto - 8}" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{c["suave"]}">Últimas {SEMANAS} semanas · {hoy.isoformat()}</text>
</svg>
'''


def main():
    dias = leer()
    SALIDA.mkdir(parents=True, exist_ok=True)
    for tema in TEMAS:
        (SALIDA / f"actividad-{tema}.svg").write_text(svg(dias, tema), encoding="utf-8")
    en_curso, mejor = rachas(dias)
    print(f"{len(dias)} días, {sum(d[2] for d in dias)} contribuciones, racha {en_curso}, mejor {mejor}")


if __name__ == "__main__":
    main()
