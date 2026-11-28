# Díl 19: „Zastav video a najdi svůj vagón“ – bez hlasu, jen hudba. Rychlé titulky se všemi veřejnými nicky
# (skryté nicky se na webu ani tady neukazují), na začátku celý vlak shora, na konci výzva nastoupit.
import asyncio, html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film12
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
REAL = json.load(open(os.path.join(ROOT, "data", "roster_real.json")))     # veřejné nicky z webu
N = max(e[0] for e in REAL)
ROUTE = film12.ROUTE
STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.bonusKm=100;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};S.supporters=%s;renderHud()}"
         % (N, N, json.dumps(ROUTE), json.dumps(film12.SUP)))
LIST_T = 15.6

EXTRA = r"""
#lst{position:absolute;inset:0;background:linear-gradient(#173248,#0f2233)}
#lh{position:absolute;left:0;right:0;top:0;height:370px;z-index:3;background:linear-gradient(#173248 78%,rgba(23,50,72,0));text-align:center;padding-top:110px}
#lh b{display:block;font:900 120px/1 BS,sans-serif;color:#ffd23f;text-transform:uppercase;letter-spacing:.01em}
#lh span{display:block;font:800 56px IS,sans-serif;color:#fff;margin-top:12px}
#lf{position:absolute;left:0;right:0;bottom:0;height:190px;z-index:3;background:linear-gradient(rgba(15,34,51,0),#0f2233 45%);text-align:center;padding-top:100px;font:700 40px IS,sans-serif;color:#cfe0ee}
#rows{position:absolute;left:30px;right:30px;top:0;display:grid;grid-template-columns:repeat(3,1fr);gap:12px 16px;will-change:transform}
.wc{background:#fff;border-radius:14px;padding:6px 12px 7px;border-left:12px solid #999;overflow:hidden;white-space:nowrap}
.wc i{display:block;font:600 22px/1.1 PM,monospace;color:#7b8a97;font-style:normal}
.wc u{display:block;text-decoration:none;font:800 29px/1.15 IS,sans-serif;color:#1e2a33;overflow:hidden;text-overflow:ellipsis}
.pz{position:absolute;left:0;right:0;text-align:center}
.pz span{display:inline-block;border-radius:999px;padding:24px 50px;font:800 64px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.3)}
"""

def list_html():
    cards = "".join(f'<div class="wc" style="border-left-color:{html.escape(a.get("coat", "#999"))}"><i>#{w}</i><u>@{html.escape(n)}</u></div>' for w, n, a, *_ in sorted(REAL, key=lambda e: e[0]))
    return ('<div id="lst"><div id="rows">' + cards + '</div>'
            '<div id="lh"><b>⏸️ Zastav video</b><span>a najdi svůj vagón 👀</span></div>'
            f'<div id="lf">{len(REAL):,} cestujících · vagóny #1 až #{N:,}</div></div>'.replace(",", " "))

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=film12.EXTRA + EXTRA + "#coalPill{display:none!important}")
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, json.dumps(REAL), "null"))
    await pg.evaluate(STATE)
    await pg.evaluate(film3.NODRV)

async def shot(name, b):
    ctx, pg = await mk(b)
    if name == "f1_intro":
        await train(pg)
        await pg.evaluate("()=>{Game.setOverview(true,true)}"); await steps(pg, 90)
        await pg.evaluate(ov('<div class="eb">%s vagónů</div><div class="ttl">Najdi svůj<br><y>vagón!</y> 👀</div>' % f"{N:,}".replace(",", " ")))
        await film.record(pg, name, 2.4)
    elif name == "f2_list":
        await setfull(pg, list_html())
        await pg.evaluate("()=>{const r=document.getElementById('rows');window.__H=r.offsetHeight}")
        js = "{const r=document.getElementById('rows');const H=window.__H;const top=380,end=1920-200;const u=Math.max(0,Math.min(1,t/%f));r.style.transform=`translateY(${top-u*(H-(end-top))}px)`}" % LIST_T
        await pg.evaluate(fx(js))
        await film.record(pg, name, LIST_T)
    elif name == "f3_end":
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Nenašel ses? 😢</div><div class="ttl">Nastup<br><y>a buď tu!</y></div>'))
        await setfull(pg, '<div class="pz" style="top:1300px"><span id="e1" style="background:#fff;color:#1e2a33;transform:scale(0)">Odkaz na web je v biu 👆</span></div>')
        await pg.evaluate(fx(ease + "{const q=t-.35;document.getElementById('e1').style.transform=`scale(${q<0?0:(q<.3?B(q/.3):1+.03*Math.sin(q*5))})`}"))
        await film.record(pg, name, 3.6)
    await ctx.close()

ALL = ["f1_intro", "f2_list", "f3_end"]

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
