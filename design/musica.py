#!/usr/bin/env python3
"""Trilha sonora ORIGINAL e SINCRONIZADA para os Reels da JN Higienização.

A API do Instagram não permite escolher músicas da biblioteca do app, então a
música precisa ir dentro do MP4. Para não usar obra protegida, este script
COMPÕE e sintetiza uma trilha própria (pop/house leve, clima "limpo e fresco").

Sincronia com o vídeo (o que aparece na tela manda na música):
- a música é CONTÍNUA (nunca para nem recomeça nas transições);
- andamento e grade são escolhidos para cada troca de cena cair num tempo da música;
- a intensidade (bateria, brilho do pad, arpejo) sobe e desce suavemente junto com as cenas:
  gancho (leve) → problema → solução → oferta (o ápice) → chamada final (fade);
- prato reverso suave e "whoosh" bem baixo levam até cada corte.

As trocas de cena vêm de (em ordem de preferência):
  1. --roteiro roteiro.json  (o mesmo JSON do design/reel.py; o tempo é exato)
  2. arquivo <video>.cenas.json gerado pelo reel.py ao lado do vídeo
  3. detecção automática de cortes no vídeo (ffmpeg), para qualquer vídeo

Uso:
    python3 design/musica.py --video reel.mp4 --saida final.mp4 --roteiro design/exemplos/reel-conheca.json
    python3 design/musica.py --video qualquer.mp4 --saida final.mp4          # detecta os cortes
    python3 design/musica.py --wav trilha.wav --duracao 16                   # só o áudio, sem vídeo
Opções: --estilo animado|suave, --seed N (varia tom, andamento e acordes).
"""
from __future__ import annotations

import argparse
import json

import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100

PROGRESSOES = [
    [(9, "m"), (5, "M"), (0, "M"), (7, "M")],    # vi IV I V   (começa "tenso", resolve)
    [(0, "M"), (7, "M"), (9, "m"), (5, "M")],    # I V vi IV
    [(5, "M"), (7, "M"), (9, "m"), (0, "M")],    # IV V vi I
    [(0, "M"), (9, "m"), (5, "M"), (7, "M")],    # I vi IV V
]
TONICAS = [50, 52, 48, 53, 55, 57]  # D E C F G A (MIDI na região do baixo +12)

ESTILOS = {
    "animado": {"bpm": (110, 124), "arpejo": 1.0, "hats": 1.0, "kick": 1.0},
    "suave":   {"bpm": (90, 102),  "arpejo": 0.75, "hats": 0.55, "kick": 0.7},
}

# Energia por papel de cena: (bumbo, palmas, chimbal, baixo, arpejo, oitava_extra)
PAPEIS = {
    "intro":  (0, 0, 0.4, 0.0, 0.8, 0),
    "build":  (0.5, 1, 0.7, 0.8, 0.9, 0),   # meia batida
    "full":   (1, 1, 1.0, 1.0, 1.0, 0),
    "climax": (1, 1, 1.2, 1.1, 1.15, 1),
    "outro":  (1, 1, 0.9, 1.0, 1.0, 0),
}
NOMES_PAPEL = {"gancho": "intro", "capa": "intro", "problema": "build", "solucao": "full",
               "solução": "full", "oferta": "climax", "cta": "outro"}


# ---------------------------------------------------------------- síntese básica
def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, a=0.005, d=0.1, s=0.6, r=0.05):
    e = np.full(n, s, dtype=float)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na, nd = min(na, n), min(nd, max(n - na, 0))
    e[:na] = np.linspace(0, 1, max(na, 1))[:na]
    e[na:na + nd] = np.linspace(1, s, max(nd, 1))[:nd]
    if 0 < nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw(f, n, fase=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * f + fase) % 1.0) - 1


def lp(x, fc, o=2):
    return sosfilt(butter(o, min(fc, SR / 2 - 200), "low", fs=SR, output="sos"), x)


def hp(x, fc, o=2):
    return sosfilt(butter(o, fc, "high", fs=SR, output="sos"), x)


def kick(n):
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.sin(ph) * np.exp(-t * 60)


def clap(n, rng):
    t = np.arange(n) / SR
    e = np.exp(-t * 22)
    for k in (0.010, 0.020):
        i = int(k * SR)
        e[i:] += 0.6 * np.exp(-t[:n - i] * 30)
    return hp(lp(rng.standard_normal(n), 6000), 900) * e * 0.11


def hat(n, rng, aberto=False):
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (12 if aberto else 60)) * 0.065


def whoosh(dur, rng):
    """Ruído que sobe (filtro abrindo) e cresce até o corte."""
    n = max(int(dur * SR), 1)
    x = rng.standard_normal(n)
    partes, passos = [], 24
    for k in range(passos):
        seg = x[k * n // passos:(k + 1) * n // passos]
        fc = 400 * (16 ** (k / passos))  # 400 Hz → 6,4 kHz
        partes.append(lp(hp(seg, max(fc / 3, 80)), fc))
    w = np.concatenate(partes)
    return w * np.linspace(0, 1, n) ** 2.2 * 0.22


def impacto(rng, forte=1.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t * 18)) / SR) * np.exp(-t * 3.2) * 0.55
    prato = hp(rng.standard_normal(n), 5000) * np.exp(-t * 2.4) * 0.07
    return (boom + prato) * forte


def tick(rng):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * t) * 0.5 + hp(rng.standard_normal(n), 4000) * 0.3) * np.exp(-t * 90) * 0.06


# ---------------------------------------------------------------- sincronia
def cenas_do_roteiro(roteiro: dict) -> list[dict]:
    """Mesma conta do reel.py (xfade): devolve início visível, transição e papel de cada cena."""
    padrao = roteiro.get("transicao", {"tipo": "wipeup", "duracao": 0.5})
    out, acumulado = [], 0.0
    for i, c in enumerate(roteiro["cenas"]):
        nome = c.get("dados", {}).get("cena", "")
        if i == 0:
            out.append({"inicio": 0.0, "transicao": 0.0, "nome": nome})
            acumulado = float(c["duracao"])
            continue
        t = c.get("transicao", padrao)
        td = float(padrao.get("duracao", 0.5)) if isinstance(t, str) else float(t.get("duracao", 0.5))
        offset = acumulado - td
        out.append({"inicio": round(offset + td, 3), "transicao": td, "nome": nome})
        acumulado = offset + float(c["duracao"])
    return out


def detectar_cortes(video: Path) -> list[dict]:
    """Detecta trocas de cena (inclusive wipes/slides suaves) comparando cada quadro com o de 0,4 s antes.

    Uma troca de cena muda a tela inteira e gera um pico bem maior que a animação de um texto.
    O corte é marcado no fim da transição, quando a cena nova já está na tela.
    """
    fps, lag, w, h = 30, 12, 36, 64
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)
    d = np.zeros(len(F))
    d[lag:] = np.abs(F[lag:] - F[:-lag]).mean(axis=(1, 2))
    base = 6.0
    regioes, i = [], 0
    while i < len(d):
        if d[i] > base:
            j = i
            while j < len(d) and d[j] > base:
                j += 1
            regioes.append((i, j, d[i:j].max()))
            i = j
        else:
            i += 1
    if not regioes:
        return [{"inicio": 0.0, "transicao": 0.0, "nome": ""}]
    corte = 0.45 * float(np.median([r[2] for r in regioes]))
    cenas = [{"inicio": 0.0, "transicao": 0.0, "nome": ""}]
    for i, j, pico in regioes:
        if pico < corte:
            continue  # animação de texto, não troca de cena
        fim = (j - lag) / fps
        ini = max(i / fps, 0)
        if fim > 0.5:
            cenas.append({"inicio": round(fim, 3), "transicao": round(min(max(fim - ini, 0.3), 1.0), 3), "nome": ""})
    return cenas


def papel(cena: dict, i: int, total: int) -> str:
    if cena.get("nome") in NOMES_PAPEL:
        return NOMES_PAPEL[cena["nome"]]
    if total == 1:
        return "full"
    if i == 0:
        return "intro"
    if i == total - 1:
        return "outro"
    if i == total - 2 and total >= 4:
        return "climax"
    return "build" if i == 1 else "full"


def melhor_bpm(cenas, duracao, faixa):
    """Escolhe o andamento em que cada cena dura o mais perto possível de um número inteiro de tempos."""
    limites = [c["inicio"] for c in cenas] + [duracao]
    tamanhos = np.diff(limites)
    melhor, erro_min = faixa[0], 1e9
    for bpm in np.arange(faixa[0], faixa[1] + 0.01, 0.25):
        beats = tamanhos * bpm / 60
        erro = float(np.abs(beats - np.round(beats)).sum())
        if erro < erro_min:
            melhor, erro_min = bpm, erro
    return float(melhor)


# ---------------------------------------------------------------- composição
def grade(cenas, faixa):
    """Andamento + deslocamento da grade para que os cortes caiam o mais perto possível de um tempo."""
    cortes = np.array([c["inicio"] for c in cenas[1:]]) if len(cenas) > 1 else np.array([])
    if not len(cortes):
        return float(np.mean(faixa)), 0.0
    melhor = (1e9, faixa[0], 0.0)
    for bpm in np.arange(faixa[0], faixa[1] + 0.01, 0.25):
        beat = 60 / bpm
        for off in np.linspace(0, beat, 24, endpoint=False):
            fase = ((cortes - off) / beat) % 1.0
            erro = float(np.minimum(fase, 1 - fase).sum())
            if erro < melhor[0]:
                melhor = (erro, float(bpm), float(off))
    return melhor[1], melhor[2]


def compor(duracao: float, estilo="animado", seed=1, cenas: list[dict] | None = None) -> np.ndarray:
    """Música CONTÍNUA (nunca para entre as cenas). A sincronia vem de:
    - andamento/grade escolhidos para os cortes caírem nos tempos;
    - a intensidade (bateria, brilho, arpejo) muda suavemente junto com a cena;
    - prato reverso + whoosh baixinho levando até cada corte."""
    rng = np.random.default_rng(seed)
    cfg = ESTILOS[estilo]
    cenas = cenas or [{"inicio": 0.0, "transicao": 0.0, "nome": ""}]
    prog = PROGRESSOES[seed % len(PROGRESSOES)]
    tonica = TONICAS[seed % len(TONICAS)]
    bpm, off = grade(cenas, cfg["bpm"])
    beat = 60 / bpm
    total = int((duracao + 0.05) * SR)
    L, R = np.zeros(total), np.zeros(total)
    duck = np.ones(total)

    # curva de intensidade por papel da cena, com rampas suaves de 0,6 s
    limites = [c["inicio"] for c in cenas] + [duracao]
    alvo = {"intro": 0.35, "build": 0.6, "full": 0.85, "climax": 1.0, "outro": 0.85}
    t_ax = np.arange(total) / SR
    energia = np.zeros(total)
    for ci, c in enumerate(cenas):
        a, b = int(limites[ci] * SR), int(limites[ci + 1] * SR)
        energia[a:b] = alvo[papel(c, ci, len(cenas))]
    energia[int(limites[-2] * SR) if len(limites) > 1 else 0:] = energia[min(int(limites[-2] * SR), total - 1)]
    k = int(0.6 * SR)
    energia = np.convolve(np.pad(energia, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]

    def e_em(t):
        return float(energia[min(max(int(t * SR), 0), total - 1)])

    def soma(sinal, ini, gl=1.0, gr=1.0, sofre_duck=False):
        i = int(round(ini * SR))
        if i >= total or i + len(sinal) <= 0:
            return
        if i < 0:
            sinal, i = sinal[-i:], 0
        s = sinal[: total - i]
        if sofre_duck:
            s = s * duck[i:i + len(s)]
        L[i:i + len(s)] += s * gl
        R[i:i + len(s)] += s * gr

    # grade contínua: começa um compasso antes do início para a música já entrar "andando"
    primeiro = off - 4 * beat * int(np.ceil(off / (4 * beat)) or 0)
    beats = np.arange(primeiro, duracao, beat)

    # 1) bateria (define o "pumping") — sempre presente, suave
    for n, tb in enumerate(beats):
        e = e_em(max(tb, 0))
        if tb >= 0 and e >= 0.5:
            soma(kick(int(0.45 * SR)) * 0.36 * cfg["kick"] * min(1, e + 0.1), tb)
            i, m = int(tb * SR), int(0.3 * SR)
            m = min(m, total - i)
            if m > 0:
                prof = 0.35 * e
                duck[i:i + m] = np.minimum(duck[i:i + m], (1 - prof) + prof * np.linspace(0, 1, m) ** 0.6)
        if n % 4 in (1, 3) and e >= 0.6:
            soma(clap(int(0.3 * SR), rng) * 0.7 * e, tb, 0.95, 1.0)
        for h in range(2):
            aberto = h == 1 and e >= 0.8
            soma(hat(int(0.25 * SR), rng, aberto) * cfg["hats"] * (0.45 if aberto else 0.55) * (0.4 + 0.6 * e),
                 tb + h * beat / 2 + (0.01 if h else 0), 0.8, 1.0)

    # 2) harmonia em compassos contínuos (pad longo + baixo + arpejo)
    for ci_bar, t_bar in enumerate(beats[::4]):
        grau, tipo = prog[ci_bar % len(prog)]
        raiz = tonica + grau
        notas = [raiz + 12, raiz + 12 + (3 if tipo == "m" else 4), raiz + 19]
        nbar = int(4 * beat * SR) + int(0.25 * SR)  # sobreposição leve: sem buracos entre compassos
        e = e_em(max(t_bar, 0) + 2 * beat)
        pad = sum(saw(hz(nt + d), nbar, rng.random()) for nt in notas for d in (-0.12, 0, 0.11))
        pad = lp(pad, 1000 + 1100 * e) * env(nbar, 0.25, 0.4, 0.85, 0.3) * 0.05
        soma(pad, t_bar, 1.0, 0.85, True)
        soma(np.roll(pad, int(0.012 * SR)), t_bar, 0.85, 1.0, True)
        for b in range(8):  # baixo
            tb = t_bar + b * beat / 2
            eb = e_em(max(tb, 0))
            if eb < 0.5:
                continue
            nb = int(beat / 2 * SR * 0.92)
            f = hz(raiz - 12 + (12 if b % 2 else 0))
            tt = np.arange(nb) / SR
            som = (np.sin(2 * np.pi * f * tt) + 0.2 * lp(saw(f, nb), 800)) * env(nb, 0.004, 0.08, 0.55, 0.03)
            soma(np.tanh(som * 1.3) * 0.2 * eb, tb, 1, 1, True)
        padrao = [0, 1, 2, 1, 2, 0, 2, 1] * 2
        for k2, idx in enumerate(padrao):  # arpejo
            ta0 = t_bar + k2 * beat / 4
            ea = e_em(max(ta0, 0))
            na = int(beat / 4 * SR)
            f = hz(notas[idx] + 12 + (12 if ea > 0.95 and k2 % 2 else 0))
            ta = np.arange(na) / SR
            som = (np.sin(2 * np.pi * f * ta) + 0.25 * np.sin(4 * np.pi * f * ta)) * np.exp(-ta * 13)
            pan = 0.35 if k2 % 2 else -0.35
            g = 0.085 * cfg["arpejo"] * (0.55 + 0.45 * ea)
            soma(som * g, ta0, 1 - pan, 1 + pan, True)
            soma(som * g * 0.4, ta0 + beat * 0.75, 1 + pan, 1 - pan, True)

    # 3) transições: prato reverso suave + whoosh BAIXO até o corte (sem "boom", sem parar a música)
    for c in cenas[1:]:
        corte = c["inicio"]
        td = max(c.get("transicao", 0.5), 0.35)
        n = int((td + 0.35) * SR)
        tt = np.arange(n) / SR
        rev = hp(rng.standard_normal(n), 6000) * (tt / tt[-1]) ** 3 * 0.035
        soma(rev, corte - n / SR, 0.9, 1.0)
        w = whoosh(td + 0.2, rng) * 0.22  # bem baixo
        soma(w, corte - len(w) / SR, 1.0, 0.9)

    mix = np.stack([L, R], axis=1)[: int(duracao * SR)]
    mix = hp(mix.T, 30).T
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)
    fi, fo = int(0.4 * SR), int(min(1.6, duracao / 4) * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2
    mix[-fo:] *= (np.linspace(1, 0, fo) ** 1.4)[:, None]
    return (mix / (np.abs(mix).max() or 1) * 0.89).astype(np.float32)


# ---------------------------------------------------------------- arquivos
def salvar_wav(audio, caminho: Path):
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def duracao_video(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def cenas_para(video: Path, roteiro: Path | None):
    if roteiro:
        return cenas_do_roteiro(json.loads(Path(roteiro).read_text(encoding="utf-8"))), "roteiro"
    lado = video.with_suffix(".cenas.json")
    if lado.exists():
        return json.loads(lado.read_text(encoding="utf-8")), "arquivo .cenas.json"
    return detectar_cortes(video), "detecção automática"


def aplicar(video: Path, saida: Path, estilo="animado", seed=1, roteiro: Path | None = None, volume_db=-2.0):
    dur = duracao_video(video)
    cenas, origem = cenas_para(video, roteiro)
    print(f"Sincronia por {origem}: cortes em " + ", ".join(f"{c['inicio']:.2f}s" for c in cenas[1:]))
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "trilha.wav"
        tmp_mp4 = Path(tmp) / "saida.mp4"
        salvar_wav(compor(dur, estilo, seed, cenas), wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", f"volume={volume_db}dB",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart",
                        str(tmp_mp4)], check=True)
        Path(saida).write_bytes(tmp_mp4.read_bytes())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", help="MP4 de entrada (o áudio dele é substituído)")
    ap.add_argument("--saida", help="MP4 de saída (pode ser o mesmo arquivo)")
    ap.add_argument("--roteiro", help="JSON do design/reel.py, para sincronia exata")
    ap.add_argument("--wav", help="gera só o áudio neste WAV")
    ap.add_argument("--duracao", type=float, default=16.0)
    ap.add_argument("--estilo", choices=sorted(ESTILOS), default="animado")
    ap.add_argument("--seed", type=int, default=1, help="muda tom, andamento e progressão")
    a = ap.parse_args(argv)
    if a.wav:
        cenas = cenas_do_roteiro(json.loads(Path(a.roteiro).read_text())) if a.roteiro else None
        salvar_wav(compor(a.duracao, a.estilo, a.seed, cenas), Path(a.wav))
        print(f"Trilha salva em {a.wav}")
    elif a.video and a.saida:
        aplicar(Path(a.video), Path(a.saida), a.estilo, a.seed, Path(a.roteiro) if a.roteiro else None)
        print(f"Vídeo com música sincronizada: {a.saida}")
    else:
        ap.error("use --video e --saida, ou --wav")


if __name__ == "__main__":
    main()
