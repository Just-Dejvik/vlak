# Díl 13: Výhybka – milionář vs. 20 lidí (tramvajové dilema). Vlastní 3D scéna trolley.html.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T = film2.ov, film3.T
PAGE = open(f"{ROOT}/trolley.html", "rb").read()
EXTRA = r"""
#ov .eb{margin-top:190px}
.opt2{position:fixed;left:70px;right:70px;top:1330px;z-index:70;display:grid;grid-template-columns:1fr 1fr;gap:24px}
.opt2 div{font:900 84px/1 BS,sans-serif;text-transform:uppercase;text-align:center;color:#fff;border-radius:26px;padding:28px 0;box-shadow:0 10px 0 rgba(0,0,0,.25);transform:scale(0)}
"""

async def mk(b):
    ctx = await b.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg = await ctx.new_page()
    pg.on("pageerror", lambda e: print("PAGEERR", e, file=sys.stderr))
    pg.on("console", lambda m: print("CONSOLE", m.text, file=sys.stderr) if m.type == "error" else None)
    await pg.add_init_script(film.INIT)
    await pg.route("**/three.min.js", lambda r: r.fulfill(body=film.THREE, content_type="application/javascript"))
    await pg.route("**/__f/*", lambda r: r.fulfill(body=film.FONTS[r.request.url.rsplit("/", 1)[1]], content_type="font/ttf"))
    await pg.route("http://trolley.local/", lambda r: r.fulfill(body=PAGE, content_type="text/html"))
    await pg.goto("http://trolley.local/", wait_until="domcontentloaded")
    for _ in range(60):
        if await pg.evaluate("!!window.__ready"): break
        await pg.evaluate("__step(33.33)"); await pg.wait_for_timeout(100)
    await pg.add_style_tag(content=film.CSS + EXTRA)
    await pg.evaluate("()=>{const o=document.createElement('div');o.id='ov';document.body.appendChild(o);const f=document.createElement('div');f.id='full';document.body.appendChild(f)}")
    for _ in range(5): await pg.evaluate("__step(33.33)")
    return ctx, pg

def opts(t0):
    html = '<div class="opt2"><div id="oA" style="background:#c99a1e">💰 Milionář</div><div id="oB" style="background:#2f6f9f">👥 Lidi</div></div>'
    js = film4.ease + f"const a=t-{t0[0]},b=t-{t0[1]};document.getElementById('oA').style.transform=`scale(${{a<0?0:(a<.3?B(a/.3):1)}})`;document.getElementById('oB').style.transform=`scale(${{b<0?0:(b<.3?B(b/.3):1)}})`"
    return html, js

async def shot(pg, name):
    S = lambda n, **o: pg.evaluate("([n,o])=>SHOT(n,o)", [n, o])
    full = lambda h: pg.evaluate("h=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='70';f.innerHTML=h}", h)
    if name == "t1_intro":      # 0–2,81: Cestou do Paříže jsme narazili na tohle…
        await S("a_intro")
        await pg.evaluate(ov('<div class="eb">Cesta do Paříže</div><div class="ttl">Narazili jsme<br><y>na tohle…</y></div>'))
        await film.record(pg, name, 2.85)
    elif name == "t2_switch":   # 2,81–3,81: Výhybka!
        await S("b_switch")
        await pg.evaluate(ov('<div class="eb">⚠️ Pozor</div><div class="ttl huge"><y>Výhybka!</y></div>'))
        await film.record(pg, name, 1.0)
    elif name == "t3_both":     # 3,81–6,42: A na obou kolejích jsou přivázaní lidi!
        await S("c_both")
        await pg.evaluate(ov('<div class="eb">Na obou kolejích</div><div class="ttl">Přivázaní<br><y>lidi!</y></div>'))
        await film.record(pg, name, 2.62)
    elif name == "t4_left":     # 6,42–9,35: Vlevo milionář…
        await S("d_left")
        await pg.evaluate(ov('<div class="eb">Vlevo</div><div class="ttl"><y>Milionář</y></div>'))
        await film.record(pg, name, 1.42)
    elif name == "t5_mil":      # 9,35–15,55: „Zachraňte mě a dám vám TURBO! Vlak pojede dvakrát rychleji a každý dostane cylindr!“
        await S("e_mil", bub="Zachraňte mě a dám vám <y>TURBO!</y> 🚀")
        await pg.evaluate(ov(''))
        cues = {T(2.45): "()=>BUB('Vlak pojede <y>2× rychleji</y>…')",
                T(4.55): "()=>BUB('…a každý dostane <y>CYLINDR!</y> 🎩')"}
        await film.record(pg, name, 6.2, cues=cues)
    elif name == "t6_right":    # 15,55–18,43: Vpravo dvacet lidí… a nenabízí nic.
        await S("f_right")
        await pg.evaluate(ov('<div class="eb">Vpravo</div><div class="ttl"><y>20 lidí</y></div>'))
        await film.record(pg, name, 3.45, cues={T(1.74): ov('<div class="eb">Nabízí</div><div class="ttl huge">Nic 🤷</div>')})
    elif name == "t7_lever":    # 18,43–21,82: Rozhodujete vy. Napište MILIONÁŘ, nebo LIDI.
        await S("g_lever")
        await pg.evaluate(ov('<div class="eb">Páka je v tvých rukou</div><div class="ttl">Rozhodujete<br><y>vy!</y></div>'))
        h, js = opts((1.25, 2.69))
        await full(h); await pg.evaluate(film4.fx(js))
        await film.record(pg, name, 3.75, cues={T(1.25): ov('<div class="eb">Napište do komentářů</div><div class="ttl">Milionář,<br><y>nebo lidi?</y></div>')})
    elif name == "t8_eject":    # 21,82–26,93: Ale pozor: když vyhraje milionář, vylosuju 20 jeho voličů a ty z vlaku vyhodím.
        await S("h_eject")
        await pg.evaluate(ov('<div class="eb">Ale pozor!</div><div class="ttl">Když vyhraje<br><y>milionář…</y></div>'))
        await film.record(pg, name, 6.05, cues={T(2.56): ov('<div class="eb">Vylosuju</div><div class="ttl">20 jeho<br><y>voličů…</y></div>'),
                                               T(4.38): ov('<div class="eb">A ty</div><div class="ttl huge"><y>Vyhodím!</y></div>')})
    elif name == "t9_risk":     # 26,93–28,76: Takže… riskneš to?
        await S("i_risk")
        await full('<div style="position:absolute;inset:0;background:radial-gradient(circle,rgba(0,0,0,0) 35%,rgba(0,0,0,.6))"></div>')
        await pg.evaluate(ov('<div class="eb">Takže…</div><div class="ttl huge">Riskneš<br><y>to?</y></div>'))
        await film.record(pg, name, 1.83)
    elif name == "t10_end":     # 28,76–30,67 (+dojezd): Výsledek bude v příštím videu!
        await S("j_end")
        await pg.evaluate(ov('<div class="eb">Hlasuj v komentářích 👇</div><div class="ttl">Výsledek<br><y>příště!</y></div>'))
        h, js = opts((.2, .35))
        await full(h); await pg.evaluate(film4.fx(js))
        await film.record(pg, name, 3.5)

ALL = ["t1_intro", "t2_switch", "t3_both", "t4_left", "t5_mil", "t6_right", "t7_lever", "t8_eject", "t9_risk", "t10_end"]

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
