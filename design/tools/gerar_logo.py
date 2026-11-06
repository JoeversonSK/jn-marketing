"""Gera os arquivos de logo da JN Higienização como SVG 100% vetorial.

O texto ("JN" e "HIGIENIZAÇÃO") é convertido em contornos a partir da
Poppins Bold (licença OFL), então o SVG não depende de fonte instalada.

Uso:  python3 design/tools/gerar_logo.py
Saída: design/logo.svg, design/logo-branco.svg, design/logo-simbolo.svg
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

DESIGN = Path(__file__).resolve().parent.parent
FONTE = DESIGN / "fonts" / "Poppins-Bold.ttf"

ROYAL = "#1C3AC4"
ROYAL_CLARO = "#2C4FDB"
NOITE = "#0B1650"
AGUA = "#5EC8F2"
BRANCO = "#FFFFFF"

font = TTFont(FONTE)
gs = font.getGlyphSet()
cmap = font.getBestCmap()
UPM = font["head"].unitsPerEm
CAP = font["OS/2"].sCapHeight


def texto_em_path(texto, tamanho, x0, baseline, tracking=0.0):
    """Converte texto em um único atributo d de <path>. Retorna (d, largura)."""
    escala = tamanho / UPM
    pen = SVGPathPen(gs)
    x = 0.0
    for i, ch in enumerate(texto):
        nome = cmap[ord(ch)]
        g = gs[nome]
        # y do glifo cresce para cima; no SVG cresce para baixo
        t = TransformPen(pen, (escala, 0, 0, -escala, x0 + x, baseline))
        g.draw(t)
        x += g.width * escala
        if i < len(texto) - 1:
            x += tracking * tamanho
    return pen.getCommands(), x


def largura(texto, tamanho, tracking=0.0):
    escala = tamanho / UPM
    w = sum(gs[cmap[ord(c)]].width * escala for c in texto)
    return w + tracking * tamanho * (len(texto) - 1)


def gota(cx, topo, raio):
    """Gota d'água: ponta em (cx, topo), corpo circular de raio r."""
    cy = topo + raio * 2.15  # centro do corpo
    r = raio
    # tangentes simétricas a partir da ponta
    return (
        f"M{cx:.1f} {topo:.1f} "
        f"C{cx + r * 0.35:.1f} {topo + r * 0.75:.1f} {cx + r:.1f} {cy - r * 0.55:.1f} {cx + r:.1f} {cy:.1f} "
        f"A{r:.1f} {r:.1f} 0 1 1 {cx - r:.1f} {cy:.1f} "
        f"C{cx - r:.1f} {cy - r * 0.55:.1f} {cx - r * 0.35:.1f} {topo + r * 0.75:.1f} {cx:.1f} {topo:.1f}Z"
    )


def simbolo(ox=0.0, oy=0.0, s=1.0):
    """Símbolo circular desenhado num quadro 400x400, transladado/escalado."""
    # Letras JN
    tam = 184
    w = largura("JN", tam, tracking=-0.02)
    cap_px = CAP * tam / UPM
    base = 200 + cap_px / 2 + 6
    d_jn, _ = texto_em_path("JN", tam, 200 - w / 2 - 8, base, tracking=-0.02)
    partes = [
        f'<g transform="translate({ox} {oy}) scale({s})">',
        f'<circle cx="200" cy="200" r="200" fill="{ROYAL}"/>',
        # onda inferior (água) recortada pelo círculo
        '<clipPath id="jn-c"><circle cx="200" cy="200" r="200"/></clipPath>',
        f'<path clip-path="url(#jn-c)" fill="{ROYAL_CLARO}" '
        'd="M0 300 C70 268 130 268 200 296 C270 324 330 324 400 292 L400 400 L0 400Z"/>',
        f'<path fill="{BRANCO}" d="{d_jn}"/>',
        # gota grande + bolhas (água) no canto superior direito
        f'<path fill="{AGUA}" d="{gota(322, 44, 24)}"/>',
        f'<circle cx="352" cy="160" r="10" fill="{AGUA}"/>',
        f'<circle cx="284" cy="62" r="6" fill="{AGUA}" opacity=".85"/>',
        "</g>",
    ]
    return "\n".join(partes)


def lockup(cor_texto):
    tam = 56
    track = 0.16
    w = largura("HIGIENIZAÇÃO", tam, track)
    W = max(400, w) + 40
    x_sim = (W - 400) / 2
    cap_px = CAP * tam / UPM
    base = 400 + 56 + cap_px
    d_txt, _ = texto_em_path("HIGIENIZAÇÃO", tam, (W - w) / 2, base, track)
    H = base + 34  # espaço para o til/cedilha
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
        f'width="{W:.0f}" height="{H:.0f}" role="img" aria-label="JN Higienização">\n'
        f"{simbolo(x_sim, 0)}\n"
        f'<path fill="{cor_texto}" d="{d_txt}"/>\n</svg>\n'
    )


def main():
    (DESIGN / "logo.svg").write_text(lockup(NOITE), encoding="utf-8")
    (DESIGN / "logo-branco.svg").write_text(lockup(BRANCO), encoding="utf-8")
    (DESIGN / "logo-simbolo.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400" '
        'role="img" aria-label="JN Higienização">\n' + simbolo() + "\n</svg>\n",
        encoding="utf-8",
    )
    print("ok:", ", ".join(p.name for p in sorted(DESIGN.glob("logo*.svg"))))


if __name__ == "__main__":
    main()
