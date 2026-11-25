# Díl 17: „Hýbej palcem do rytmu“ – pozvánka na uhelný event přesně na hudbu z virálního videa
# (147 BPM, akce na každou druhou dobu = 0,816 s; 7 scén po 8 dobách jako v předloze).
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film3, film4, film5, film12, film14, film15
from thumb import thumb_svg, thumb_js
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
T, steps, fx, ease = film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
B = 0.4079                    # doba v hudbě (kopák každých 0,408 s od 0,006 s)
S = 8 * B                     # jedna scéna = 8 dob
END = 22.96                   # délka písničky
NAMES = ["s1_thumb", "s2_coal", "s3_count", "s4_gold", "s5_train", "s6_avatar", "s7_end"]
FB = [round(i * S * 30) for i in range(len(NAMES))] + [round(END * 30)]
LEN = {n: (FB[i + 1] - FB[i]) / 30 for i, n in enumerate(NAMES)}

CSS = r"""
#tt{position:absolute;left:0;right:0;top:250px;text-align:center;font:800 76px/1.15 IS,sans-serif;color:#111}
#tt small{display:block;font:700 50px IS,sans-serif;color:#333;margin-top:14px}
.pz{position:absolute;left:0;right:0;text-align:center}
.pz span{display:inline-block;border-radius:999px;padding:24px 50px;font:800 64px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.3)}
.bigc{position:absolute;left:0;right:0;text-align:center;font:900 200px/1 BS,sans-serif;color:#ffd27a;-webkit-text-stroke:12px #3a1606;paint-order:stroke fill}
#coal .c-top,#coal .c-prog,#coal .c-me,#coal .c-hint,#coal .c-msg,#coal .c-top5,#coal .c-pl,#coal .c-sub{display:none!important}
"""
DARK = "background:#1f1712;color:#fff;box-shadow:0 0 50px rgba(255,120,30,.6),0 12px 30px rgba(0,0,0,.3)"
GOLD = "background:linear-gradient(#ffe27a,#f0b323);color:#3a2600;box-shadow:0 0 50px rgba(255,200,40,.8),0 12px 30px rgba(0,0,0,.3)"
WHITE = "background:#fff;color:#1e2a33"

def pop(el, t0):
    """Vyskočí v čase t0 (s) a pak se lehce pohupuje do rytmu."""
    return "{const q=t-%f,e=document.getElementById('%s');if(e)e.style.transform=`scale(${q<0?0:(q<.22?B(q/.22):1+.035*Math.max(0,1-((t%%%f)/%f)*3))})`}" % (t0, el, 2 * B, 2 * B)

def throws():
    sw = film15.SWIPE
    return {T(2 * k * B): "()=>(%s)(%d)" % (sw, [0, -18, 14, -6][k]) for k in range(4)}

async def coal_page(b, gold=False):
    ctx, pg = await film15.mk_c(b, coal=False, api="hang")
    await pg.evaluate("()=>{window.__coalFly=%f}" % (B - .16))
    await pg.add_style_tag(content=CSS)
    if gold:
        await pg.evaluate("()=>{S.goldShovels=['tvuj.nick']}")
    await pg.evaluate("()=>{openCoal()}")
    await pg.wait_for_timeout(800)
    for _ in range(20): await pg.evaluate("__step(33.33)")
    return ctx, pg

async def site_page(b):
    ctx, pg = await film15.mk_s(b)
    await pg.add_style_tag(content=CSS)
    await film14.train(pg)
    return ctx, pg

async def shot(name, b):
    L = LEN[name]
    if name == "s1_thumb":      # palec na čistém pozadí, jako v předloze
        ctx, pg = await site_page(b)
        await setfull(pg, '<div style="position:absolute;inset:0;background:#bfe6f7"></div>'
                      '<div id="tt">Hýbej palcem do rytmu<small>🔥 uhelný event</small></div>' + thumb_svg("th"))
        await pg.evaluate(fx(thumb_js("th", B)))
        await film.record(pg, name, L)
    elif name == "s2_coal":
        ctx, pg = await coal_page(b)
        await setfull(pg, f'<div class="pz" style="top:260px"><span id="c1" style="{DARK}">🔥 Házej uhlí do kotle</span></div>')
        await pg.evaluate(fx(ease + pop("c1", .0)))
        await film.record(pg, name, L, cues=throws())
    elif name == "s3_count":
        ctx, pg = await coal_page(b)
        await setfull(pg, '<div class="bigc" id="km" style="top:1150px;transform:scale(0)">+100 km! 🚂</div>'
                      '<div style="position:absolute;left:60px;right:60px;top:260px;background:rgba(20,14,10,.78);border-radius:44px;padding:30px 40px;box-shadow:inset 0 0 0 3px rgba(255,170,80,.3)">'
                      '<div style="display:flex;align-items:baseline;gap:18px"><span id="ct" style="display:inline-block;font:800 130px/1 BS,sans-serif;color:#ffd27a;transform-origin:0 70%">0</span><span style="font:600 52px IS,sans-serif;color:#e8d9c4">/ 40 000 lopat</span></div>'
                      '<div style="height:38px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin-top:22px"><i id="cb" style="display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,#ff5a1f,#ffb02e,#ffe27a);box-shadow:0 0 30px rgba(255,140,40,.8)"></i></div></div>')
        # číslo skočí v okamžiku, kdy uhlí dopadne do kotle (liché doby)
        js = ease + ("{const n=Math.max(0,Math.min(4,Math.floor((t-%f)/%f)+1));const v=10000*n;const f=((t-%f)%%%f)/%f;"
                     "const el=document.getElementById('ct');el.textContent=v.toLocaleString('cs-CZ');el.style.transform=`scale(${n>0?1+.28*Math.max(0,1-f*4):1})`;"
                     "document.getElementById('cb').style.width=(v/400)+'%%'}" % (B, 2 * B, B, 2 * B, 2 * B)) + pop("km", 7 * B)
        await pg.evaluate(fx(js))
        await film.record(pg, name, L, cues=throws())
    elif name == "s4_gold":
        ctx, pg = await coal_page(b, gold=True)
        await setfull(pg, f'<div class="pz" style="top:260px"><span id="g1" style="{GOLD}">🏆 Top 5 = zlatá lopata ✨</span></div>')
        await pg.evaluate(fx(ease + pop("g1", .0)))
        await film.record(pg, name, L, cues=throws())
    elif name == "s5_train":
        ctx, pg = await site_page(b)
        await pg.evaluate("()=>{Game.flyTo(1700,.85)}"); await steps(pg, 200)
        await setfull(pg, '<div class="bigc" style="top:1120px;color:#fff;-webkit-text-stroke:12px #13324a"><span id="kc" style="display:inline-block">+0</span> km</div>'
                      f'<div class="pz" style="top:300px"><span id="v1" style="{WHITE}">🚂 Splníme cíl a vlak poskočí</span></div>')
        js = ease + pop("v1", 0) + ("{const n=Math.max(0,Math.min(4,Math.floor(t/%f)+1));const f=(t%%%f)/%f;const e=document.getElementById('kc');e.textContent='+'+(25*n);e.style.transform=`scale(${1+.22*Math.max(0,1-f*4)})`}" % (2 * B, 2 * B, 2 * B))
        await pg.evaluate(fx(js))
        cues = {T(2 * k * B): "()=>{Game.flyTo(%d,.%d)}" % (1700 - k * 420, 82 - k * 6) for k in range(4)}
        await film.record(pg, name, L, cues=cues)
    elif name == "s6_avatar":
        ctx, pg = await site_page(b)
        await pg.evaluate("()=>{S.goldShovels=[%s];Game.refreshWagon()}" % json.dumps(film15.GSN))
        await pg.evaluate(f"()=>{{Game.flyTo({film15.GSW},.12)}}"); await steps(pg, 260)
        await pg.evaluate(film12.cam_js(film15.GSW), [1.6, 2.75, 4.2, .15, 2.15, -.6]); await steps(pg, 5)
        await pg.add_style_tag(content=".lbl.big{display:none!important}")
        await setfull(pg, f'<div class="pz" style="top:300px"><span id="a1" style="{GOLD}">✨ Zlatá lopata do vagónu</span></div>')
        # kamera se na každou druhou dobu přiblíží „úderem“
        js = ease + pop("a1", 0) + ("{const n=Math.floor(t/%f),f=(t%%%f)/%f;const z=n*.22+.22*E(Math.min(1,f/.25));window.__cam=[1.6-z*.55,2.75-z*.06,4.2-z*.75,.15,2.15,-.6]}" % (2 * B, 2 * B, 2 * B))
        await pg.evaluate(fx(js))
        await film.record(pg, name, L)
    elif name == "s7_end":
        ctx, pg = await site_page(b)
        await pg.evaluate("()=>{Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await setfull(pg, '<div id="tt" style="top:230px;color:#fff;text-shadow:0 5px 0 rgba(20,40,60,.4)">Házej uhlí doopravdy!</div>'
                      f'<div class="pz" style="top:470px"><span id="e1" style="{DARK}">🔥 Dnes 16:00–19:00</span></div>'
                      f'<div class="pz" style="top:620px"><span id="e2" style="{WHITE}">Odkaz na web je v biu 👆</span></div>' + thumb_svg("th"))
        await pg.evaluate(fx(ease + pop("e1", 0) + pop("e2", 2 * B) + thumb_js("th", B)))
        await film.record(pg, name, L)
    await ctx.close()

async def main():
    names = sys.argv[1:] or NAMES
    os.makedirs(f"{ROOT}/clips", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            await shot(n, b)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
