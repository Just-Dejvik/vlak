# Díl 18: Výsledky uhelného eventu – cíl 44 000 splněn za hodinu, 104 882 lopat, +100 km, do Paříže 39 km, top 5 zlatých lopat.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7, film12, film14, film15
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = PEAK = 1985
BONUS = 100
LEFT = 2124 - N - BONUS            # 39 km
ROUTE = film12.ROUTE
TOP = [  # pořadí eventu (pravidlo: top 5 bude ve videu; nicky jsou veřejné)
    (1906, "neptun", 19597, {"coat": "#7a4fa3", "hat": "koruna", "pet": "pes", "item": "kytara", "hair": "#6b3f22", "skin": "#f1c9a5"}),
    (1813, "egor8.11", 15948, {"coat": "#7a4fa3", "hat": "zadna", "pet": "zadny", "item": "nic", "hair": "#2a1c14", "skin": "#f1c9a5"}),
    (504, "danielasimova278", 14266, {"coat": "#2b2f3a", "hat": "zadna", "pet": "pes", "item": "hrnek", "hair": "#6b3f22", "skin": "#f1c9a5"}),
    (1134, "jirkarybari", 11039, {"coat": "#2b2f3a", "hat": "koruna", "pet": "pes", "item": "hrnek", "hair": "#2a1c14", "skin": "#d9a27a"}),
    (682, "katka_kasalova", 10251, {"coat": "#e8e0cc", "hat": "koruna", "pet": "kocka", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}),
]
GOLDSH = [t[1] for t in TOP]

def roster():
    r = json.loads(film3.roster(N))
    for w, (nick, av) in film12.GOLD.items():
        r[w - 1] = [w, nick, av]
    for w, nick, _, av in TOP:
        r[w - 1] = [w, nick, av]
    return json.dumps(r)
ROSTER = roster()

STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.bonusKm=%d;S.goldShovels=%s;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=%s;renderHud()}"
         % (N, PEAK, BONUS, json.dumps(GOLDSH), json.dumps(ROUTE), json.dumps(film12.SUP)))
MAP = (film7.MAP7.replace('__N__', str(N)).replace('__P__', str(PEAK)).replace('__R__', json.dumps(ROUTE))
       .replace("S.vote={at:'berlin',deadline:'',options:[]}", "S.vote={at:'pariz',deadline:'',options:[]};S.bonusKm=%d" % BONUS))

EXTRA = r"""
.cardc{position:absolute;left:60px;right:60px;top:1150px;background:rgba(20,14,10,.8);border-radius:44px;padding:30px 40px;box-shadow:inset 0 0 0 3px rgba(255,170,80,.3)}
.cardc .n{display:inline-block;font:800 130px/1 BS,sans-serif;color:#ffd27a;transform-origin:0 70%}
.cardc .g{font:600 50px IS,sans-serif;color:#e8d9c4}
.cardc .tr{height:38px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin-top:22px;position:relative}
.cardc .tr i{display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,#ff5a1f,#ffb02e,#ffe27a);box-shadow:0 0 30px rgba(255,140,40,.8)}
.stamp{position:absolute;left:0;right:0;text-align:center}
.stamp span{display:inline-block;background:#3f8a5c;color:#fff;border-radius:26px;padding:22px 44px;font:800 64px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.3);transform:scale(0) rotate(-4deg)}
.lb{position:absolute;left:60px;right:60px;top:1020px;display:grid;gap:22px}
.lb .r{display:flex;align-items:center;gap:22px;background:rgba(255,255,255,.95);border-radius:30px;padding:20px 30px;box-shadow:0 12px 30px rgba(0,0,0,.3);transform:translateX(-1200px)}
.lb .r b{font:900 80px/1 BS,sans-serif;color:#c99a1e;width:70px;text-align:center}
.lb .r .nk{flex:1;font:800 54px/1.1 IS,sans-serif;color:#1e2a33;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lb .r .c{font:700 46px IS,sans-serif;color:#7a4a10}
.win{position:absolute;left:0;right:0;top:1180px;text-align:center}
.win .w1{display:inline-block;background:linear-gradient(#ffe27a,#f0b323);color:#3a2600;border-radius:40px;padding:26px 56px;font:900 110px/1 BS,sans-serif;box-shadow:0 0 60px rgba(255,200,40,.85),0 14px 0 rgba(0,0,0,.2);transform:scale(0)}
.win .w2{margin-top:30px;font:800 64px IS,sans-serif;color:#fff;text-shadow:0 5px 0 rgba(20,40,60,.45);opacity:0}
.cf{position:fixed;top:-40px;width:22px;height:34px;z-index:69;border-radius:4px}
"""

async def mk_s(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=film12.EXTRA + EXTRA + "#coalPill{display:none!important}")
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, ROSTER, "null"))
    await pg.evaluate(STATE)
    await pg.evaluate("()=>{Game.refreshWagon()}")
    await pg.evaluate(film3.NODRV)

async def coal(b, gold=False):
    ctx, pg = await film15.mk_c(b, coal=False, api="hang")
    await pg.add_style_tag(content=EXTRA + "#coal .c-top,#coal .c-prog,#coal .c-me,#coal .c-hint,#coal .c-msg,#coal .c-top5,#coal .c-pl,#coal .c-sub{display:none!important}")
    await pg.evaluate("()=>{window.__coalFly=.26" + (";S.goldShovels=['tvuj.nick']" if gold else "") + ";openCoal()}")
    await pg.wait_for_timeout(800)
    for _ in range(20): await pg.evaluate("__step(33.33)")
    return ctx, pg

def swipes(times):
    return {T(t): "()=>(%s)(%d)" % (film15.SWIPE, [0, -18, 14, -6, 10][i % 5]) for i, t in enumerate(times)}

def counter_html(goal=44000):
    return ('<div class="cardc"><div style="display:flex;align-items:baseline;gap:18px"><span class="n" id="ct">0</span><span class="g">/ %s lopat</span></div>'
            '<div class="tr"><i id="cb"></i></div><div id="pc" style="font:800 60px IS,sans-serif;color:#ffd27a;margin-top:16px;opacity:0"></div></div>' % f"{goal:,}".replace(",", " "))

def confetti(t0, n=80, seed=5):
    import random
    r = random.Random(seed)
    cols = ["#d4361f", "#2f6f9f", "#f0a03a", "#3f8a5c", "#ffc93a", "#e24a7a", "#2b9fc2"]
    html = "".join(f'<div class="cf" id="cf{i}" style="left:{r.randint(0,1060)}px;background:{r.choice(cols)}"></div>' for i in range(n))
    par = [(r.uniform(0, .6), r.uniform(700, 1300), r.uniform(-120, 120), r.uniform(3, 9)) for _ in range(n)]
    js = (f"{{const P={json.dumps(par)};for(let i=0;i<P.length;i++){{const e=document.getElementById('cf'+i);if(!e)continue;const k=t-{t0}-P[i][0];"
          "if(k<0){e.style.opacity=0;continue}e.style.opacity=1;e.style.transform=`translate(${P[i][2]*k}px,${k*P[i][1]}px) rotate(${k*P[i][3]*80}deg) rotateY(${k*P[i][3]*120}deg)`}}")
    return html, js

async def shot(name, b):
    if name == "e1_crazy":      # 0–2,22: Uhelný event byl šílený!
        ctx, pg = await coal(b)
        await pg.evaluate(ov('<div class="eb">Uhelný event</div><div class="ttl">Byl<br><y>šílený!</y> 🔥</div>'))
        await film.record(pg, name, 2.22, cues=swipes([.1, .45, .8, 1.15, 1.5, 1.85]))
    elif name == "e2_goal":     # 2,22–6,01: Cíl 44 000 lopat jste dali za necelou hodinu
        ctx, pg = await coal(b)
        await pg.evaluate(ov('<div class="eb">Cíl</div><div class="ttl"><y>44 000</y><br>lopat</div>'))
        await setfull(pg, counter_html() + '<div class="stamp" style="top:1560px"><span id="st">✅ Splněno za 57 minut!</span></div>')
        js = ease + ("{const u=E(Math.min(1,t/2.2));const v=Math.round(u*44000);document.getElementById('ct').textContent=v.toLocaleString('cs-CZ');document.getElementById('cb').style.width=(v/440)+'%';"
                     "const q=t-2.3;document.getElementById('st').style.transform=`scale(${q<0?0:(q<.25?B(q/.25):1)}) rotate(-4deg)`}")
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.79, cues=swipes([.2, .6, 1.0, 1.4, 1.8, 2.2, 2.9]))
    elif name == "e3_total":    # 6,01–9,67: a celkem jste naházeli přes 104 000 lopat!
        ctx, pg = await coal(b)
        await pg.evaluate(ov('<div class="eb">Celkem jste naházeli</div><div class="ttl huge"><y>104 882</y></div>'))
        await setfull(pg, counter_html())
        js = ease + ("{const u=E(Math.min(1,t/2.6));const v=Math.round(44000+u*60882);const e=document.getElementById('ct');e.textContent=v.toLocaleString('cs-CZ');e.style.color=v>44000?'#7dffa0':'#ffd27a';"
                     "document.getElementById('cb').style.width='100%';const p=document.getElementById('pc');p.style.opacity=1;p.textContent='🔥 '+Math.round(v/440)+' % cíle!'}")
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.66, cues=swipes([.1, .45, .8, 1.15, 1.5, 1.85, 2.2, 2.55, 2.9, 3.25]))
    elif name == "e4_map":      # 9,67–14,64: Vlak poskočil o 100 km a do Paříže zbývá už jen 39!
        ctx, pg = await mk_s(b)
        await pg.evaluate(MAP)
        await pg.evaluate(ov('<div class="eb">Odměna</div><div class="ttl">Vlak poskočil<br><y>+100 km!</y> 🚂</div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          f'<div class="kmcard"><div id="k0">🚂 +100 km</div><div id="k1">🏁 Paříž: <b>{LEFT} km</b></div></div>')
        await pg.evaluate(fx(ease + film12.pop(["k0", "k1"], [.5, 2.5])))
        await film.record(pg, name, 4.97, cues={T(2.45): ov(f'<div class="eb">Do Paříže zbývá</div><div class="ttl">Už jen<br><y>{LEFT} km!</y></div>')})
    elif name == "e5_gold":     # 14,64–16,51: A teď zlaté lopaty.
        ctx, pg = await coal(b, gold=True)
        await pg.evaluate(ov('<div class="eb">A teď…</div><div class="ttl">Zlaté<br><y>lopaty!</y> 🏆</div>'))
        await film.record(pg, name, 1.87, cues=swipes([.1, .5, .9, 1.3]))
    elif name == "e6_list":     # 16,51–21,14: Pátá Katka, čtvrtý Jirka, třetí Daniela, druhý Egor…
        ctx, pg = await mk_s(b)
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(%d,.35)}" % TOP[1][0]); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Zlatá lopata ✨</div><div class="ttl">Top <y>5</y><br>topičů</div>'))
        rows = "".join(f'<div class="r" id="r{i}"><b>{i + 1}.</b><span class="nk">{"@" + n if i else "???"}</span><span class="c">{f"{c:,}".replace(",", " ") if i else ""}</span></div>' for i, (w, n, c, a) in enumerate(TOP))
        await setfull(pg, '<div style="position:absolute;inset:0;background:rgba(20,30,40,.35)"></div><div class="lb">' + rows + '</div>')
        times = {4: 0.05, 3: 1.11, 2: 2.29, 1: 3.38, 0: 3.9}
        js = ease + "".join("{const k=t-%f,e=document.getElementById('r%d');e.style.transform=`translateX(${k<0?-1200:(k<.3?-1200*(1-E(k/.3)):0)}px)`}" % (tt, i) for i, tt in times.items())
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.63)
    elif name == "e7_win":      # 21,14–25,84: a první Neptun s neuvěřitelnými 19 tisíci lopatami!
        ctx, pg = await mk_s(b)
        await train(pg)
        w = TOP[0][0]
        await pg.evaluate(f"()=>{{Game.flyTo({w},.12)}}"); await steps(pg, 260)
        await pg.evaluate(film12.cam_js(w), [1.6, 2.75, 4.2, .15, 2.15, -.6]); await steps(pg, 5)
        await pg.add_style_tag(content=".lbl.big{display:none!important}")
        await pg.evaluate(ov('<div class="eb">1. místo 🥇</div><div class="ttl huge"><y>@neptun</y></div>'))
        h, cj = confetti(.5)
        await setfull(pg, '<div class="win"><div class="w1" id="w1">🥇 19 597 lopat</div><div class="w2" id="w2">✨ zlatá lopata do vagónu</div></div>' + h)
        js = ease + "{const k=t;window.__cam=[1.6-k*.18,2.75-k*.03,4.2-k*.3,.15,2.15,-.6]}" + \
             "{const q=t-.5;document.getElementById('w1').style.transform=`scale(${q<0?0:(q<.3?B(q/.3):1+.03*Math.sin(q*5))})`;document.getElementById('w2').style.opacity=Math.min(1,Math.max(0,(t-1.3)/.3))}" + cj
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.7)
    elif name == "e8_paris":    # 25,84–29,18: Stačí 39 nových cestujících a jsme v Paříži.
        ctx, pg = await mk_s(b)
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov(f'<div class="eb">Stačí</div><div class="ttl"><y>{LEFT}</y> lidí<br>a jsme v Paříži! 🗼</div>'))
        await film.record(pg, name, 3.34, cues={0: "()=>{Game.flyTo(0,.5)}"})
    elif name == "e9_end":      # 29,18–konec: Dej follow a nastup, odkaz je v biu!
        ctx, pg = await mk_s(b)
        await train(pg)
        await pg.evaluate("()=>{Game.setStop(true,'pariz','Paříž');Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Dej follow<br><y>a nastup!</y></div>'))
        await setfull(pg, '<div style="position:absolute;left:0;right:0;top:1330px;text-align:center"><span id="fb" style="display:inline-block;background:#2f6f9f;color:#fff;border-radius:22px;padding:24px 56px;font:800 66px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)">➕ Sledovat</span>'
                      '<div id="ht" style="margin-top:46px;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div></div>')
        js = ease + "{const s=t-.2;document.getElementById('fb').style.transform=`scale(${s<0?0:(s<.35?B(s/.35):1+.03*Math.sin(s*5))})`;document.getElementById('ht').style.opacity=t<1.3?0:Math.min(1,(t-1.3)/.3)}"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.9, cues={T(1.37): ov('<div class="eb">Odkaz na web</div><div class="ttl">Je v <y>biu!</y> 👆</div>')})
    await ctx.close()

ALL = ["e1_crazy", "e2_goal", "e3_total", "e4_map", "e5_gold", "e6_list", "e7_win", "e8_paris", "e9_end"]

async def main():
    names = sys.argv[1:] or ALL
    os.makedirs(f"{ROOT}/clips", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            await shot(n, b)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
