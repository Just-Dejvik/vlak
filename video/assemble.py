# Střih Reels podle hlasu: najde pauzy, rozloží záběry a titulky, složí mp4.
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
VOICE = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else f"{ROOT}/vlak-followeru-reel-1.mp4"
FPS = 30

# (záběr, délka natočeného klipu, věty: (mluvený text, titulek))
PLAN = [
    ("s1_follow", 7, [("Tohle je vlak followerů.", "Tohle je vlak followerů."),
                      ("Každý, kdo dá follow, nastoupí a přidá jeden vagón.", "Každý, kdo dá follow, nastoupí a přidá jeden vagón."),
                      ("Dvacet pět metrů vlaku.", "25 metrů vlaku.")]),
    ("s2_ticket", 8, [("Na webu v biu si vyzvedneš jízdenku se svým nickem.", "Na webu v biu si vyzvedneš jízdenku se svým nickem."),
                      ("Pak se podíváš do svého vagónu a uvidíš tam sám sebe.", "Pak se podíváš do svého vagónu a uvidíš tam sám sebe.")]),
    ("s3_start", 5, [("Teď stojíme v Praze a máme jediný vagón.", "Teď stojíme v Praze a máme jediný vagón.")]),
    ("s4_earth", 6, [("Cíl?", "Cíl?"), ("Vlak tak dlouhý, že obepne celou Zemi.", "Vlak tak dlouhý, že obepne celou Zemi."),
                     ("Čtyřicet tisíc kilometrů.", "40 000 kilometrů.")]),
    ("s5_vote", 8, [("A kam vyjedeme jako první, rozhodnete vy.", "A kam vyjedeme jako první, rozhodnete vy."),
                    ("Kolín, Plzeň, Ústí, nebo Tábor?", "Kolín, Plzeň, Ústí, nebo Tábor?"),
                    ("Napište to do komentářů.", "Napište to do komentářů.")]),
    ("s6_cta", 5, [("Dej follow a nastup.", "Dej follow a nastup.")]),
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

sentences = [s for _, _, ss in PLAN for s in ss]
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
for name, _, ss in PLAN:
    k += len(ss)
    bounds.append(sent_start[k] if k < len(sentences) else dur + 0.7)
bounds[-1] = max(bounds[-1], dur + 0.7)
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
        caps.append((p, t, t + d)); t += d; ci += 1

# složit: oříznout/prodloužit záběry, spojit, přidat titulky a hlas
inputs, fl = [], []
for i, (name, clip_len, _) in enumerate(PLAN):
    need = bounds[i + 1] - bounds[i]
    inputs.append(f'-i "{ROOT}/clips/{name}.mp4"')
    pad = max(0.0, need - clip_len + 0.1)
    fl.append(f"[{i}:v]tpad=stop_mode=clone:stop_duration={pad:.3f},trim=duration={need:.3f},setpts=PTS-STARTPTS,fps={FPS}[v{i}]")
n = len(PLAN)
fl.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[base]")
last = "base"
for j, (p, a, b) in enumerate(caps):
    inputs.append(f'-i "{p}"')
    idx = n + j
    fl.append(f"[{last}][{idx}:v]overlay=0:1250:enable='between(t,{a:.3f},{b:.3f})'[c{j}]")
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
