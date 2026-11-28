# Díl 21: Most nad propastí – hlasování MOST / OBJÍŽĎKA (kostka: přejedeme, nebo spadneme do řeky).
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film13
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, fx, ease = film2.ov, film3.T, film4.fx, film4.ease
PAGE = open(os.path.join(ROOT, "bridge.html"), encoding="utf-8").read()
EXTRA = film13.EXTRA + r"""
.opt2 div{min-width:0}
.dice2{position:absolute;left:0;right:0;top:1250px;display:grid;gap:26px;justify-items:center}
.dice2 div{font:800 64px/1 IS,sans-serif;color:#fff;padding:24px 44px;border-radius:999px;box-shadow:0 12px 30px rgba(0,0,0,.3);transform:scale(0)}
"""

async def mk(b):
    ctx = await b.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg = await ctx.new_page()
    pg.on("pageerror", lambda e: print("PAGEERR", e, file=sys.stderr))
    await pg.add_init_script(film.INIT)
    await pg.route("**/three.min.js", lambda r: r.fulfill(body=film.THREE, content_type="application/javascript"))
    await pg.route("**/__f/*", lambda r: r.fulfill(body=film.FONTS[r.request.url.rsplit("/", 1)[1]], content_type="font/ttf"))
    await pg.route("http://bridge.local/", lambda r: r.fulfill(body=PAGE, content_type="text/html"))
    await pg.goto("http://bridge.local/", wait_until="domcontentloaded")
    for _ in range(80):
        if await pg.evaluate("!!window.__ready"): break
        await pg.evaluate("__step(33.33)"); await pg.wait_for_timeout(100)
    await pg.add_style_tag(content=film.CSS + EXTRA)
    await pg.evaluate("()=>{const o=document.createElement('div');o.id='ov';document.body.appendChild(o);const f=document.createElement('div');f.id='full';document.body.appendChild(f)}")
    for _ in range(5): await pg.evaluate("__step(33.33)")
    return ctx, pg

def pops(ids, times):
    return ease + "".join("{const q=t-%f,e=document.getElementById('%s');e.style.transform=`scale(${q<0?0:(q<.3?B(q/.3):1+.03*Math.sin(q*5))})`}" % (tt, i) for i, tt in zip(ids, times))

PLAN = {  # název: (záběr ve scéně, délka)
    "b1_rush": ("a_rush", 1.25), "b1_gorge": ("b_gorge", 1.25), "b2_bridge": ("c_bridge", 5.06), "b3_plank": ("d_plank", 2.69),
    "b4_detour": ("e_detour", 4.58), "b5_lever": ("f_lever", 3.69), "b6_dice": ("h_dice", 3.16), "b7_cross": ("i_cross", 1.18),
    "b8_fall": ("j_fall", 4.04),
}

async def shot(name, b):
    ctx, pg = await mk(b)
    sc, L = PLAN[name]
    await pg.evaluate("([n,d])=>SHOT(n,{d})", [sc, L])
    full = lambda h: pg.evaluate("h=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='70';f.innerHTML=h}", h)
    cues = {}
    if name == "b1_rush":       # Vlak se řítí…
        await pg.evaluate(ov('<div class="eb">Pozor!</div><div class="ttl">Vlak se<br><y>řítí…</y></div>'))
    elif name == "b1_gorge":    # …k obrovské propasti!
        await pg.evaluate(ov('<div class="eb">Před námi je</div><div class="ttl huge"><y>Propast!</y> 😱</div>'))
    elif name == "b2_bridge":   # Vlevo je starý dřevěný most. Je to zkratka a ušetří nám 100 km…
        await pg.evaluate(ov('<div class="eb">Vlevo</div><div class="ttl">Starý<br><y>dřevěný most</y></div>'))
        cues = {T(2.04): ov('<div class="eb">Je to zkratka</div><div class="ttl">Ušetří<br><y>100 km!</y> 🚀</div>')}
    elif name == "b3_plank":    # …ale vrže a už z něj padají prkna.
        await pg.evaluate(ov('<div class="eb">Ale pozor…</div><div class="ttl">Padají z něj<br><y>prkna!</y> 😬</div>'))
    elif name == "b4_detour":   # Vpravo je objížďka přes hory. Bezpečná, ale nic nezískáme.
        await pg.evaluate(ov('<div class="eb">Vpravo</div><div class="ttl">Objížďka<br><y>přes hory</y> ⛰️</div>'))
        cues = {T(1.98): ov('<div class="eb">Bezpečná…</div><div class="ttl">Ale nic<br><y>nezískáme</y></div>')}
    elif name == "b5_lever":    # Rozhodujete vy! Napište MOST, nebo OBJÍŽĎKA.
        await pg.evaluate(ov('<div class="eb">Rozhodujete vy!</div><div class="ttl">Most, nebo<br><y>objížďka?</y></div>'))
        await full('<div class="opt2"><div id="oA" style="background:#b5302a">💀 Most</div><div id="oB" style="background:#2f6f9f">⛰️ Objížďka</div></div>')
        await pg.evaluate(fx(pops(["oA", "oB"], [1.21, 2.32])))
    elif name == "b6_dice":     # Ale pozor: když vyhraje most, hodím kostkou.
        await pg.evaluate(ov('<div class="eb">Když vyhraje most…</div><div class="ttl">Hodím<br><y>kostkou!</y> 🎲</div>'))
        await full('<div class="dice2"><div id="d1" style="background:#2f8a4a">🎲 1–3 · přejedeme ✅</div><div id="d2" style="background:#c0302a">🎲 4–6 · spadneme 💀</div></div>')
        await pg.evaluate(fx(pops(["d1", "d2"], [1.0, 1.9])))
    elif name == "b7_cross":    # Buď přejedeme…
        await pg.evaluate(ov('<div class="eb">Buď…</div><div class="ttl huge"><y>Přejedeme</y> ✅</div>'))
    elif name == "b8_fall":     # …nebo spadneme do řeky. Riskneš to?
        await pg.evaluate(ov('<div class="eb">…nebo</div><div class="ttl">Spadneme<br><y>do řeky!</y> 💀</div>'))
        cues = {T(1.78): ov('<div class="eb">Most, nebo objížďka?</div><div class="ttl huge"><y>Riskneš to?</y></div>')}
    await film.record(pg, name, L, cues=cues)
    await ctx.close()

async def main():
    names = sys.argv[1:] or list(PLAN)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            await shot(n, b)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
