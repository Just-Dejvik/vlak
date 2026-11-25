# Díl 16: „Švihni prstem do rytmu“ (150 BPM, sedí na zvuk z předlohy) – pozvánka na uhelný event ve stylu interaktivních rytmických videí.
# Bez hlasu: na každou dobu (140 BPM) prst švihne a lopata hodí uhlí; každé 3,4 s nová scéna.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film14, film15
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
T, steps, fx, ease = film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
BPM = 150
B = 60 / BPM
OFF = 0.13          # první doba ve zvuku z předlohy
SCENE = 8 * B

CSS = r"""
#rt{position:absolute;left:40px;right:40px;top:120px;text-align:center;font:900 92px/1.02 BS,sans-serif;color:#fff;text-transform:uppercase;
  -webkit-text-stroke:10px #111;paint-order:stroke fill;letter-spacing:.01em}
#rt small{display:block;font-size:62px;margin-top:8px}
#fing{position:absolute;left:0;top:0;font-size:330px;line-height:1;filter:drop-shadow(0 0 0 #fff) drop-shadow(0 14px 18px rgba(0,0,0,.45))}
.pz{position:absolute;left:0;right:0;text-align:center}
.pz span{display:inline-block;border-radius:999px;padding:22px 46px;font:800 62px/1 IS,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,.3)}
.bigc{position:absolute;left:0;right:0;text-align:center;font:900 200px/1 BS,sans-serif;color:#ffd27a;-webkit-text-stroke:12px #3a1606;paint-order:stroke fill}
#coal .c-top,#coal .c-prog,#coal .c-me,#coal .c-hint,#coal .c-msg,#coal .c-top5,#coal .c-pl,#coal .c-sub{display:none!important}
"""
TITLE = '<div id="rt">Švihni prstem<br>do rytmu! 🔥<small>(uhelný event)</small></div>'
FING = '<div id="fing">👆</div>'
# prst: na každou dobu rychle nahoru, pak pomalu zpátky
FING_JS = ("{const F=document.getElementById('fing');if(F){const b=%f;const t0=t-(window.__off||0);const k=t0<0?.99:(t0%%b)/b;const up=k<.22?E(k/.22):1-E((k-.22)/.78);"
           "F.style.transform=`translate(${520+Math.sin(Math.floor(Math.max(0,t0)/b)*1.7)*30}px,${1430-up*360}px) rotate(${-8+up*10}deg)`}}" % B)

def throws(n=8, off=0):
    sw = film15.SWIPE
    return {T(off + k * B): "()=>(%s)(%d)" % (sw, [0, -20, 15, -8, 10, -15, 5, 0][k % 8]) for k in range(n)}

async def coal_page(b, gold=False):
    ctx, pg = await film15.mk_c(b, coal=False, api="hang")
    await pg.add_init_script("window.__coalFly=.24")
    await pg.evaluate("()=>{window.__coalFly=.24}")
    await pg.add_style_tag(content=CSS + "#rt,#fing,.pz,.bigc{zoom:1}")
    if gold:
        await pg.evaluate("()=>{S.goldShovels=['tvuj.nick']}")
    await pg.evaluate("()=>{openCoal()}")
    await pg.wait_for_timeout(800)
    for _ in range(20): await pg.evaluate("__step(33.33)")
    return ctx, pg

async def shot(name, b):
    if name == "r1_coal":
        ctx, pg = await coal_page(b)
        await setfull(pg, TITLE + FING)
        await pg.evaluate("()=>{window.__off=%f}" % OFF)
        await pg.evaluate(fx(ease + FING_JS))
        await film.record(pg, name, OFF + SCENE, cues=throws(off=OFF))
    elif name == "r2_count":
        ctx, pg = await coal_page(b)
        await setfull(pg, TITLE + FING + '<div class="bigc" id="km" style="top:1150px;opacity:0">+100 km! 🚂</div>'
                      '<div style="position:absolute;left:60px;right:60px;top:430px;background:rgba(20,14,10,.75);border-radius:44px;padding:30px 40px;box-shadow:inset 0 0 0 3px rgba(255,170,80,.3)">'
                      '<div style="display:flex;align-items:baseline;gap:18px"><span id="ct" style="display:inline-block;font:800 120px/1 BS,sans-serif;color:#ffd27a;transform-origin:0 70%">0</span><span style="font:600 50px IS,sans-serif;color:#e8d9c4">/ 40 000 lopat</span></div>'
                      '<div style="height:36px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin-top:22px"><i id="cb" style="display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,#ff5a1f,#ffb02e,#ffe27a);box-shadow:0 0 30px rgba(255,140,40,.8)"></i></div></div>')
        js = ease + FING_JS + (";{const k=Math.min(7,Math.floor(t/%f)),u=(t%%%f)/%f;const v=5000*(k+1);"
              "const el=document.getElementById('ct');el.textContent=v.toLocaleString('cs-CZ');el.style.transform=`scale(${1+.25*Math.max(0,1-u*4)})`;"
              "document.getElementById('cb').style.width=(v/400)+'%%';const km=document.getElementById('km');const q=t-7*%f;km.style.opacity=q<0?0:1;km.style.transform=`scale(${q<0?0:(q<.25?B(q/.25):1)})`}") % (B, B, B, B)
        await pg.evaluate(fx(js))
        await film.record(pg, name, SCENE, cues=throws())
    elif name == "r3_gold":
        ctx, pg = await coal_page(b, gold=True)
        await setfull(pg, TITLE + FING + '<div class="pz" style="top:420px"><span id="gc" style="background:linear-gradient(#ffe27a,#f0b323);color:#3a2600;box-shadow:0 0 50px rgba(255,200,40,.8),0 12px 30px rgba(0,0,0,.3)">🏆 Top 5 = zlatá lopata ✨</span></div>')
        await pg.evaluate(fx(ease + FING_JS + ";{const q=t;document.getElementById('gc').style.transform=`scale(${q<.25?B(q/.25):1+.03*Math.sin(q*9)})`}"))
        await film.record(pg, name, SCENE, cues=throws())
    elif name == "r4_train":
        ctx, pg = await film15.mk_s(b)
        await pg.add_style_tag(content=CSS)
        await film14.train(pg)
        await pg.evaluate("()=>{Game.flyTo(1700,.85)}"); await steps(pg, 200)
        await setfull(pg, TITLE + FING + '<div class="bigc" style="top:1120px;color:#fff;-webkit-text-stroke:12px #13324a"><span id="kc">+0</span> km</div>'
                      '<div class="pz" style="top:1350px"><span style="background:#fff;color:#1e2a33">🚂 vlak jede dopředu</span></div>')
        js = ease + FING_JS + ";{const k=Math.min(7,Math.floor(t/%f));const u=(t%%%f)/%f;const e=document.getElementById('kc');e.textContent='+'+Math.round(12.5*(k+1));e.parentNode.style.transform=`scale(${1+.18*Math.max(0,1-u*4)})`}" % (B, B, B)
        await pg.evaluate(fx(js))
        cues = {T(k * B): "()=>{Game.flyTo(%d,.%d)}" % (1700 - k * 230, 85 - k * 3) for k in range(8)}
        await film.record(pg, name, SCENE, cues=cues)
    elif name == "r5_end":
        ctx, pg = await film15.mk_s(b)
        await pg.add_style_tag(content=CSS)
        await film14.train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await setfull(pg, '<div id="rt" style="top:150px">Házej uhlí<br>doopravdy! 🔥</div>'
                      '<div class="pz" style="top:1180px"><span id="e1" style="background:#1f1712;color:#fff;box-shadow:0 0 50px rgba(255,120,30,.6),0 12px 30px rgba(0,0,0,.3);transform:scale(0)">🔥 Dnes 16:00–19:00</span></div>'
                      '<div class="pz" style="top:1330px"><span id="e2" style="background:#fff;color:#1e2a33;transform:scale(0)">Odkaz na web je v biu 👆</span></div>')
        js = ease + "{const s=t-.05;document.getElementById('e1').style.transform=`scale(${s<0?0:(s<.3?B(s/.3):1+.03*Math.sin(s*5))})`;const r=t-%f;document.getElementById('e2').style.transform=`scale(${r<0?0:(r<.3?B(r/.3):1)})`}" % (2 * B)
        await pg.evaluate(fx(js))
        await film.record(pg, name, 6 * B + 2.2)
    await ctx.close()

ALL = ["r1_coal", "r2_count", "r3_gold", "r4_train", "r5_end"]

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
