# Díl 15: Uhelný event – dnes 16:00–19:00, švihni prstem a hoď uhlí do kotle, 40 000 lopat = +100 km dopředu, top 5 zlatá lopata.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film11, film12, film14
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
TOK = open("/tmp/claude-0/ftok").read().strip()
ME = {"nick": "tvuj.nick", "token": TOK, "wagon": 1816, "status": "pending", "public": True,
      "avatar": {"coat": "#2f6f9f", "hat": "koruna", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}}
ROSTER = json.loads(film12.roster())
C2LEN = float(os.environ.get('C2LEN', '4.32'))
GSW = 12                      # vagón s vymyšleným cestujícím se zlatou lopatou
GSN = next(e[1] for e in ROSTER if e[0] == GSW)

EXTRA_C = r"""
#ov,#full{zoom:.33333}
#ov{z-index:500!important}#full{z-index:450!important}
#ov .eb{margin-top:445px!important}#ov .ttl{font-size:100px!important;margin-top:18px!important}
#coal .c-top5,#coal .c-pl,#coal .c-sub{display:none!important}
.hand{position:fixed;z-index:400;font-size:64px;pointer-events:none;filter:drop-shadow(0 6px 10px rgba(0,0,0,.5));opacity:0}
.tagb{position:absolute;left:0;right:0;top:1560px;text-align:center}
.tagb span{display:inline-block;background:linear-gradient(#ffe27a,#f0b323);color:#3a2600;border-radius:999px;padding:24px 46px;font:800 66px/1 IS,sans-serif;box-shadow:0 0 50px rgba(255,200,40,.75),0 12px 30px rgba(0,0,0,.3);transform:scale(0)}
.timec{position:absolute;left:0;right:0;top:1180px;text-align:center}
.timec span{display:inline-block;background:#fff;color:#1e2a33;border-radius:34px;padding:26px 50px;font:900 120px/1 BS,sans-serif;box-shadow:0 14px 0 rgba(0,0,0,.25),0 0 60px rgba(255,140,40,.6);transform:scale(0)}
.kmc{position:absolute;left:0;right:0;top:1200px;text-align:center;font:900 230px/1 BS,sans-serif;color:#fff;text-shadow:0 10px 0 rgba(20,40,60,.4)}
.kmc small{display:block;font:800 60px IS,sans-serif;margin-top:10px}
"""

async def mk_c(b, ticket=True, coal=True, api='fake', total=12480):
    """Telefonní pohled (360×640 @3×) – minihra i tlačítko eventu vypadají jako v mobilu."""
    ctx = await b.new_context(viewport={"width": 360, "height": 640}, device_scale_factor=3, has_touch=True)
    pg = await ctx.new_page()
    pg._vf_scale = 3
    pg.on("pageerror", lambda e: print("PAGEERR", e, file=sys.stderr))
    await pg.add_init_script(film.INIT)
    me = dict(ME)
    await pg.add_init_script("window.__coalDpr=3;" + ("localStorage.setItem('vf.myticket.v3',%s)" % json.dumps(json.dumps(me)) if ticket else "localStorage.removeItem('vf.myticket.v3')"))
    await pg.route("**/three.min.js", lambda r: r.fulfill(body=film.THREE, content_type="application/javascript"))
    await pg.route("**/__f/*", lambda r: r.fulfill(body=film.FONTS[r.request.url.rsplit("/", 1)[1]], content_type="font/ttf"))
    st = {"total": total, "mine": 0}
    async def coal_api(route):
        r = route.request
        if api == "real": return await route.continue_()
        if api == "hang": return await route.abort()   # čísla řídí animace
        if r.method == "POST":
            n = json.loads(r.post_data or "{}").get("n", 1); st["mine"] += n; st["total"] += n * 37
            return await route.fulfill(content_type="application/json", body=json.dumps({"added": n, "total": st["total"], "mine": st["mine"], "done": False, "goal": 40000}))
        resp = await route.fetch(); d = await resp.json()
        d.update(total=st["total"], players=318, top=[], mine=st["mine"])
        await route.fulfill(content_type="application/json", body=json.dumps(d))
    await pg.route("**/api/coal*", coal_api)
    await pg.goto("http://localhost:3457/", wait_until="domcontentloaded")
    for _ in range(40):
        await pg.evaluate("__step(33.33)"); await pg.wait_for_timeout(60)
    await pg.add_style_tag(content=film.CSS + EXTRA_C)
    await pg.evaluate("""()=>{const o=document.createElement('div');o.id='ov';document.body.appendChild(o);
      const f=document.createElement('div');f.id='full';document.body.appendChild(f);document.querySelector('#boarding').hidden=true;
      const h=document.createElement('div');h.className='hand';h.id='hand';h.textContent='👆';document.body.appendChild(h)}""")
    await pg.evaluate(film14.STATE)
    await pg.evaluate(film2.TRAIN % (film14.N, json.dumps(ROSTER), json.dumps(me) if ticket else "null"))
    await pg.evaluate(film14.STATE)
    await pg.wait_for_timeout(1500)   # stav eventu ze serveru
    await pg.evaluate("()=>{renderCoalPill()}")
    for _ in range(10): await pg.evaluate("__step(33.33)")
    if coal:
        await pg.evaluate("()=>{openCoal()}")
        await pg.wait_for_timeout(1200)
        for _ in range(20): await pg.evaluate("__step(33.33)")
    return ctx, pg

SWIPE = """(dx)=>{const c=document.querySelector('#coal canvas');const o={bubbles:true,pointerId:7,pointerType:'touch',isPrimary:true};
c.dispatchEvent(new PointerEvent('pointerdown',{...o,clientX:180,clientY:520}));c.dispatchEvent(new PointerEvent('pointermove',{...o,clientX:180+dx,clientY:420}));c.dispatchEvent(new PointerEvent('pointerup',{...o,clientX:180+dx,clientY:400}))}"""

def swipes(times, dxs=(0, -25, 20, -10, 15, 5)):
    """cue (snímek) → švih; ruka se pohne nahoru."""
    return {T(t): "()=>(%s)(%d)" % (SWIPE, dxs[i % len(dxs)]) for i, t in enumerate(times)}

def hand_js(times):
    # ruka: přijede zdola a švihne nahoru 0,18 s před hodem
    return ("const H=document.getElementById('hand');const A=%s;let on=0;for(const a of A){const k=t-a+.2;if(k>=0&&k<.45){on=1;const u=k/.45;H.style.left=(165+Math.sin(a*7)*8)+'px';H.style.top=(560-u*200)+'px';H.style.opacity=u<.15?u/.15:(u>.8?(1-u)/.2:1)}}if(!on)H.style.opacity=0" % json.dumps(times))

async def mk_s(b):
    ctx, pg = await film14.mk_w(b)
    await pg.add_style_tag(content="#coalPill{display:none!important}" + EXTRA_C.split("#coal .c-top5")[0].replace("#ov,#full{zoom:.33333}", "").replace("#ov{z-index:500!important}#full{z-index:450!important}", "").replace("#ov .eb{margin-top:445px!important}#ov .ttl{font-size:100px!important;margin-top:18px!important}", "") + EXTRA_C[EXTRA_C.index(".hand"):])
    return ctx, pg

async def shot(name, b):
    if name == "c1_coal":     # 0–2,13: Lokomotiva potřebuje uhlí!
        ctx, pg = await mk_s(b)
        await film14.train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.42)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Pozor, cestující!</div><div class="ttl">Lokomotiva<br>potřebuje<br><y>uhlí!</y></div>'))
        await film.record(pg, name, 2.13, cues={0: "()=>{Game.flyTo(0,.3)}"})
    elif name == "c2_event":  # 2,13–6,45: Dnes od 16 do 19 hodin se koná uhelný event.
        ctx, pg = await mk_c(b, api="hang")
        await pg.add_style_tag(content="#coal .c-top,#coal .c-prog,#coal .c-me,#coal .c-hint{opacity:0}")
        await pg.evaluate(ov('<div class="eb">🔥 Uhelný event</div><div class="ttl" style="font-size:190px!important;line-height:.95">V <y>PÁTEK!</y></div>'))
        await setfull(pg, '<div class="timec"><span id="tc">16:00 – 19:00</span></div>')
        await pg.evaluate(fx(ease + "const k=t-1.2;document.getElementById('tc').style.transform=`scale(${k<0?0:(k<.35?B(k/.35):1+.02*Math.sin(k*4))})`"))
        await film.record(pg, name, C2LEN, cues=swipes([.5, 2.0, 3.2]))
    elif name == "c3_open":   # 6,45–7,30: Otevři web,
        ctx, pg = await mk_c(b, coal=False)
        await pg.evaluate("()=>{Game.flyTo(1790,.6)}"); await steps(pg, 200)
        await pg.add_style_tag(content="#coalPill{top:330px!important;transform-origin:50% 50%}")
        await pg.evaluate(ov('<div class="eb">Krok 1</div><div class="ttl">Otevři<br><y>web</y></div>'))
        await pg.evaluate(fx("const H=document.getElementById('hand');const p=document.getElementById('coalPill').getBoundingClientRect();const u=Math.min(1,t/.45);H.style.left=(p.left+p.width/2-10)+'px';H.style.top=(p.bottom+40-u*40)+'px';H.style.opacity=Math.min(1,t/.15);document.getElementById('coalPill').style.transform=`translateX(-50%) scale(${t>.5?.92:1})`"))
        await film.record(pg, name, .85)
    elif name == "c3_swipe":  # 7,30–10,88: švihni prstem nahoru a lopatou hodíš uhlí do kotle.
        ctx, pg = await mk_c(b)
        await pg.evaluate(ov('<div class="eb">Krok 2</div><div class="ttl">Švihni<br><y>nahoru</y> 👆</div>'))
        times = [.45, 1.0, 1.5, 1.95, 2.4, 2.85, 3.3]
        await pg.evaluate(fx(hand_js(times)))
        await film.record(pg, name, 3.58, cues={**swipes(times), T(1.36): ov('<div class="eb">Krok 2</div><div class="ttl">Uhlí letí<br>do <y>kotle!</y> 🔥</div>')})
    elif name == "c4_goal":   # 10,88–13,74: Když společně naházíme 40 000 lopat,
        ctx, pg = await mk_c(b, api="hang", total=14000)
        await pg.add_style_tag(content="#coal .c-me{display:none!important}")
        await pg.evaluate(ov('<div class="eb">Společný cíl</div><div class="ttl"><y>40 000</y><br>lopat</div>'))
        times = [.3, .75, 1.2, 1.65, 2.1, 2.55]
        await pg.evaluate(fx(ease + hand_js(times) + ";const u=E(Math.min(1,t/2.6));const v=Math.round(14000+u*26000);document.getElementById('cTot').textContent=v.toLocaleString('cs-CZ');document.getElementById('cBar').style.width=(v/400)+'%'"))
        await film.record(pg, name, 2.86, cues=swipes(times))
    elif name == "c5_jump":   # 13,74–16,45: vlak poskočí o 100 km dopředu!
        ctx, pg = await mk_s(b)
        await film14.train(pg)
        await pg.evaluate("()=>{Game.flyTo(1500,.9)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Odměna</div><div class="ttl">Vlak<br><y>poskočí!</y> 🚂</div>'))
        await setfull(pg, '<div class="kmc"><span id="km">+0</span> km<small>dopředu</small></div>')
        await pg.evaluate(fx(ease + "const u=E(Math.min(1,Math.max(0,t-.3)/1.5));document.getElementById('km').textContent='+'+Math.round(u*100)"))
        await film.record(pg, name, 2.71, cues={0: "()=>{Game.flyTo(0,.75)}"})
    elif name == "c6_gold":   # 16,45–19,57: A pět nejlepších topičů dostane zlatou lopatu.
        ctx, pg = await mk_s(b)
        await film14.train(pg)
        await pg.evaluate("()=>{S.goldShovels=[%s];Game.refreshWagon()}" % json.dumps(GSN))
        await pg.evaluate(f"()=>{{Game.flyTo({GSW},.12)}}"); await steps(pg, 260)
        await pg.evaluate(film12.cam_js(GSW), [1.6, 2.75, 4.2, .15, 2.15, -.6]); await steps(pg, 5)
        await pg.add_style_tag(content=".lbl.big{display:none!important}")
        await pg.evaluate(fx("{const k=t;window.__cam=[1.6-k*.25,2.75-k*.04,4.2-k*.35,.15,2.15,-.6]}"))
        await pg.evaluate(ov('<div class="eb">Top 5 topičů</div><div class="ttl">Zlatá<br><y>lopata!</y> ✨</div>'))
        await setfull(pg, '<div class="tagb"><span id="gt">🏆 Top 5</span></div>')
        await pg.evaluate(fx(ease + "{const k=t;window.__cam=[1.6-k*.25,2.75-k*.04,4.2-k*.35,.15,2.15,-.6]};const k=t-.6;document.getElementById('gt').style.transform=`scale(${k<0?0:(k<.3?B(k/.3):1)})`"))
        await film.record(pg, name, 3.12)
    elif name == "c7_only":   # 19,57–23,19: Házet můžou jen cestující, tak dej follow a nastup.
        ctx, pg = await mk_c(b, ticket=False, total=23410)
        await pg.add_style_tag(content="#coal .c-me{display:none!important}")
        await pg.evaluate(ov('<div class="eb">Pozor</div><div class="ttl">Jen pro<br><y>cestující</y> 🎫</div>'))
        await film.record(pg, name, 3.62, cues={T(1.97): ov('<div class="eb">@vlak.followeru</div><div class="ttl">Dej follow<br><y>a nastup!</y></div>')})
    elif name == "c8_end":    # 23,19–konec: Odkaz na web je v biu!
        ctx, pg = await mk_s(b)
        await film14.train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.6);Game.setShift(-.13)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">Odkaz na web</div><div class="ttl">Je v <y>biu!</y> 👆</div>'))
        await setfull(pg, '<div style="position:absolute;left:0;right:0;top:1060px;text-align:center"><div id="tc" style="display:inline-block;transform:scale(0)"><div style="font:900 210px/1 BS,sans-serif;color:#ffd27a;-webkit-text-stroke:12px #3a1606;paint-order:stroke fill">V PÁTEK!</div><span style="display:inline-block;margin-top:14px;background:#1f1712;color:#fff;border-radius:999px;padding:24px 50px;font:800 70px/1 IS,sans-serif;box-shadow:0 0 50px rgba(255,120,30,.6),0 12px 30px rgba(0,0,0,.3)">🔥 16:00–19:00</span></div>'
                      '<div id="ht" style="margin-top:46px;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div></div>')
        await pg.evaluate(fx(ease + "const s=t-.15;document.getElementById('tc').style.transform=`scale(${s<0?0:(s<.35?B(s/.35):1+.03*Math.sin(s*5))})`;document.getElementById('ht').style.opacity=Math.min(1,Math.max(0,(t-.7)/.3))"))
        await film.record(pg, name, 3.0)
    await ctx.close()

ALL = ["c1_coal", "c2_event", "c3_open", "c3_swipe", "c4_goal", "c5_jump", "c6_gold", "c7_only", "c8_end"]

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
