"""Recorta o logo oficial (JPG com fundo branco) em PNG com fundo transparente.

Não redesenha nada: mantém os pixels originais do logo. Só faz três coisas:
  1. encontra o círculo (ajuste por mínimos quadrados na borda azul);
  2. aplica uma máscara circular antisserrilhada (supersampling 4x), um pouco
     para dentro da borda, para eliminar o halo branco do JPG;
  3. pinta de azul da marca a faixa de ~10 px junto à borda (onde só há fundo
     azul) para matar o halo, e uniformiza o ruído de compressão no azul chapado (só pixels quase iguais
     ao azul da marca; letras, estrela e gotas não são tocadas).

Uso: python3 design/tools/extrair_logo_oficial.py
Saída: design/logo-oficial/logo.png (1024 px) e simbolo.png (256 px)
"""
from pathlib import Path

import numpy as np
from PIL import Image

PASTA = Path(__file__).resolve().parent.parent / "logo-oficial"
ORIGEM = PASTA / "logo-original.jpg"
RECUO = 1.5      # px (na escala do original) para dentro da borda
SS = 4           # supersampling da máscara


def main():
    im = Image.open(ORIGEM).convert("RGB")
    a = np.asarray(im).astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    azul = (b > 120) & (r < 80) & (b - r > 80)

    # ajuste do círculo pelas bordas esquerda/direita de cada linha
    ys = np.nonzero(azul.any(1))[0]
    pts = []
    for y in range(ys.min(), ys.max() + 1, 2):
        lin = np.nonzero(azul[y])[0]
        pts += [(lin[0] - 0.5, y), (lin[-1] + 0.5, y)]
    P = np.array(pts, float)
    A = np.c_[2 * P, np.ones(len(P))]
    cx, cy, c = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0]
    R = float(np.sqrt(c + cx * cx + cy * cy))

    # cor da marca = mediana do azul chapado
    cor = np.median(a[azul].reshape(-1, 3), 0)
    # limpa ruído de JPG no fundo azul (pixels muito próximos da cor da marca)
    dist = np.abs(a - cor).sum(-1)
    limpo = a.copy()
    limpo[dist < 30] = cor
    # anel perto da borda: só existe fundo azul ali, então troca qualquer
    # mistura com o branco do JPG (halo) pela cor da marca
    yy0, xx0 = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    rr = np.sqrt((xx0 + 0.5 - cx) ** 2 + (yy0 + 0.5 - cy) ** 2)
    limpo[(rr > R - 10) & (rr < R + 6)] = cor
    rgb = Image.fromarray(limpo.astype(np.uint8))

    # recorte quadrado centrado no círculo
    lado = int(np.ceil(2 * R)) + 4
    x0, y0 = int(round(cx - lado / 2)), int(round(cy - lado / 2))
    rgb = rgb.crop((x0, y0, x0 + lado, y0 + lado))

    # máscara circular antisserrilhada
    n = lado * SS
    yy, xx = np.mgrid[0:n, 0:n]
    ccx, ccy = (cx - x0) * SS, (cy - y0) * SS
    dentro = ((xx + 0.5 - ccx) ** 2 + (yy + 0.5 - ccy) ** 2) <= ((R - RECUO) * SS) ** 2
    mask = Image.fromarray((dentro * 255).astype(np.uint8)).resize((lado, lado), Image.LANCZOS)

    rgba = rgb.convert("RGBA")
    rgba.putalpha(mask)
    for nome, tam in (("logo.png", 1024), ("simbolo.png", 256)):
        rgba.resize((tam, tam), Image.LANCZOS).save(PASTA / nome, optimize=True)
    hexcor = "#%02X%02X%02X" % tuple(int(v) for v in cor)
    print(f"círculo: centro=({cx:.1f},{cy:.1f}) raio={R:.1f}px  cor={hexcor}")


if __name__ == "__main__":
    main()
