# Díl 12: Díky! Máme 4 zlaté vagóny + stav cesty (Kolín nad Rýnem, Brusel 77 km, do Paříže chybí ~450).
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7, film11
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 1675
PEAK = 1675
NEED = 2124
MISS = NEED - PEAK
ROUTE = ['praha', 'kolin', 'pardubice', 'hradec', 'liberec', 'vratislav', 'poznan', 'berlin', 'hannover', 'koln_r', 'brusel', 'lille', 'pariz']
# podporovatelé (sami se zapsali do seznamu podporovatelů) – skuteční panáčci a vagóny z webu
GOLD = {
    504: ["danielasimova278", {"coat": "#2b2f3a", "hat": "zadna", "pet": "pes", "item": "hrnek", "hair": "#6b3f22", "skin": "#f1c9a5"}],
    717: ["_fiala_27", {"coat": "#7a4fa3", "hat": "cepice", "pet": "zadny", "item": "hrnek", "hair": "#c9a35a", "skin": "#9c6b48"}],
    1157: ["karol_ledin", {"coat": "#c4453a", "hat": "koruna", "pet": "kocka", "item": "kniha", "hair": "#c9a35a", "skin": "#f1c9a5"}],
    1309: ["brazile_c28_gg", {"coat": "#2f6f9f", "hat": "klobouk", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#d9a27a"}],
}
SUP = [v[0] for v in GOLD.values()]

EXTRA = film11.EXTRA + r"""
.gtag{position:absolute;left:0;right:0;top:1330px;text-align:center}
.gtag span{display:inline-block;background:linear-gradient(#ffe27a,#f0b323);color:#3a2600;border-radius:999px;padding:22px 40px;font:800 62px/1 IS,sans-serif;box-shadow:0 0 40px rgba(255,200,40,.7),0 12px 30px rgba(0,0,0,.25);transform:scale(0)}
.miss{position:absolute;left:0;right:0;top:1250px;text-align:center}
.miss .k{font:600 40px PM,monospace;letter-spacing:.16em;text-transform:uppercase;color:#1e2a33}
.miss .n{font:900 230px/1 BS,sans-serif;color:#cf4630;text-shadow:0 8px 0 rgba(120,30,20,.25)}
.miss .u{font:800 56px/1 IS,sans-serif;color:#1e2a33}
.big{position:absolute;left:0;right:0;top:1180px;text-align:center;font:900 260px/1 BS,sans-serif;color:#fff;text-shadow:0 10px 0 rgba(20,40,60,.35)}
.kmcard{position:absolute;left:80px;right:80px;top:1240px;display:grid;gap:22px}
.kmcard div{background:#fff;border-radius:28px;padding:22px 30px;font:800 56px/1.1 IS,sans-serif;color:#1e2a33;box-shadow:0 12px 30px rgba(0,0,0,.2);opacity:0;transform:scale(.4)}
.kmcard b{color:#cf4630}
"""

STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=%s;renderHud()}"
         % (N, PEAK, json.dumps(ROUTE), json.dumps(SUP)))
MAP = film7.MAP7.replace('__N__', str(N)).replace('__P__', str(PEAK)).replace('__R__', json.dumps(ROUTE)).replace("S.vote={at:'berlin',deadline:'',options:[]}", "S.vote={at:'pariz',deadline:'',options:[]}")

def roster():
    r = json.loads(film3.roster(1400))
    for w, (nick, av) in GOLD.items():
        r[w - 1] = [w, nick, av]
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

def cam_js(n):
    return film11.CAM.replace("v.n===%d" % film11.GW, "v.n===%d" % n)

def pop(ids, times):
    return "const A=%s;const I=%s;for(let i=0;i<I.length;i++){const k=t-A[i];const e=document.getElementById(I[i]);if(!e)continue;e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}" % (json.dumps(times), json.dumps(ids))

async def gold_close(pg, name, n, nick, length, title):
    await train(pg)
    await pg.evaluate(f"()=>{{Game.flyTo({n},.6)}}"); await steps(pg, 240)
    await pg.evaluate(cam_js(n), [8.0, 2.65, 9.0, -1.5, 2.9, 0]); await steps(pg, 5)
    await pg.evaluate(ov(title))
    await setfull(pg, f'<div class="gtag"><span id="gt">⭐ @{nick}</span></div>')
    js = ease + "{const k=t;window.__cam=[8.0-k*1.2,2.65+k*.1,9.0-k*1.0,-1.5,2.9,0]};document.getElementById('gt').style.transform=`scale(${t<.25?B(t/.25):1})`"
    await pg.evaluate(fx(js))
    await film.record(pg, name, length)

async def shot(pg, name):
    if name == "r1_four":   # 0–2,90: Lidi… máme ČTYŘI zlaté vagóny!
        await train(pg)
        await pg.evaluate("()=>{Game.setOverview(true,true)}"); await steps(pg, 70)
        await pg.evaluate(ov('<div class="eb">Lidi…</div><div class="ttl huge">Lidi…</div>'))
        await film.record(pg, name, 2.9, cues={T(.75): ov('<div class="eb">Celý vlak</div><div class="ttl">Máme 4<br><y>zlaté vagóny!</y> ✨</div>')})
    elif name == "r2a":
        await gold_close(pg, name, 504, "danielasimova278", .5, '<div class="eb">Vagón № 504</div><div class="ttl">Díky,<br><y>Danielo!</y></div>')
    elif name == "r2b":
        await gold_close(pg, name, 717, "_fiala_27", .35, '<div class="eb">Vagón № 717</div><div class="ttl">Díky,<br><y>Fialo!</y></div>')
    elif name == "r2c":
        await gold_close(pg, name, 1157, "karol_ledin", .45, '<div class="eb">Vagón № 1 157</div><div class="ttl">Díky,<br><y>Karole!</y></div>')
    elif name == "r2d":
        await gold_close(pg, name, 1309, "brazile_c28_gg", 1.25, '<div class="eb">Vagón № 1 309</div><div class="ttl">Díky,<br><y>Brazile!</y></div>')
    elif name == "r3_thanks":   # 5,40–8,57: moc vám děkujeme! Díky vám vlak jede dál.
        await train(pg)
        await pg.evaluate("()=>{Game.setOverview(true,true)}"); await steps(pg, 90)
        await pg.evaluate(ov('<div class="eb">Podporovatelé vlaku</div><div class="ttl huge">Moc<br><y>děkujeme!</y></div>'))
        await film.record(pg, name, 3.17, cues={T(1.42): ov('<div class="eb">Díky vám</div><div class="ttl">Vlak jede<br><y>dál!</y> 🚂</div>')})
    elif name == "r4_zero":   # 8,57–11,02: Ještě před pár dny jsme měli nula korun…
        await setfull(pg, '<div style="position:absolute;inset:0;background:#1e2a33"></div><div class="zero" style="top:700px"><div class="n" id="z">0 Kč</div><div class="k" id="cr" style="font-size:80px">🦗 🦗 🦗</div></div>')
        await pg.evaluate(ov('<div class="eb">Před pár dny</div><div class="ttl">Nula<br><y>korun</y></div>'))
        js = ease + "const z=document.getElementById('z');z.style.transform=`scale(${t<.3?B(t/.3):1+.02*Math.sin(t*3)})`;document.getElementById('cr').style.transform=`translateX(${Math.sin(t*20)*6}px)`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 2.45)
    elif name == "r4_gold":   # 11,02–14,10: a teď se ve vlaku lesknou čtyři zlaté vagóny.
        await gold_close(pg, name, 1157, "karol_ledin", 3.08, '<div class="eb">A teď?</div><div class="ttl">4 zlaté<br><y>vagóny</y> ✨</div>')
    elif name == "r5_count":   # 14,10–18,75: A vlak mezitím nabral rychlost. Je nás 1 675!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(900,1)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Mezitím</div><div class="ttl">Vlak nabral<br><y>rychlost!</y></div>'))
        await setfull(pg, '<div class="big" id="bn" style="opacity:0">0</div>')
        js = ease + f"const k=t-1.95;const e=document.getElementById('bn');e.style.opacity=k<0?0:1;e.textContent=Math.round(E(Math.max(0,k)/1.6)*{N}).toLocaleString('cs-CZ')"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.65, cues={0: "()=>{Game.flyTo(40,1)}", T(1.95): ov('<div class="eb">Cestujících</div><div class="ttl">Je nás<br><y>1 675!</y></div>')})
    elif name == "r6_map":   # 18,75–23,92: Projeli jsme Kolínem nad Rýnem a do Bruselu zbývá posledních 77 km.
        await pg.evaluate(MAP)
        await pg.evaluate(ov('<div class="eb">Kde jsme?</div><div class="ttl">Za Kolínem<br><y>nad Rýnem</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          '<div class="kmcard"><div id="k0">✅ Kolín nad Rýnem</div><div id="k1">🏁 Brusel: <b>77 km</b></div></div>')
        await pg.evaluate(fx(ease + pop(["k0", "k1"], [.4, 2.7])))
        await film.record(pg, name, 5.17, cues={T(2.7): ov('<div class="eb">Další stanice</div><div class="ttl">Brusel<br><y>za 77 km</y></div>')})
    elif name == "r7_miss":   # 23,92–26,92: Do Paříže nám chybí už jen 450 lidí!
        await pg.evaluate(MAP)
        await pg.evaluate(ov('<div class="eb">Cíl: Paříž</div><div class="ttl">Do Paříže<br><y>chybí</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          '<div class="miss"><div class="k">už jen</div><div class="n" id="mn">0</div><div class="u">cestujících</div></div>')
        await pg.evaluate(fx(ease + f"document.getElementById('mn').textContent=Math.round(E(Math.max(0,t-.3)/1.4)*{MISS}).toLocaleString('cs-CZ')"))
        await film.record(pg, name, 3.0)
    elif name == "r8_invite":   # 26,92–29,80: Tak pozvi kamarády, ať tam dojedeme co nejdřív.
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Cíl: Paříž</div><div class="ttl">Pozvi<br><y>kamarády!</y></div>'))
        await setfull(pg, '<div class="share" style="position:absolute;left:0;right:0;top:1380px;text-align:center"><span id="sh" style="display:inline-block;background:#fff;border-radius:999px;padding:22px 40px;font:800 58px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)">📤 Pošli kamarádům</span></div>')
        await pg.evaluate(fx(ease + "const s=t-.4;document.getElementById('sh').style.transform=`scale(${s<0?0:(s<.35?B(s/.35):1)})`"))
        await film.record(pg, name, 2.88)
    elif name == "r9_support":   # 29,80–34,74 (+dojezd): A kdo chce taky zlatý vagón, tlačítko Podpořit najdeš na webu. Odkaz je v profilu!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(717,.6)}"); await steps(pg, 240)
        await pg.evaluate(cam_js(717), [7.5, 2.65, 8.8, -1.5, 2.9, 0]); await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Chceš taky?</div><div class="ttl">Zlatý vagón<br><y>pro tebe</y> ✨</div>'))
        await setfull(pg, '<div id="wb" style="position:absolute;left:50%;top:1300px;transform:translateX(-50%) scale(0);background:#fff;border-radius:30px;padding:26px 44px;box-shadow:0 18px 40px rgba(0,0,0,.3);font:800 66px/1 IS,sans-serif;color:#c2410c;white-space:nowrap">☕ Podpořit</div>'
                      '<div id="ht" style="position:absolute;left:0;right:0;top:1500px;text-align:center;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div>')
        js = ease + "{const k=t;window.__cam=[7.5-k*.4,2.65+k*.05,8.8-k*.5,-1.5,2.9,0]};const s=t-1.45;document.getElementById('wb').style.transform=`translateX(-50%) scale(${s<0?0:(s<.35?B(s/.35):1)})`;document.getElementById('ht').style.opacity=t<3.7?0:Math.min(1,(t-3.7)/.3)"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6.2, cues={T(1.45): ov('<div class="eb">Na webu</div><div class="ttl">Tlačítko<br><y>Podpořit</y></div>'),
                                               T(3.75): ov('<div class="eb">@vlak.followeru</div><div class="ttl">Odkaz je<br><y>v profilu!</y></div>')})

ALL = ["r1_four", "r2a", "r2b", "r2c", "r2d", "r3_thanks", "r4_zero", "r4_gold", "r5_count", "r6_map", "r7_miss", "r8_invite", "r9_support"]

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
