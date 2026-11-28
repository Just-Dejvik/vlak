# Díl 22: Napiš do komentářů číslo vagónu a ukážu ti, co v něm je (ukázky: pes, kytara, zlatá lopata).
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film12
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 1996
ROUTE = film12.ROUTE
DOG, GUIT, GOLDW = 77, 512, 1337
def roster():
    r = json.loads(film3.roster(N))
    for w, (nick, av) in film12.GOLD.items():
        r[w - 1] = [w, nick, av]
    r[DOG - 1] = [DOG, "pejskar.kuba", {"coat": "#3f8a5c", "hat": "cepice", "pet": "pes", "item": "hrnek", "hair": "#6b3f22", "skin": "#f1c9a5"}]
    r[GUIT - 1] = [GUIT, "rockerka_ema", {"coat": "#2b2f3a", "hat": "zadna", "pet": "zadny", "item": "kytara", "hair": "#a8501f", "skin": "#f1c9a5"}]
    r[GOLDW - 1] = [GOLDW, "topic.mira", {"coat": "#7a4fa3", "hat": "koruna", "pet": "kocka", "item": "nic", "hair": "#2a1c14", "skin": "#d9a27a"}]
    return json.dumps(r)
ROSTER = roster()
STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.bonusKm=100;S.goldShovels=['topic.mira'];S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=%s;renderHud()}"
         % (N, N, json.dumps(ROUTE), json.dumps(film12.SUP)))
EXTRA = r"""
.cmx{position:absolute;left:70px;right:70px;display:flex;align-items:center;gap:22px;background:#fff;border-radius:34px;padding:22px 30px;box-shadow:0 14px 34px rgba(0,0,0,.3);transform:scale(0);transform-origin:20% 50%}
.cmx .av{width:84px;height:84px;border-radius:50%;flex:none}
.cmx .tx{flex:1;font:700 52px/1.15 IS,sans-serif;color:#1e2a33}
.cmx .tx small{display:block;font:600 34px IS,sans-serif;color:#7b8a97}
.cmx .hr{font:800 46px IS,sans-serif;color:#d4361f;white-space:nowrap}
.num{position:absolute;left:0;right:0;top:1240px;text-align:center}
.num span{display:inline-block;background:#1e2a33;color:#ffd23f;border-radius:30px;padding:20px 44px;font:900 110px/1 BS,sans-serif;box-shadow:0 14px 34px rgba(0,0,0,.35);transform:scale(0)}
"""
CAMI = [2.4, 2.95, 5.6, .05, 2.05, -.5]

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=film12.EXTRA + EXTRA + "#coalPill{display:none!important}.lbl.big{display:none!important}")
    await pg.evaluate(STATE)
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, ROSTER, "null"))
    await pg.evaluate(STATE)
    await pg.evaluate("()=>{Game.refreshWagon()}")
    await pg.evaluate(film3.NODRV)
    return ctx, pg

def pop(el, t0):
    return "{const q=t-%f,e=document.getElementById('%s');if(e)e.style.transform=`scale(${q<0?0:(q<.28?B(q/.28):1)})`}" % (t0, el)

def comment(i, top, nick, txt, hearts, col):
    return (f'<div class="cmx" id="cm{i}" style="top:{top}px"><div class="av" style="background:{col}"></div>'
            f'<div class="tx"><small>@{nick}</small>{txt}</div><div class="hr">{hearts}</div></div>')

async def interior(pg, w, c=None):
    c = c or CAMI
    await pg.evaluate(f"()=>{{Game.flyTo({w},.12)}}"); await steps(pg, 260)
    await pg.evaluate(film12.cam_js(w), c); await steps(pg, 5)
    await pg.evaluate(fx("{const k=t;window.__cam=[%f-k*.25,%f-k*.03,%f-k*.4,%f,%f,%f]}" % tuple(c)))

async def shot(name, b):
    ctx, pg = await mk(b)
    if name == "q1_write":      # 0–2,03: Napiš do komentářů číslo vagónu
        await pg.evaluate("()=>{Game.flyTo(900,.7)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Do komentářů</div><div class="ttl">Napiš číslo<br><y>vagónu</y> 💬</div>'))
        await setfull(pg, comment(0, 1150, "martin_k", "Ukaž vagón 777! 🙏", "", "#f0a03a") + comment(1, 1330, "lucka.v", "Co je v 1500? 👀", "", "#2b9fc2") + comment(2, 1510, "fanda_06", "Já chci vidět 42!", "", "#3f8a5c"))
        await pg.evaluate(fx(ease + pop("cm0", .3) + pop("cm1", .8) + pop("cm2", 1.3)))
        await film.record(pg, name, 2.03, cues={0: "()=>{Game.flyTo(900,.6)}"})
    elif name == "q2_show":     # 2,03–4,12: a já ti ukážu, co v něm je!
        await pg.evaluate("()=>{Game.flyTo(%d,.6)}" % DOG); await steps(pg, 240)
        await pg.evaluate(ov('<div class="eb">Ukážu ti</div><div class="ttl">Co v něm<br><y>je!</y> 🔍</div>'))
        await film.record(pg, name, 2.09, cues={T(.2): "()=>{Game.flyTo(%d,.12)}" % (DOG + 3)})
    elif name == "q3_diff":     # 4,12–5,87: Každý vagón je jiný.
        await pg.evaluate("()=>{Game.flyTo(300,.2)}"); await steps(pg, 240)
        await pg.evaluate(ov('<div class="eb">Každý vagón</div><div class="ttl huge"><y>Je jiný!</y></div>'))
        await film.record(pg, name, 1.75, cues={0: "()=>{Game.flyTo(306,.2)}"})
    elif name == "q4_dog":      # 5,87–7,98: Tady sedí cestující se psem…
        await interior(pg, DOG, [.2, 2.9, 5.8, -1.3, 1.9, -.2])
        await pg.evaluate(ov(f'<div class="eb">Vagón № {DOG}</div><div class="ttl">Cestující<br><y>se psem</y> 🐶</div>'))
        await film.record(pg, name, 2.11)
    elif name == "q5_guit":     # 7,98–9,89: tady někdo hraje na kytaru…
        await interior(pg, GUIT)
        await pg.evaluate(ov(f'<div class="eb">Vagón № {GUIT}</div><div class="ttl">Hraje na<br><y>kytaru</y> 🎸</div>'))
        await film.record(pg, name, 1.91)
    elif name == "q6_gold":     # 9,89–12,92: a tady má někdo dokonce zlatou lopatu!
        await interior(pg, GOLDW)
        await pg.evaluate(ov(f'<div class="eb">Vagón № {GOLDW:,}</div>'.replace(",", " ") + '<div class="ttl">Dokonce<br><y>zlatou lopatu!</y> ✨</div>'))
        await film.record(pg, name, 3.03)
    elif name == "q7_likes":    # 12,92–15,81: Nejlajkovanější čísla ukážu v dalším videu.
        await pg.evaluate("()=>{Game.flyTo(1200,.75)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Nejvíc ❤️</div><div class="ttl">V dalším<br><y>videu!</y> 🎬</div>'))
        await setfull(pg, '<div style="position:absolute;inset:0;background:rgba(20,30,40,.3)"></div>' + comment(0, 1060, "martin_k", "Ukaž vagón 777! 🙏", "❤️ 312", "#f0a03a") + comment(1, 1240, "lucka.v", "Co je v 1500? 👀", "❤️ 248", "#2b9fc2") + comment(2, 1420, "fanda_06", "Já chci vidět 42!", "❤️ 197", "#3f8a5c"))
        await pg.evaluate(fx(ease + pop("cm0", .1) + pop("cm1", .45) + pop("cm2", .8)))
        await film.record(pg, name, 2.89)
    elif name == "q8_end":      # 15,81–konec: A jestli ještě nemáš svůj vagón, dej follow a nastup. Odkaz je v biu!
        await pg.evaluate("()=>{Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Nemáš ještě vagón?</div><div class="ttl">Dej follow<br><y>a nastup!</y></div>'))
        await setfull(pg, '<div style="position:absolute;left:0;right:0;top:1330px;text-align:center"><span id="fb" style="display:inline-block;background:#2f6f9f;color:#fff;border-radius:22px;padding:24px 56px;font:800 66px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)">➕ Sledovat</span>'
                      '<div id="ht" style="margin-top:46px;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div></div>')
        js = ease + "{const s=t-1.7;const e=document.getElementById('fb');e.style.transform=`scale(${s<0?0:(s<.3?B(s/.3):1+.03*Math.sin(s*5))})`;document.getElementById('ht').style.opacity=t<2.4?0:Math.min(1,(t-2.4)/.3)}"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6.02, cues={T(3.44): ov('<div class="eb">Odkaz na web</div><div class="ttl">Je v <y>biu!</y> 👆</div>')})
    await ctx.close()

ALL = ["q1_write", "q2_show", "q3_diff", "q4_dog", "q5_guit", "q6_gold", "q7_likes", "q8_end"]

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
