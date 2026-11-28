# Díl 20: Kdo dovede vlak do Paříže? Cestující, se kterým vlak dorazí do Paříže, dostane pařížský vagón (Eiffelovka + vlajka).
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7, film12
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
PW = 2024                      # pařížský vagón
N = PW                         # natáčíme stav „právě dorazil“ – pařížský vagón je poslední
PEAK = 1990
ROUTE = film12.ROUTE
def roster():
    r = json.loads(film3.roster(N))
    for w, (nick, av) in film12.GOLD.items():
        r[w - 1] = [w, nick, av]
    r[PW - 1] = [PW, "tvuj.nick", {"coat": "#1f4fa8", "hat": "koruna", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}]
    return json.dumps(r)
ROSTER = roster()
STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.bonusKm=100;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=%s;renderHud()}"
         % (N, N, json.dumps(ROUTE), json.dumps(film12.SUP)))
MAP = (film7.MAP7.replace('__N__', str(PEAK)).replace('__P__', str(PEAK)).replace('__R__', json.dumps(ROUTE))
       .replace("S.vote={at:'berlin',deadline:'',options:[]}", "S.vote={at:'pariz',deadline:'',options:[]};S.bonusKm=100"))
EXTRA = r"""
.pz{position:absolute;left:0;right:0;text-align:center}
.pz span{display:inline-block;border-radius:999px;padding:24px 50px;font:800 64px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.3)}
.big{position:absolute;left:0;right:0;text-align:center;font:900 230px/1 BS,sans-serif;color:#ffd23f;-webkit-text-stroke:14px #13324a;paint-order:stroke fill}
.fr{display:inline-block;width:150px;height:100px;border-radius:12px;background:linear-gradient(90deg,#1f4fa8 33%,#f4f4f0 33% 66%,#d4303a 66%);box-shadow:0 10px 24px rgba(0,0,0,.3);vertical-align:middle}
"""

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=film12.EXTRA + EXTRA + "#coalPill{display:none!important}")
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, ROSTER, "null"))
    await pg.evaluate(STATE)
    await pg.evaluate(film3.NODRV)

def pop(el, t0):
    return "{const q=t-%f,e=document.getElementById('%s');if(e)e.style.transform=`scale(${q<0?0:(q<.28?B(q/.28):1+.03*Math.sin(q*5))})`}" % (t0, el)

async def shot(name, b):
    ctx, pg = await mk(b)
    if name == "p1_close":      # 0–2,41: Do Paříže nám zbývá už jen kousek!
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.55);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Cíl na dohled</div><div class="ttl">Paříž je<br><y>kousek!</y> 🗼</div>'))
        await film.record(pg, name, 2.41, cues={0: "()=>{Game.flyTo(0,.45)}"})
    elif name == "p2_chal":     # 2,41–3,98: A mám pro vás výzvu.
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.4);Game.setShift(-.13)}"); await steps(pg, 220)
        await setfull(pg, '<div style="position:absolute;inset:0;background:rgba(20,30,40,.35)"></div><div class="big" id="vz" style="top:780px;transform:scale(0)">Výzva! 🏆</div>')
        await pg.evaluate(fx(ease + pop("vz", .15)))
        await film.record(pg, name, 1.57)
    elif name == "p3_who":      # 3,98–7,55: Ten, kdo nastoupí přesně ve chvíli, kdy vlak dorazí do Paříže,
        await pg.evaluate(MAP)
        await pg.evaluate("()=>{const [x,y,w]=__fit(['lille','pariz'],1.6);__vb(x,y,w)}")
        await pg.evaluate(ov('<div class="eb">Kdo nastoupí, když…</div><div class="ttl">Vlak dorazí<br><y>do Paříže</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}", '<div class="kmcard"><div id="k0">🚂 → 🗼</div><div id="k1">🎫 Ten cestující vyhraje!</div></div>')
        await pg.evaluate(fx(ease + film12.pop(["k0", "k1"], [.4, 1.8])))
        await film.record(pg, name, 3.57)
    elif name == "p4_wagon":    # 7,55–10,18: dostane speciální pařížský vagón.
        await train(pg)
        await pg.evaluate(f"()=>{{Game.flyTo({PW},.6)}}"); await steps(pg, 240)
        await pg.evaluate(film12.cam_js(PW), [11, 4.5, 13, 0, 3.5, 0]); await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Odměna</div><div class="ttl">Pařížský<br><y>vagón!</y> <span class="fr" style="width:110px;height:72px"></span></div>'))
        await pg.evaluate(fx("{const k=t;window.__cam=[11-k*1.4,4.5+k*.4,13-k*1.6,0,3.5,0]}"))
        await film.record(pg, name, 2.63)
    elif name == "p5_roof":     # 10,18–13,11: S Eiffelovkou na střeše a francouzskou vlajkou!
        await train(pg)
        await pg.evaluate(f"()=>{{Game.flyTo({PW},.6)}}"); await steps(pg, 240)
        await pg.evaluate(film12.cam_js(PW), [4.5, 6.6, 6.5, 0, 5.6, 0]); await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Na střeše</div><div class="ttl"><y>Eiffelovka</y> 🗼<br>a vlajka!</div>'))
        await pg.evaluate(fx("{const k=t;const a=-.4+k*.35;window.__cam=[Math.sin(a)*7.5,6.4+k*.2,Math.cos(a)*7.5,0,5.6,0]}"))
        await film.record(pg, name, 2.93)
    elif name == "p6_only":     # 13,11–15,11: Bude jediný v celém vlaku.
        await train(pg)
        await pg.evaluate(f"()=>{{Game.flyTo({PW},.6)}}"); await steps(pg, 240)
        await pg.evaluate(film12.cam_js(PW), [-16, 7, 15, 9, 2.5, 0]); await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Ze všech vagónů</div><div class="ttl">Jediný<br><y>v celém vlaku!</y></div>'))
        await pg.evaluate(fx("{const k=t;window.__cam=[-16-k*3,7+k*2,15+k*5,9+k*4,2.5,0]}"))
        await film.record(pg, name, 2.0)
    elif name == "p7_you":      # 15,11–17,10: Tak kdo to bude? Ty?
        await train(pg)
        await pg.evaluate(f"()=>{{Game.flyTo({PW},.6)}}"); await steps(pg, 240)
        await pg.evaluate(film12.cam_js(PW), [8, 4, 10, 0, 3.5, 0]); await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Tak kdo</div><div class="ttl huge"><y>to bude?</y> 🤔</div>'))
        await pg.evaluate(fx("{const k=t;window.__cam=[8-k*.8,4,10-k*1.2,0,3.5,0]}"))
        await film.record(pg, name, 1.99, cues={T(1.4): ov('<div class="eb">Možná…</div><div class="ttl huge"><y>Ty?</y> 👉</div>')})
    elif name == "p8_end":      # 17,10–konec: Dej follow, nastup a možná dovedeš vlak do Paříže právě ty. Odkaz je v biu!
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Dej follow<br><y>a nastup!</y></div>'))
        await setfull(pg, '<div style="position:absolute;left:0;right:0;top:1330px;text-align:center"><span id="fb" style="display:inline-block;background:#2f6f9f;color:#fff;border-radius:22px;padding:24px 56px;font:800 66px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)">➕ Sledovat</span>'
                      '<div id="ht" style="margin-top:46px;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div></div>')
        js = ease + pop("fb", .2) + "{document.getElementById('ht').style.opacity=t<1.2?0:Math.min(1,(t-1.2)/.3)}"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6.77, cues={T(1.9): ov('<div class="eb">A možná</div><div class="ttl">Dovedeš vlak<br>do Paříže <y>ty!</y> 🗼</div>'),
                                               T(4.35): ov('<div class="eb">Odkaz na web</div><div class="ttl">Je v <y>biu!</y> 👆</div>')})
    await ctx.close()

ALL = ["p1_close", "p2_chal", "p3_who", "p4_wagon", "p5_roof", "p6_only", "p7_you", "p8_end"]

async def main():
    names = sys.argv[1:] or ALL
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            await shot(n, b)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
