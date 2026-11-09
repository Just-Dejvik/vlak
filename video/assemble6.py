# Díl 3 – střih Reels podle hlasu: najde pauzy, rozloží záběry a titulky, složí mp4.
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
VOICE = sys.argv[1]
OUT = sys.argv[2]
FPS = 30

# (záběr, délka natočeného klipu, věty: (mluvený text, titulek))
PLAN = [
    ("w1_arrive", 2.7, 1640, [("Pardubice vyhrály a jsme tam!", "Pardubice vyhrály a jsme tam!")]),
    ("w2_reserve", 5.8, 1600, [("Je nás přes pět set padesát…", "Je nás přes 550…"), ("takže máme v zásobě přes čtyři sta padesát kilometrů!", "takže máme v zásobě přes 450 kilometrů!")]),
    ("w3_big", 5.9, 1360, [("Proto teď nehlasujeme o zastávce…", "Proto teď nehlasujeme o zastávce…"), ("ale o velkém cíli.", "ale o velkém cíli."), ("Vlak si cestu najde sám.", "Vlak si cestu najde sám.")]),
    ("w4_vs", 2.1, None, [("Vídeň, nebo Berlín?", "Vídeň, nebo Berlín?")]),
    ("w5_viden", 3.9, 1700, [("Do Vídně je to dvě stě devadesát kilometrů.", "Do Vídně je to 290 kilometrů."), ("Tam jsme hned.", "Tam jsme hned.")]),
    ("w6_berlin", 6.0, 1760, [("Berlín je osm set kilometrů daleko…", "Berlín je 800 kilometrů daleko…"), ("na ten potřebujeme ještě zhruba dvě stě padesát lidí.", "na ten potřebujeme ještě zhruba 250 lidí.")]),
    ("w7_rule", 4.1, 1620, [("Piš do komentářů…", "Piš do komentářů…"), ("počítají se jen hlasy lidí s jízdenkou!", "počítají se jen hlasy lidí s jízdenkou!")]),
    ("v7_outro", 5.1, 1660, [("Tak dej follow a nastup do svého vagónu přes odkaz v biu!", "Tak dej follow a nastup do svého vagónu přes odkaz v biu!")]),
]
if len(sys.argv) > 3:  # vlastní časy začátků vět v sekundách, oddělené čárkou
    MANUAL = [float(x) for x in sys.argv[3].split(",")]
else:
    MANUAL = None

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

dur = float(run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{VOICE}"').stdout.strip())
log = run(f'ffmpeg -hide_banner -i "{VOICE}" -af silencedetect=noise=-38dB:d=0.18 -f null -').stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
speech0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
speech1 = sil[-1][0] if sil and sil[-1][1] >= dur - 0.05 else dur
gaps = [(a, b) for a, b in sil if a > speech0 + 0.05 and b < speech1 - 0.05]

sentences = [s for _, _, _, ss in PLAN for s in ss]
sent_shot = [i for i, (_, _, _, ss) in enumerate(PLAN) for _ in ss]
weights = [len(s[0]) + 6 for s in sentences]  # +6 ≈ přirozená pauza za větou
tot = sum(weights)
est, acc = [], 0
for w in weights:
    est.append(speech0 + (speech1 - speech0) * acc / tot)
    acc += w
# přichytit odhad začátku věty ke konci nejbližší pauzy
used = set()
sent_start = [speech0]
for t in est[1:]:
    cands = [(abs(b - t), i, b) for i, (a, b) in enumerate(gaps) if i not in used and abs(b - t) < 1.3]
    if cands:
        _, i, b = min(cands); used.add(i); sent_start.append(b - 0.05)
    else:
        sent_start.append(t)
if MANUAL:
    sent_start = MANUAL
sent_start = sorted(sent_start)
sent_end = []
for k in range(len(sentences)):
    nxt = sent_start[k + 1] if k + 1 < len(sentences) else speech1
    # konec věty = začátek pauzy před další větou, když existuje
    pre = [a for a, b in gaps if sent_start[k] < a < nxt]
    sent_end.append(max(pre) if pre else nxt)

# hranice záběrů
bounds, k = [0.0], 0
for name, _, _, ss in PLAN:
    k += len(ss)
    bounds.append(sent_start[k] if k < len(sentences) else dur + 1.5)
bounds[-1] = max(bounds[-1], dur + 1.5)
total = bounds[-1]

# titulky: věty rozdělené na kousky po ~4 slovech
font = ImageFont.truetype(f"{ROOT}/fonts/is.ttf", 66)
try: font.set_variation_by_axes([100, 800])
except Exception: pass
caps = []
os.makedirs(f"{ROOT}/caps", exist_ok=True)
for f in os.listdir(f"{ROOT}/caps"): os.remove(f"{ROOT}/caps/{f}")
ci = 0
for k, (spoken, cap) in enumerate(sentences):
    cap_y = PLAN[sent_shot[k]][2]
    if cap_y is None: continue
    words = cap.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or (len(" ".join(cur)) > 22 and len(cur) >= 2) or w.endswith((",", "?", ".")) and len(cur) >= 2:
            chunks.append(" ".join(cur)); cur = []
    if cur:
        if chunks and len(cur) == 1 and len(cur[0]) < 6: chunks[-1] += " " + cur[0]
        else: chunks.append(" ".join(cur))
    a, b = sent_start[k], sent_end[k]
    clen = sum(len(c) + 2 for c in chunks)
    t = a
    for c in chunks:
        d = (b - a) * (len(c) + 2) / clen
        img = Image.new("RGBA", (1080, 260), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        bb = dr.textbbox((0, 0), c, font=font, stroke_width=9)
        if bb[2] - bb[0] > 960:  # dlouhý kousek zalomit na dva řádky
            ws = c.split(); h = len(ws) // 2; c = " ".join(ws[:h]) + "\n" + " ".join(ws[h:])
            bb = dr.multiline_textbbox((0, 0), c, font=font, stroke_width=9, align="center", spacing=6)
        x = (1080 - (bb[2] - bb[0])) // 2 - bb[0]; y = (260 - (bb[3] - bb[1])) // 2 - bb[1]
        dr.multiline_text((x, y), c, font=font, fill=(255, 255, 255, 255), stroke_width=9,
                          stroke_fill=(20, 32, 44, 235), align="center", spacing=6)
        p = f"{ROOT}/caps/{ci:03d}.png"; img.save(p)
        caps.append((p, t, t + d, cap_y)); t += d; ci += 1

# složit: oříznout/prodloužit záběry, spojit, přidat titulky a hlas
inputs, fl = [], []
for i, (name, clip_len, _, _) in enumerate(PLAN):
    need = bounds[i + 1] - bounds[i]
    inputs.append(f'-i "{ROOT}/clips/{name}.mp4"')
    pad = max(0.0, need - clip_len + 0.1)
    fl.append(f"[{i}:v]tpad=stop_mode=clone:stop_duration={pad:.3f},trim=duration={need:.3f},setpts=PTS-STARTPTS,fps={FPS}[v{i}]")
n = len(PLAN)
fl.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[base]")
last = "base"
for j, (p, a, b, cy) in enumerate(caps):
    inputs.append(f'-i "{p}"')
    idx = n + j
    fl.append(f"[{last}][{idx}:v]overlay=0:{cy}:enable='between(t,{a:.3f},{b:.3f})'[c{j}]")
    last = f"c{j}"
inputs.append(f'-i "{VOICE}"')
aidx = n + len(caps)
fl.append(f"[{aidx}:a]apad=whole_dur={total:.3f},afade=t=out:st={total-0.4:.3f}:d=0.4[aud]")
with open(f"{ROOT}/filter.txt", "w") as fh: fh.write(";\n".join(fl))
cmd = (f'ffmpeg -y -loglevel error {" ".join(inputs)} -filter_complex_script {ROOT}/filter.txt '
       f'-map "[{last}]" -map "[aud]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r {FPS} '
       f'-c:a aac -b:a 192k -movflags +faststart -t {total:.3f} "{OUT}"')
r = run(cmd)
print(r.stderr[-2000:])
print(json.dumps({"duration": round(total, 2), "voice": round(dur, 2), "speech": [round(speech0, 2), round(speech1, 2)],
                  "sentences": [round(x, 2) for x in sent_start], "shots": [round(x, 2) for x in bounds], "gaps": len(gaps)}, ensure_ascii=False))
