# Vlastní beat pro díl 16 („Švihni prstem do rytmu“): 150 BPM, Am–F–C–G, kopák na každou dobu,
# k tomu zvuky švihu lopaty (na dobu) a bouchnutí ohně (o dobu později) ve scénách s kotlem.
import sys, numpy as np
from scipy.io import wavfile

SR = 44100
BPM = 150
B = 60 / BPM
BEATS = int(sys.argv[2]) if len(sys.argv) > 2 else 38
COAL = [tuple(map(int, x.split('-'))) for x in (sys.argv[3].split(',') if len(sys.argv) > 3 else [])]  # rozsahy dob s házením
OFF = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
TOTAL = OFF + BEATS * B + 2.2
N = int(TOTAL * SR)
out = np.zeros(N)
rng = np.random.default_rng(3)

def put(sig, t, vol=1.0):
    i = int((t + OFF) * SR)
    if i >= N: return
    j = min(N, i + len(sig))
    out[i:j] += sig[: j - i] * vol

def env(n, a=.002, d=.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def kick():
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 1.0

def snare():
    n = int(.25 * SR); t = np.arange(n) / SR
    return (rng.standard_normal(n) * .7 * np.exp(-t * 18) + np.sin(2 * np.pi * 190 * t) * .4 * np.exp(-t * 25))

def hat(op=False):
    n = int((.12 if op else .045) * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-t * (25 if op else 80)) * .35

def tone(freq, dur, kind='sq', vol=.3, dec=.25):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == 'sq': w = np.sign(np.sin(2 * np.pi * freq * t)) * .6 + np.sin(2 * np.pi * freq * t) * .4
    elif kind == 'saw': w = 2 * ((t * freq) % 1) - 1
    else: w = np.sin(2 * np.pi * freq * t)
    return w * env(n, .004, dec) * vol

def whoosh():
    n = int(.22 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # jednoduchý pásmový filtr rostoucí frekvencí (rozdíl dvou vyhlazení)
    k1 = np.convolve(x, np.ones(6) / 6, 'same'); k2 = np.convolve(x, np.ones(40) / 40, 'same')
    return (k1 - k2) * np.sin(np.pi * t / t[-1]) * .5

def boom():
    n = int(.5 * SR); t = np.arange(n) / SR
    f = 40 + 70 * np.exp(-t * 18)
    low = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    cr = rng.standard_normal(n) * np.exp(-t * 6) * (rng.random(n) > .985) * 1.5
    nz = np.convolve(rng.standard_normal(n), np.ones(25) / 25, 'same') * np.exp(-t * 9) * 2
    return low * .8 + cr * .4 + nz * .5

def midi(m): return 440 * 2 ** ((m - 69) / 12)

CH = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [62, 67, 71])]   # Am F C G
LEAD = [76, 0, 72, 74, 76, 79, 76, 0, 77, 0, 76, 72, 69, 0, 72, 74, 76, 0, 79, 81, 79, 76, 72, 0, 74, 0, 71, 74, 79, 0, 74, 0]

import os
MUSIC = os.environ.get('NOMUSIC') != '1'
for b in range(BEATS if MUSIC else 0):
    t = b * B
    bar, pos = divmod(b, 4)
    root, chord = CH[bar % 4]
    put(kick(), t, .9)
    if pos in (1, 3): put(snare(), t, .55)
    for k in range(4): put(hat(k == 2), t + k * B / 4, .5 if k % 2 == 0 else .3)
    # basa v osminách
    for k in range(2): put(tone(midi(root - 12), B / 2 * .9, 'saw', .22, .12), t + k * B / 2)
    # melodie v osminách (od 2. taktu)
    if b >= 4:
        for k in range(2):
            m = LEAD[(b * 2 + k) % len(LEAD)]
            if m: put(tone(midi(m), B / 2 * .95, 'sq', .1, .14), t + k * B / 2)
    # akord na začátku taktu
    if pos == 0:
        for m in chord: put(tone(midi(m), B * 3.5, 'sin', .07, 1.0), t)

for a, z in COAL:
    for b in range(a, z):
        put(whoosh(), b * B, .55)
        put(boom(), (b + 1) * B, .65)

# finále: činel a dlouhý akord
tf = BEATS * B
if MUSIC:
  pass
n = int(2 * SR); tt = np.arange(n) / SR
if MUSIC:
  put(rng.standard_normal(n) * np.exp(-tt * 2.2) * .35, tf)
  put(kick(), tf, 1.0)
  for m in [57, 64, 69, 72, 76]: put(tone(midi(m), 2.0, 'sin', .12, 1.2), tf)


out = out / np.max(np.abs(out)) * .9
fade = int(.4 * SR); out[-fade:] *= np.linspace(1, 0, fade)
wavfile.write(sys.argv[1], SR, (out * 32767).astype(np.int16))
print(f"beat {B:.4f}s, {TOTAL:.2f}s")
