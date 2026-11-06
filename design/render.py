#!/usr/bin/env python3
"""Renderiza peças da JN Higienização a partir de um JSON de especificação.

Uso:
    python3 design/render.py especificacao.json [--saida DIR] [--png] [--estrito]

Formato do JSON (uma peça, uma lista de peças, ou {"saida": ..., "pecas": [...]}):
    {
      "saida": "/caminho/de/saida",          # opcional (padrão: ./saida)
      "pecas": [
        {
          "template": "feed-oferta",          # nome do arquivo em design/templates/ (sem .html)
          "arquivo":  "01-post.jpg",          # nome do arquivo de saída (.jpg ou .png)
          "dados":    { "titulo": "Chegamos*.*", ... },   # campos do template
          "qualidade": 92                     # opcional, JPG
        }
      ]
    }

Cada template documenta seus campos no comentário do topo do HTML. Ao final, o
script imprime avisos de layout (texto cortado, conteúdo fora da área útil,
texto na zona de interface do story). Com --estrito, avisos viram erro.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

DESIGN = Path(__file__).resolve().parent
TEMPLATES = DESIGN / "templates"
LOGO_OFICIAL = DESIGN / "logo-oficial" / "logo.png"  # gerado por tools/extrair_logo_oficial.py


def caminho_template(nome: str) -> Path:
    p = TEMPLATES / (nome if nome.endswith(".html") else f"{nome}.html")
    if not p.exists():
        disponiveis = ", ".join(sorted(x.stem for x in TEMPLATES.glob("*.html")))
        raise SystemExit(f"Template '{nome}' não existe. Disponíveis: {disponiveis}")
    return p


def abrir_template(page, template: str, dados: dict, animar: bool = False):
    """Carrega o template com os dados e espera fontes/imagens. Retorna (largura, altura)."""
    if not LOGO_OFICIAL.exists():
        raise SystemExit(f"Logo oficial não encontrado em {LOGO_OFICIAL}. Rode: python3 design/tools/extrair_logo_oficial.py")
    init = f"window.SPEC = {json.dumps(dados, ensure_ascii=False)}; window.ANIMAR = {str(animar).lower()};"
    # add_init_script acumula por página; usamos uma página nova por peça
    page.add_init_script(init)
    page.goto(caminho_template(template).as_uri())
    page.wait_for_function("window.JN_PRONTO === true", timeout=15000)
    caixa = page.eval_on_selector(".canvas", "e => [e.offsetWidth, e.offsetHeight]")
    page.set_viewport_size({"width": caixa[0], "height": caixa[1]})
    return caixa


def capturar(page, largura: int, altura: int) -> Image.Image:
    png = page.screenshot(clip={"x": 0, "y": 0, "width": largura, "height": altura}, type="png")
    return Image.open(io.BytesIO(png)).convert("RGB")


def salvar(img: Image.Image, destino: Path, qualidade: int = 92):
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.suffix.lower() in (".jpg", ".jpeg"):
        # subsampling=0 (4:4:4) mantém bordas de texto colorido nítidas
        img.save(destino, "JPEG", quality=qualidade, subsampling=0, optimize=True, progressive=True)
    else:
        img.save(destino, "PNG", optimize=True)


def normalizar(spec) -> tuple[list[dict], str | None]:
    if isinstance(spec, list):
        return spec, None
    if "pecas" in spec:
        return spec["pecas"], spec.get("saida")
    return [spec], spec.get("saida")


def renderizar(pecas: list[dict], saida: Path, png: bool = False, escala: float = 1.0) -> dict[str, list[str]]:
    relatorio: dict[str, list[str]] = {}
    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=escala)
        for peca in pecas:
            page = ctx.new_page()
            w, h = abrir_template(page, peca["template"], peca.get("dados", {}))
            avisos = page.evaluate("JN.checar()")
            img = capturar(page, w, h)
            if escala != 1:
                img = img.resize((w, h), Image.LANCZOS)
            nome = peca.get("arquivo") or f"{peca['template']}.jpg"
            if png:
                nome = str(Path(nome).with_suffix(".png"))
            destino = saida / nome
            salvar(img, destino, peca.get("qualidade", 92))
            relatorio[str(destino)] = avisos
            estado = "OK" if not avisos else f"{len(avisos)} aviso(s)"
            print(f"[{estado}] {destino}  ({w}x{h})")
            for a in avisos:
                print(f"    ! {a}")
            page.close()
        nav.close()
    return relatorio


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="arquivo JSON de especificação")
    ap.add_argument("--saida", help="diretório de saída (sobrepõe o do JSON)")
    ap.add_argument("--png", action="store_true", help="salvar PNG em vez de JPG")
    ap.add_argument("--escala", type=float, default=1.0, help="supersampling (ex.: 2 renderiza em 2x e reduz)")
    ap.add_argument("--estrito", action="store_true", help="falhar se houver avisos de layout")
    a = ap.parse_args(argv)

    spec_path = Path(a.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    pecas, saida_json = normalizar(spec)
    saida = Path(a.saida or saida_json or "saida")
    if not saida.is_absolute():
        saida = (spec_path.parent / saida).resolve()
    rel = renderizar(pecas, saida, png=a.png, escala=a.escala)
    if a.estrito and any(rel.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
