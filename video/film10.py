# Díl 10: „Vyhrála Paříž!“ Do Paříže chybí ~650 cestujících + podpora (hvězdička pro podporovatele).
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 1311          # vagóny teď
PEAK = 1478       # rekord = kilometry
NEED = 2124       # km do Paříže
MISS = NEED - PEAK
VOTES = 35
SUP = 77          # ukázkový vagón podporovatele (smyšlený nick)
ROUTE = ['praha', 'kolin', 'pardubice', 'hradec', 'liberec', 'vratislav', 'poznan', 'berlin', 'hannover', 'koln_r', 'brusel', 'lille', 'pariz']

EXTRA = r"""
.cities{position:absolute;left:60px;right:60px;top:1260px;display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.cities span{background:#fff;border-radius:999px;padding:14px 26px;font:800 48px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 10px 24px rgba(0,0,0,.18);opacity:0;transform:scale(.4)}
.cities span.end{background:#ffd23f}
.bigkm{position:absolute;left:0;right:0;top:1480px;text-align:center;font:900 150px/1 BS,sans-serif;color:#fff;text-shadow:0 8px 0 rgba(20,40,60,.35);opacity:0}
.miss{position:absolute;left:0;right:0;top:1250px;text-align:center}
.miss .k{font:600 40px PM,monospace;letter-spacing:.16em;text-transform:uppercase;color:#1e2a33}
.miss .n{font:900 230px/1 BS,sans-serif;color:#cf4630;text-shadow:0 8px 0 rgba(120,30,20,.25)}
.miss .u{font:800 56px/1 IS,sans-serif;color:#1e2a33}
.plus{position:absolute;font:900 90px/1 BS,sans-serif;color:#ffd23f;text-shadow:0 6px 0 rgba(20,40,60,.4);opacity:0}
.webbtn{position:absolute;left:50%;top:1280px;transform:translateX(-50%) scale(0);background:#fff;border-radius:30px;padding:26px 44px;box-shadow:0 18px 40px rgba(0,0,0,.3);display:flex;gap:22px;align-items:center;font:800 64px/1 IS,sans-serif;color:#c2410c;white-space:nowrap}
.tap{position:absolute;width:120px;height:120px;border-radius:50%;border:10px solid #fff;opacity:0}
.share{position:absolute;left:0;right:0;top:1300px;text-align:center}
.share span{display:inline-block;background:#fff;border-radius:999px;padding:22px 40px;font:800 58px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)}
"""

STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=['tvuj.nick'];renderHud()}"
         % (N, PEAK, json.dumps(ROUTE)))
MAP = film7.MAP7.replace('__N__', str(N)).replace('__P__', str(PEAK)).replace('__R__', json.dumps(ROUTE)).replace("S.vote={at:'berlin',deadline:'',options:[]}", "S.vote={at:'pariz',deadline:'',options:[]}")

def roster():
    r = json.loads(film3.roster(400))
    r[SUP - 1][1] = "tvuj.nick"
    return json.dumps(r)

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=EXTRA)
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, roster(), "null"))
    await pg.evaluate(STATE)
    await pg.evaluate(film3.NODRV)

def pop(ids, times):
    return "const A=%s;const I=%s;for(let i=0;i<I.length;i++){const k=t-A[i];const e=document.getElementById(I[i]);if(!e)continue;e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}" % (json.dumps(times), json.dumps(ids))

async def shot(pg, name):
    if name == "p1_win":   # 0–3,88: Hlasování skončilo… a vyhrála PAŘÍŽ!
        await pg.evaluate(MAP)
        await pg.evaluate("()=>{const [x,y,w]=__fit(['berlin','pariz','kodan','hamburk']);__vb(x,y,w)}")
        await pg.evaluate(ov('<div class="eb">Výhybka v Berlíně</div><div class="ttl">Hlasování<br><y>skončilo…</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          f'<div style="position:absolute;left:0;right:0;top:1290px;text-align:center"><div class="stampG" id="st" style="font-size:120px;padding:30px 60px">🇫🇷 PAŘÍŽ!</div><div id="vv" style="margin-top:40px;font:800 56px IS,sans-serif;color:#1e2a33;opacity:0">přibližně {VOTES} hlasů</div></div>')
        js = ease + "const s=t-2.86;document.getElementById('st').style.transform=`rotate(-4deg) scale(${s<0?0:(s<.35?B(s/.35):1)})`;document.getElementById('vv').style.opacity=s<.3?0:1;const c=document.getElementById('mapbox');const k=s>0?Math.exp(-s*3):0;c.style.transform=`translate(${Math.sin(t*61)*20*k}px,${Math.cos(t*47)*14*k}px)`"
        await pg.evaluate(fx(js))
        cues = {T(1.72): ov('<div class="eb">Výsledek hlasování</div><div class="ttl">A vyhrála…</div>'),
                T(2.86): ov('<div class="eb">Výsledek hlasování</div><div class="ttl huge"><y>Paříž!</y></div>')}
        await film.record(pg, name, 3.9, cues=cues)
    elif name == "p2_route":   # 3,88–9,86: Z Berlína je to přes Hannover, Kolín nad Rýnem a Brusel přes 1 200 km.
        await pg.evaluate(MAP)
        await pg.evaluate("()=>{const [x,y,w]=__fit(['berlin','pariz']);__vb(x,y,w)}")
        await pg.evaluate(ov('<div class="eb">Berlín → Paříž</div><div class="ttl">Cesta do<br><y>Paříže</y></div>'))
        cities = [("c0", "Berlín"), ("c1", "Hannover"), ("c2", "Kolín n. R."), ("c3", "Brusel"), ("c4", "Lille"), ("c5", "Paříž")]
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          '<div class="cities">' + ''.join(f'<span id="{i}"{" class=end" if i == "c5" else ""}>{n}</span>' for i, n in cities) + '</div><div class="bigkm" id="km">1 220 km</div>')
        js = ease + pop([i for i, _ in cities], [0.15, 1.3, 2.2, 3.0, 3.6, 4.1]) + ";const k=t-4.4;const e=document.getElementById('km');e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.5:(k<.3?B(k/.3):1)})`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6.0, cues={T(2.03): ov('<div class="eb">Berlín → Paříž</div><div class="ttl">Přes<br><y>1 200 km</y></div>')})
    elif name == "p3_catch":   # 9,86–15,10: Jenže je tu háček. Vlak jede jen tolik kilometrů, kolik je nás.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.55)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Jenže…</div><div class="ttl huge">Háček!</div>'))
        js = "const c=document.querySelector('canvas');const k=t>0.1?Math.exp(-(t-.1)*3):0;c.style.transform=`translate(${Math.sin(t*63)*20*k}px,${Math.cos(t*51)*14*k}px)`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 5.3, cues={T(1.97): ov('<div class="eb">Pravidlo hry</div><div class="ttl">Kolik nás je,<br><y>tolik km</y></div>'),
                                               T(2.0): "()=>{Game.flyTo(20,.75)}"})
    elif name == "p4_rule":   # 15,10–18,35: Každý nový cestující = jeden kilometr.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(30,.7)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Pravidlo hry</div><div class="ttl">1 cestující =<br><y>1 km</y></div>'))
        pl = ''.join(f'<div class="plus" id="pl{i}" style="left:{x}px;top:{y}px">+1 km</div>' for i, (x, y) in enumerate([(140, 1150), (620, 1050), (300, 1400), (700, 1330), (420, 1220)]))
        await setfull(pg, pl)
        js = "for(let i=0;i<5;i++){const k=t-.3-i*.5;const e=document.getElementById('pl'+i);e.style.opacity=k<0||k>1.2?0:Math.min(1,k/.15)*(1-Math.max(0,k-.8)/.4);e.style.transform=`translateY(${-k*120}px)`}"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.3, cues={0: "()=>{Game.flyTo(36,.7)}"})
    elif name == "p5_missing":   # 18,35–22,08: A do Paříže nám chybí ještě asi 650 lidí.
        await pg.evaluate(MAP)
        await pg.evaluate("()=>{const [x,y,w]=__fit(['berlin','pariz']);__vb(x,y,w)}")
        await pg.evaluate(ov('<div class="eb">Lokomotiva je za Hannoverem</div><div class="ttl">Do Paříže<br><y>chybí</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          f'<div class="miss"><div class="k">chybí ještě</div><div class="n" id="mn">0</div><div class="u">cestujících</div></div>')
        js = ease + f"document.getElementById('mn').textContent='~'+Math.round(E(Math.max(0,t-.6)/1.6)*{MISS}).toLocaleString('cs-CZ')"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.8)
    elif name == "p6_eiffel":   # 22,08–27,97: Takže pokud chcete vidět Eiffelovku… pošlete video kamarádům a vezměte je do vlaku!
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.6)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Cíl: Paříž</div><div class="ttl">Chcete vidět<br><y>Eiffelovku?</y></div>'))
        await setfull(pg, '<div class="share"><span id="sh">📤 Pošli kamarádům</span></div>')
        js = ease + "const s=t-2.57;document.getElementById('sh').style.transform=`scale(${s<0?0:(s<.35?B(s/.35):1)})`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6.0, cues={T(2.57): ov('<div class="eb">Cíl: Paříž</div><div class="ttl">Vezměte je<br><y>do vlaku!</y></div>')})
    elif name == "p7_support":   # 27,97–34,20: A jestli nám chcete pomoct jinak: web a servery stojí peníze. Na webu najdete tlačítko Podpořit,
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(SUPN,.75)}".replace("SUPN", str(SUP - 6))); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Podpoř vlak</div><div class="ttl">Chceš pomoct<br><y>jinak?</y></div>'))
        await setfull(pg, '<div class="webbtn" id="wb"><span style="font-size:80px">☕</span>Podpořit</div><div class="tap" id="tp" style="left:620px;top:1300px"></div>')
        js = ease + "const s=t-4.13;document.getElementById('wb').style.transform=`translateX(-50%) scale(${s<0?0:(s<.35?B(s/.35):1)})`;const q=t-5.0;const tp=document.getElementById('tp');tp.style.opacity=q<0?0:Math.max(0,1-q/.6);tp.style.transform=`scale(${q<0?.4:.4+q*1.4})`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6.3, cues={T(1.98): ov('<div class="eb">Podpoř vlak</div><div class="ttl">Servery stojí<br><y>peníze</y></div>'),
                                               T(4.13): ov('<div class="eb">Na webu</div><div class="ttl">Tlačítko<br><y>Podpořit</y></div>')})
    elif name == "p8_star":   # 34,20–39,23: a kdo přispěje, dostane hvězdičku u svého vagónu a bude v seznamu podporovatelů.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(%d,.6)}" % SUP); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Pro podporovatele</div><div class="ttl">Hvězdička<br><y>u vagónu ⭐</y></div>'))
        await film.record(pg, name, 5.1, cues={0: "()=>{Game.flyTo(%d,0)}" % SUP,
                                               T(2.6): ov('<div class="eb">Pro podporovatele</div><div class="ttl">Seznam<br><y>podporovatelů</y></div>')})
    elif name == "p9_outro":
        os.environ["OUTRO_AT"] = "0.05,1.43,2.2"
        os.environ["OUTRO_LEN"] = "4.7"
        await film5.shot(pg, "v7_outro")

ALL = ["p1_win", "p2_route", "p3_catch", "p4_rule", "p5_missing", "p6_eiffel", "p7_support", "p8_star", "p9_outro"]

async def main():
    names = sys.argv[1:] or ALL
    os.makedirs(f"{ROOT}/clips", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            ctx, pg = await mk(b)
            await shot(pg, n)
            await ctx.close()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
