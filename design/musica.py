#!/usr/bin/env python3
"""Trilha sonora ORIGINAL para os Reels da JN Higienização.

A API do Instagram não permite escolher músicas da biblioteca do app, então a
música precisa ir dentro do MP4. Para não usar obra protegida, este script
COMPÕE e sintetiza uma trilha própria (pop/house leve, clima "limpo e fresco"):
bateria, baixo, pad de acordes com "pumping" e um arpejo brilhante.
Nada é baixado nem copiado: tudo é gerado por código, então a JN pode usar à vontade.

Uso:
    python3 design/musica.py --video reel.mp4 --saida reel-com-musica.mp4 [--estilo animado|suave] [--seed 3]
    python3 design/musica.py --wav trilha.wav --duracao 16          # só o áudio

O vídeo sai com AAC 44,1 kHz estéreo, +faststart e fade-out no final.
Mude --seed para variar tom, andamento e progressão entre os Reels da semana.
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

# Progressões em graus (semitons a partir da tônica, tríade maior "M" ou menor "m")
PROGRESSOES = [
    [(0, "M"), (7, "M"), (9, "m"), (5, "M")],    # I  V  vi IV
    [(9, "m"), (5, "M"), (0, "M"), (7, "M")],    # vi IV I  V
    [(0, "M"), (9, "m"), (5, "M"), (7, "M")],    # I  vi IV V
    [(5, "M"), (7, "M"), (9, "m"), (0, "M")],    # IV V  vi I
]
TONICAS = {"C": 48, "D": 50, "E": 52, "F": 53, "G": 55, "A": 57}  # MIDI (oitava do baixo +12)

ESTILOS = {
    "animado": {"bpm": (112, 122), "arpejo": 1.0, "hats": 1.0, "kick": 1.0},
    "suave":   {"bpm": (92, 100),  "arpejo": 0.7, "hats": 0.5, "kick": 0.7},
}


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.05):
    t = np.arange(n) / SR
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, max(na, 1))[:len(e[:na])]
    e[na:na + nd] = np.linspace(1, s, max(nd, 1))[:len(e[na:na + nd])]
    if nr and n > nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw(f, n, fase=0.0):
    t = np.arange(n) / SR
    x = (t * f + fase) % 1.0
    return 2 * x - 1


def lp(x, fc, ordem=2):
    return sosfilt(butter(ordem, min(fc, SR / 2 - 100), "low", fs=SR, output="sos"), x)


def hp(x, fc, ordem=2):
    return sosfilt(butter(ordem, fc, "high", fs=SR, output="sos"), x)


def kick(n):
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 32)
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * np.exp(-t * 7.5) + 0.25 * np.sin(fase) * np.exp(-t * 60)


def clap(n, rng):
    t = np.arange(n) / SR
    ruido = hp(lp(rng.standard_normal(n), 6000), 900)
    e = np.exp(-t * 22)
    for atraso in (0.010, 0.020):  # "palmas" em camadas
        k = int(atraso * SR)
        e[k:] += 0.6 * np.exp(-t[:n - k] * 30)
    return ruido * e * 0.11


def hat(n, rng, aberto=False):
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (12 if aberto else 60)) * 0.065


def compor(duracao: float, estilo: str = "animado", seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    cfg = ESTILOS[estilo]
    bpm = int(rng.integers(*cfg["bpm"]))
    prog = PROGRESSOES[seed % len(PROGRESSOES)]
    tonica = list(TONICAS.values())[seed % len(TONICAS)]
    beat = 60 / bpm
    compasso = 4 * beat
    total = int((duracao + 0.1) * SR)

    L = np.zeros(total)
    R = np.zeros(total)
    sidechain = np.ones(total)

    def soma(sinal, ini, gl=1.0, gr=1.0):
        i = int(ini * SR)
        if i >= total:
            return
        s = sinal[: total - i]
        L[i:i + len(s)] += s * gl
        R[i:i + len(s)] += s * gr

    n_comp = int(np.ceil(duracao / compasso)) + 1
    intro = 1  # 1º compasso sem kick (entrada mais leve)

    for c in range(n_comp):
        t0 = c * compasso
        grau, tipo = prog[c % len(prog)]
        raiz = tonica + grau
        terça = 3 if tipo == "m" else 4
        acorde = [raiz + 12, raiz + 12 + terça, raiz + 19]

        # Pad: 3 serras desafinadas por nota, filtradas, ataque suave
        n = int(compasso * SR)
        pad = np.zeros(n)
        for nota in acorde:
            for det in (-0.12, 0.0, 0.11):
                pad += saw(hz(nota + det), n, rng.random())
        pad = lp(pad, 1800 + 600 * (c % 2)) * env_adsr(n, a=0.08, d=0.3, s=0.8, r=0.15) * 0.05
        soma(pad, t0, 1.0, 0.85)
        soma(np.roll(pad, int(0.012 * SR)), t0, 0.85, 1.0)  # largura estéreo

        # Baixo: oitavas em colcheias (sine + um pouco de serra)
        for b in range(8):
            nb = int(beat / 2 * SR * 0.92)
            f = hz(raiz - 12 + (12 if b % 2 else 0))
            tb = np.arange(nb) / SR
            som = (np.sin(2 * np.pi * f * tb) + 0.25 * lp(saw(f, nb), 900)) * env_adsr(nb, 0.003, 0.08, 0.5, 0.03)
            soma(np.tanh(som * 1.4) * 0.22, t0 + b * beat / 2)

        # Arpejo brilhante em semicolcheias (a partir do 2º compasso)
        if c >= intro and cfg["arpejo"]:
            padrao = [0, 1, 2, 1, 2, 0, 2, 1] * 2
            for k, idx in enumerate(padrao):
                na = int(beat / 4 * SR)
                f = hz(acorde[idx] + 12)
                ta = np.arange(na) / SR
                som = (np.sin(2 * np.pi * f * ta) + 0.3 * np.sin(4 * np.pi * f * ta)) * np.exp(-ta * 14)
                pan = 0.35 if k % 2 else -0.35
                soma(som * 0.11 * cfg["arpejo"], t0 + k * beat / 4, 1 - pan, 1 + pan)
                # eco (delay de colcheia pontuada)
                soma(som * 0.045 * cfg["arpejo"], t0 + k * beat / 4 + beat * 0.75, 1 + pan, 1 - pan)

        # Bateria
        for b in range(4):
            tb = t0 + b * beat
            if c >= intro:
                soma(kick(int(0.45 * SR)) * 0.5 * cfg["kick"], tb)
                i = int(tb * SR)
                m = min(int(0.32 * SR), total - i)
                if m > 0:
                    sidechain[i:i + m] = np.minimum(sidechain[i:i + m], 0.45 + 0.55 * np.linspace(0, 1, m) ** 0.6)
            if b in (1, 3):
                soma(clap(int(0.3 * SR), rng) * (0.6 if c < intro else 1.0), tb, 0.95, 1.0)
            for h in range(2):
                aberto = h == 1 and c >= intro
                soma(hat(int(0.25 * SR), rng, aberto) * cfg["hats"] * (0.5 if aberto else 0.7),
                     tb + h * beat / 2 + (0.012 if h else 0), 0.8, 1.0)

    # "Pumping": abaixa pad/arpejo/baixo quando o kick bate (sidechain aplicado no mix)
    L *= sidechain
    R *= sidechain
    # Kick por cima, sem ducking
    # (o ducking acima também atinge o kick, mas o ataque dele é instantâneo e continua presente)

    mix = np.stack([L, R], axis=1)[: int(duracao * SR)]
    mix = hp(mix.T, 30).T
    mix = np.tanh(mix * 1.6) / np.tanh(1.6)            # saturação/limitador suave
    fade_in, fade_out = int(0.05 * SR), int(1.6 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None] ** 1.5
    pico = np.abs(mix).max() or 1
    return (mix / pico * 0.89).astype(np.float32)          # ~ -1 dBFS


def salvar_wav(audio: np.ndarray, caminho: Path):
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def duracao_video(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def aplicar(video: Path, saida: Path, estilo="animado", seed=1, volume_db=-3.0):
    dur = duracao_video(video)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "trilha.wav"
        salvar_wav(compor(dur, estilo, seed), wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                        "-af", f"volume={volume_db}dB", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                        "-shortest", "-movflags", "+faststart", str(saida)], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", help="MP4 de entrada (o áudio dele é substituído)")
    ap.add_argument("--saida", help="MP4 de saída")
    ap.add_argument("--wav", help="gera só o áudio neste WAV")
    ap.add_argument("--duracao", type=float, default=16.0)
    ap.add_argument("--estilo", choices=sorted(ESTILOS), default="animado")
    ap.add_argument("--seed", type=int, default=1, help="muda tom, andamento e progressão")
    a = ap.parse_args(argv)
    if a.wav:
        salvar_wav(compor(a.duracao, a.estilo, a.seed), Path(a.wav))
        print(f"Trilha salva em {a.wav}")
    elif a.video and a.saida:
        aplicar(Path(a.video), Path(a.saida), a.estilo, a.seed)
        print(f"Vídeo com música: {a.saida}")
    else:
        ap.error("use --video e --saida, ou --wav")


if __name__ == "__main__":
    main()
