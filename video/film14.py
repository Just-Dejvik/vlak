# Díl 14: Výsledek výhybky – vyhráli LIDI (259 : 152), milionáře vlak přejel (kresleně, bez krve) + stav cesty do Paříže.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7, film11, film12, film13
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = PEAK = 1816
LEFT = 2124 - N
ROUTE = film12.ROUTE
GOLD = film12.GOLD
SUP = film12.SUP

EXTRA13 = film13.EXTRA + r"""
.vbar{position:fixed;left:70px;right:70px;top:1180px;z-index:70;display:grid;gap:30px}
.vrow{background:rgba(255,255,255,.92);border-radius:28px;padding:22px 26px;box-shadow:0 12px 30px rgba(0,0,0,.25)}
.vrow .h{display:flex;justify-content:space-between;font:900 70px/1 BS,sans-serif;text-transform:uppercase;color:#1e2a33;margin-bottom:16px}
.vrow .tr{height:46px;background:#e3e7ea;border-radius:999px;overflow:hidden}
.vrow .f{height:100%;width:0;border-radius:999px}
.win{position:fixed;left:0;right:0;top:1300px;z-index:70;text-align:center}
.win span{display:inline-block;background:#2f6f9f;color:#fff;font:900 150px/1 BS,sans-serif;padding:26px 70px;border-radius:40px;box-shadow:0 14px 0 rgba(0,0,0,.25),0 0 60px rgba(80,160,255,.6);transform:scale(0)}
.cf{position:fixed;top:-40px;width:22px;height:34px;z-index:69;border-radius:4px}
"""

def confetti(t0, n=70):
    import random
    r = random.Random(7)
    cols = ["#d4361f", "#2f6f9f", "#f0a03a", "#3f8a5c", "#ffc93a", "#e24a7a", "#2b9fc2"]
    html = "".join(f'<div class="cf" id="cf{i}" style="left:{r.randint(0,1060)}px;background:{r.choice(cols)}"></div>' for i in range(n))
    par = [(r.uniform(0, .5), r.uniform(700, 1300), r.uniform(-120, 120), r.uniform(3, 9)) for _ in range(n)]
    js = (f"const P={json.dumps(par)};for(let i=0;i<P.length;i++){{const e=document.getElementById('cf'+i);const k=t-{t0}-P[i][0];"
          "if(k<0){e.style.opacity=0;continue}e.style.opacity=1;e.style.transform=`translate(${Math.sin(k*P[i][3])*P[i][2]*.3+P[i][2]*k}px,${k*P[i][1]}px) rotate(${k*P[i][3]*80}deg) rotateY(${k*P[i][3]*120}deg)`}")
    return html, js

async def mk_t(b):
    ctx, pg = await film13.mk(b)
    await pg.add_style_tag(content=EXTRA13)
    return ctx, pg

# --- záběry z webu (mapa a konec) ---
STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=%s;renderHud()}"
         % (N, PEAK, json.dumps(ROUTE), json.dumps(SUP)))
MAP = film7.MAP7.replace('__N__', str(N)).replace('__P__', str(PEAK)).replace('__R__', json.dumps(ROUTE)).replace("S.vote={at:'berlin',deadline:'',options:[]}", "S.vote={at:'pariz',deadline:'',options:[]}")

async def mk_w(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=film12.EXTRA)
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, film12.roster(), "null"))
    await pg.evaluate(STATE)
    await pg.evaluate(film3.NODRV)

async def shot(pg, name):
    S = lambda n, **o: pg.evaluate("([n,o])=>SHOT(n,o)", [n, o])
    full = lambda h: pg.evaluate("h=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='70';f.innerHTML=h}", h)
    if name == "v1_decided":    # 0–1,62: Výhybka je rozhodnutá!
        await S("j_end")
        await pg.evaluate(ov('<div class="eb">Výsledek</div><div class="ttl">Výhybka je<br><y>rozhodnutá!</y></div>'))
        await film.record(pg, name, 1.62)
    elif name == "v2_win":      # 1,62–5,56: Hlasovalo přes 400 lidí a vyhráli… LIDI!
        await S("c_both")
        await pg.evaluate(ov('<div class="eb">Hlasovalo</div><div class="ttl">Přes<br><y>400 lidí!</y></div>'))
        h, cj = confetti(3.1)
        await full('<div class="win"><span id="wn">👥 Lidi!</span></div>' + h)
        js = ease + "const k=t-3.1;document.getElementById('wn').style.transform=`scale(${k<0?0:(k<.35?B(k/.35):1+.03*Math.sin(k*6))})`;" + cj
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.94, cues={T(2.0): ov('<div class="eb">A vyhráli…</div><div class="ttl huge">…</div>'),
                                               T(3.1): ov('<div class="eb">Vyhráli</div><div class="ttl huge"><y>LIDI!</y></div>')})
    elif name == "v3_score":    # 5,56–8,74: 259 proti 152
        await S("f_right")
        await full('<div style="position:absolute;inset:0;background:rgba(20,30,40,.35)"></div><div class="vbar">'
                   '<div class="vrow"><div class="h"><span>👥 Lidi</span><span id="na">0</span></div><div class="tr"><div class="f" id="fa" style="background:#2f6f9f"></div></div></div>'
                   '<div class="vrow"><div class="h"><span>💰 Milionář</span><span id="nb">0</span></div><div class="tr"><div class="f" id="fb" style="background:#c99a1e"></div></div></div></div>')
        await pg.evaluate(ov('<div class="eb">Hlasování</div><div class="ttl huge">259 <y>:</y> 152</div>'))
        js = ease + "const u=E(Math.max(0,t-.15)/1.3);document.getElementById('na').textContent=Math.round(u*259);document.getElementById('nb').textContent=Math.round(u*152);document.getElementById('fa').style.width=(u*63)+'%';document.getElementById('fb').style.width=(u*37)+'%'"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.18)
    elif name == "v4_lever":    # 8,74–9,80: Páka je přehozená,
        await S("k_lever")
        await pg.evaluate(ov('<div class="eb">Páka je</div><div class="ttl"><y>přehozená!</y></div>'))
        await film.record(pg, name, 1.06)
    elif name == "v5_saved":    # 9,80–13,23: dvacet lidí je zachráněných a nikdo z vlaku nevyletí.
        await S("l_saved")
        await pg.evaluate(ov('<div class="eb">Zachráněno</div><div class="ttl"><y>20 lidí</y> ✅</div>'))
        await film.record(pg, name, 3.43, cues={T(1.62): ov('<div class="eb">A z vlaku</div><div class="ttl">Nikdo<br><y>nevyletí!</y></div>')})
    elif name == "v6_hit":      # 13,23–17,73: A milionář? Ten měl smůlu. Zbyly po něm jen peníze a cylindr.
        await S("m_hit", bub="Néééé! 😱")
        await pg.evaluate(ov('<div class="eb">A milionář?</div><div class="ttl huge">A <y>milionář?</y></div>'))
        await film.record(pg, name, 4.5, cues={T(1.25): ov('<div class="eb">Ten měl</div><div class="ttl huge"><y>Smůlu…</y></div>'),
                                              T(2.2): ov('<div class="eb">Zbyly po něm jen</div><div class="ttl">Peníze<br>a <y>cylindr</y> 🎩</div>')})
    elif name == "v7_map":      # 17,73–21,75: A Paříž? Projeli jsme Bruselem a zbývá už jen tři sta kilometrů.
        await pg.evaluate(MAP)
        await pg.evaluate(ov('<div class="eb">Cíl cesty</div><div class="ttl huge">A <y>Paříž?</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          f'<div class="kmcard"><div id="k0">✅ Brusel</div><div id="k1">🏁 Paříž: <b>{LEFT} km</b></div></div>')
        await pg.evaluate(fx(ease + film12.pop(["k0", "k1"], [1.2, 2.5])))
        await film.record(pg, name, 4.02, cues={T(1.05): ov('<div class="eb">Kde jsme?</div><div class="ttl">Za<br><y>Bruselem!</y></div>'),
                                               T(2.5): ov(f'<div class="eb">Do Paříže zbývá</div><div class="ttl">Už jen<br><y>{LEFT} km</y></div>')})
    elif name == "v8_end":      # 21,75–24,40 (+dojezd): Dej follow a nastup, odkaz na web je v biu!
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Dej follow<br><y>a nastup!</y></div>'))
        await setfull(pg, '<div style="position:absolute;left:0;right:0;top:1330px;text-align:center"><span id="fb" style="display:inline-block;background:#2f6f9f;color:#fff;border-radius:22px;padding:24px 56px;font:800 66px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)">➕ Sledovat</span>'
                      '<div id="ht" style="margin-top:46px;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div></div>')
        js = ease + "const s=t-.25;document.getElementById('fb').style.transform=`scale(${s<0?0:(s<.35?B(s/.35):1+.03*Math.sin(s*5))})`;document.getElementById('ht').style.opacity=t<1.35?0:Math.min(1,(t-1.35)/.3)"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.95, cues={T(1.33): ov('<div class="eb">Odkaz na web</div><div class="ttl">Je v <y>biu!</y> 👆</div>')})

TROLLEY = ["v1_decided", "v2_win", "v3_score", "v4_lever", "v5_saved", "v6_hit"]
ALL = TROLLEY + ["v7_map", "v8_end"]

async def main():
    names = sys.argv[1:] or ALL
    os.makedirs(f"{ROOT}/clips", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            ctx, pg = await (mk_t(b) if n in TROLLEY else mk_w(b))
            await shot(pg, n)
            await ctx.close()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
