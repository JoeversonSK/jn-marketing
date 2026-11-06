#!/usr/bin/env python3
"""Gera um Reel MP4 vertical (1080x1920) a partir de uma sequência de cenas HTML.

Cada cena é um template (normalmente `reel-cena`) com animações CSS de entrada.
O script congela as animações no navegador e avança quadro a quadro (30 fps),
grava cada cena como clipe e junta tudo com transições do ffmpeg (xfade).
Saída: H.264, yuv420p, +faststart, com trilha original sincronizada (design/musica.py).
Grava também <saida>.cenas.json com os tempos das trocas de cena.
No JSON: "musica": {"estilo": "animado"|"suave", "seed": N} ou "musica": false.

Uso:
    python3 design/reel.py roteiro.json

Formato do JSON:
    {
      "saida": "/caminho/reel.mp4",
      "fps": 30,
      "transicao": {"tipo": "wipeup", "duracao": 0.5},     # padrão para todas
      "capa": {"template": "reel-cena", "dados": {"cena": "capa"}, "arquivo": "/caminho/capa.jpg"},
      "cenas": [
        {"template": "reel-cena", "duracao": 3.4, "dados": {"cena": "gancho"}},
        {"template": "reel-cena", "duracao": 3.8, "dados": {"cena": "problema"}, "transicao": "slideleft"},
        ...
      ]
    }
Transições aceitas: as do filtro xfade do ffmpeg (fade, wipeup, wipeleft, slideup,
slideleft, smoothup, circleopen, ...). A transição de uma cena é a que leva ATÉ ela.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import abrir_template, capturar, salvar  # noqa: E402

LARGURA, ALTURA = 1080, 1920


def gravar_cena(ctx, cena: dict, fps: int, destino: Path):
    dur = float(cena["duracao"])
    dados = dict(cena.get("dados", {}), duracao=dur)
    page = ctx.new_page()
    abrir_template(page, cena.get("template", "reel-cena"), dados, animar=True)
    page.evaluate("() => { window.__an = document.getAnimations(); window.__an.forEach(a => a.pause()); }")
    n = round(dur * fps)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-pix_fmt", "yuv420p", "-r", str(fps), str(destino)],
        stdin=subprocess.PIPE,
    )
    for i in range(n):
        t_ms = i * 1000.0 / fps
        page.evaluate("t => window.__an.forEach(a => { a.currentTime = t; })", t_ms)
        ff.stdin.write(page.screenshot(type="png", clip={"x": 0, "y": 0, "width": LARGURA, "height": ALTURA}))
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit(f"ffmpeg falhou na cena {destino.name}")
    page.close()
    return dur


def juntar(clipes: list[Path], duracoes: list[float], transicoes: list[tuple[str, float]], saida: Path, fps: int):
    """Encadeia os clipes com xfade. transicoes[i] liga o clipe i ao i+1."""
    entradas = []
    for c in clipes:
        entradas += ["-i", str(c)]
    if len(clipes) == 1:
        filtro, rotulo = "[0:v]null[v]", "[v]"
    else:
        partes, ant, acumulado = [], "[0:v]", duracoes[0]
        for i in range(1, len(clipes)):
            tipo, td = transicoes[i - 1]
            offset = acumulado - td
            rot = f"[x{i}]"
            partes.append(f"{ant}[{i}:v]xfade=transition={tipo}:duration={td}:offset={offset:.3f}{rot}")
            ant = rot
            acumulado = offset + duracoes[i]
        filtro, rotulo = ";".join(partes), ant
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", filtro, "-map", rotulo,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps),
           "-profile:v", "high", "-movflags", "+faststart", "-an", str(saida)]
    subprocess.run(cmd, check=True)


def duracao_video(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roteiro", help="JSON com as cenas")
    ap.add_argument("--saida", help="diretório de saída (mantém os nomes de arquivo do JSON)")
    a = ap.parse_args(argv)
    caminho = Path(a.roteiro)
    r = json.loads(caminho.read_text(encoding="utf-8"))
    fps = int(r.get("fps", 30))
    saida = Path(r["saida"])
    if a.saida:
        saida = Path(a.saida) / saida.name
        if r.get("capa", {}).get("arquivo"):
            r["capa"]["arquivo"] = str(Path(a.saida) / Path(r["capa"]["arquivo"]).name)
    if not saida.is_absolute():
        saida = (caminho.parent / saida).resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    padrao = r.get("transicao", {"tipo": "wipeup", "duracao": 0.5})

    cenas = r["cenas"]
    transicoes = []
    for c in cenas[1:]:
        t = c.get("transicao", padrao)
        if isinstance(t, str):
            t = {"tipo": t, "duracao": padrao.get("duracao", 0.5)}
        transicoes.append((t["tipo"], float(t.get("duracao", 0.5))))

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=1)
        clipes, duracoes = [], []
        for i, c in enumerate(cenas):
            destino = Path(tmp) / f"cena{i:02d}.mp4"
            print(f"cena {i + 1}/{len(cenas)}: {c.get('dados', {}).get('cena', c.get('template'))} ({c['duracao']}s)")
            duracoes.append(gravar_cena(ctx, c, fps, destino))
            clipes.append(destino)

        if r.get("capa"):
            capa = r["capa"]
            page = ctx.new_page()
            abrir_template(page, capa.get("template", "reel-cena"), capa.get("dados", {"cena": "capa"}))
            destino_capa = Path(capa.get("arquivo") or saida.with_name(saida.stem + "-capa.jpg"))
            if not destino_capa.is_absolute():
                destino_capa = (caminho.parent / destino_capa).resolve()
            salvar(capturar(page, LARGURA, ALTURA), destino_capa, 92)
            print(f"capa: {destino_capa}")
            page.close()
        nav.close()
        juntar(clipes, duracoes, transicoes, saida, fps)

    # Trocas de cena (tempos reais) ao lado do vídeo, para a música sincronizar.
    from musica import aplicar, cenas_do_roteiro  # noqa: E402
    r_real = {**r, "cenas": [{**c, "duracao": d} for c, d in zip(cenas, duracoes)]}
    marcas = cenas_do_roteiro(r_real)
    saida.with_suffix(".cenas.json").write_text(json.dumps(marcas, ensure_ascii=False, indent=2), encoding="utf-8")

    # Música original sincronizada (regra da JN: todo vídeo tem música). Desligue com "musica": false.
    m = r.get("musica", {})
    if m is not False:
        m = m if isinstance(m, dict) else {}
        aplicar(saida, saida, m.get("estilo", "animado"), int(m.get("seed", 1)))

    total = duracao_video(saida)
    print(f"reel: {saida}  ({total:.2f}s, {LARGURA}x{ALTURA}, {fps}fps, com música sincronizada)")
    if not 12 <= total <= 20:
        print(f"  ! duração fora da faixa recomendada (12–20 s): {total:.2f}s")


if __name__ == "__main__":
    main()
