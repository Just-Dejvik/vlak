# Díl 2: záběry pro Reels „Ty vole, jen 8 ve vlaku“.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 30
URL = os.environ.get("VLAK_URL", "http://localhost:3457/")
NICKS = ["jana.n", "petr_k", "eva.v", "ondra.m", "klara.z", "tom_b", "misa.r", "adam_j"]
AV = ["#c4453a", "#2f6f9f", "#3f8a5c", "#d9a13b", "#7a4fa3", "#e07a9b", "#2b2f3a", "#e8e0cc"]
HATS = ["koruna", "ksilt", "klobouk", "cepice", "zadna", "koruna", "ksilt", "klobouk"]

EXTRA_CSS = r"""
.lbl.anon{display:none!important}
.lbl{font-size:28px!important;padding:8px 20px!important}
.lbl.big{font-size:46px!important;padding:16px 36px!important;border-radius:24px!important}
.lbl.big small{font-size:26px!important}
#ov .ttl.huge{font-size:230px}
#ov .chip.sm{font-size:38px}
.tap{position:fixed;width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,.55);border:6px solid #fff;transform:translate(-50%,-50%) scale(0);z-index:120;pointer-events:none}
"""

def roster(n=8):
    return json.dumps([[i + 1, NICKS[i], {"coat": AV[i], "hat": HATS[i], "pet": "zadny", "item": "nic",
                                          "hair": "#2a1c14", "skin": "#f1c9a5"}] for i in range(n)])

def ticket(av):
    return json.dumps({"nick": "tvuj.nick", "wagon": 1, "status": "verified", "public": True, "avatar": av})

TRAIN = "()=>{ONLINE=true;S.followers=%d;setRoster(%s);myTicket=%s;Game.setN(wagonCount());Game.refreshWagon()}"

async def mkpage(b):
    ctx = await b.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg = await ctx.new_page()
    pg.on("pageerror", lambda e: print("PAGEERR", e, file=sys.stderr))
    await pg.add_init_script(film.INIT)
    await pg.route("**/three.min.js", lambda r: r.fulfill(body=film.THREE, content_type="application/javascript"))
    await pg.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(body="""@font-face{font-family:'Big Shoulders Display';src:url(/__f/bs);font-weight:100 900}@font-face{font-family:'Instrument Sans';src:url(/__f/is);font-weight:100 900}@font-face{font-family:'IBM Plex Mono';src:url(/__f/pm);font-weight:400 600}""", content_type="text/css"))
    await pg.route("**/__f/*", lambda r: r.fulfill(body=film.FONTS[r.request.url.rsplit("/", 1)[1]], content_type="font/ttf"))
    await pg.goto(URL, wait_until="domcontentloaded")
    for _ in range(40):
        await pg.evaluate("__step(33.33)"); await pg.wait_for_timeout(50)
    await pg.add_style_tag(content=film.CSS + EXTRA_CSS)
    await pg.evaluate("""()=>{const o=document.createElement('div');o.id='ov';document.body.appendChild(o);
      const f=document.createElement('div');f.id='full';document.body.appendChild(f);
      document.querySelector('#boarding').hidden=true;closeSheet&&closeSheet(true)}""")
    await pg.evaluate("""()=>Promise.race([Promise.all(['900 100px BS','700 40px IS','800 40px IS','600 30px PM','900 100px "Big Shoulders Display"','800 100px "Big Shoulders Display"','400 30px "Instrument Sans"','600 30px "Instrument Sans"','700 30px "Instrument Sans"','800 30px "Instrument Sans"','500 30px "IBM Plex Mono"','600 30px "IBM Plex Mono"'].map(f=>document.fonts.load(f))),new Promise(r=>setTimeout(r,4000))])""")
    await pg.wait_for_timeout(300)
    return ctx, pg

async def steps(pg, n):
    for _ in range(n): await pg.evaluate("__step(33.333)")

def ov(html):
    return f"()=>{{document.getElementById('ov').innerHTML={json.dumps(html)}}}"

async def shot(pg, name):
    if name == "h1_hook":   # kamera vletí do prázdného vagónu
        await pg.evaluate(TRAIN % (16, roster(8), "null"))
        await pg.evaluate("()=>{__G.avatarSlot.add=function(){return this};__G.petSlot.add=function(){return this}}")
        await pg.evaluate("()=>{Game.flyTo(12,1)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="ttl huge" style="margin-top:300px">Ty <y>vole!</y></div>'))
        cues = {int(1.30 * FPS): ov('<div class="eb">Vlak followerů</div><div class="ttl"><y>16</y> followerů<br>jen <y>8</y> ve vlaku?!</div><div class="chip">tenhle vagón je <b>prázdný</b></div>')}
        await pg.evaluate("()=>{Game.flyTo(12,0)}")
        await film.record(pg, name, 6.5, cues=cues)
    elif name == "h2_pan":   # let podél vlaku, nicky má jen přední polovina
        await pg.evaluate(TRAIN % (16, roster(8), "null"))
        await pg.evaluate("()=>{Game.flyTo(15,.55)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Pozor</div><div class="ttl">Follow<br><y>nestačí</y></div><div class="chip">vagón dostaneš <b>s jízdenkou z webu</b></div>'))
        cues = {int(.5 * FPS): "()=>{Game.flyTo(3,.5)}"}
        await film.record(pg, name, 5.5, cues=cues)
    elif name == "h3a_type":   # nástupiště: píše se nick
        await pg.evaluate(TRAIN % (16, roster(8), "null"))
        await pg.evaluate("()=>{Game.flyTo(4,.8)}"); await steps(pg, 120)
        await pg.add_style_tag(content=".boarding{display:grid!important;zoom:2.05;top:46%!important}#ov{display:none}")
        await pg.evaluate("()=>{openBoarding();document.querySelector('#bNick').value=''}")
        nick = "tvuj.nick"
        cues = {}
        for i in range(len(nick) + 1):
            cues[int((.15 + i * .1) * FPS)] = f"()=>{{document.querySelector('#bNick').value={json.dumps('@' + nick[:i])}}}"
        cues[int(1.35 * FPS)] = """()=>{const b=document.querySelector('#bForm button[type=submit]');b.style.transform='scale(.92)';b.style.filter='brightness(.92)';
          const r=b.getBoundingClientRect();const t=document.createElement('div');t.className='tap';t.id='tapc';t.style.left=(r.left+r.width/2)*2.05+'px';t.style.top=(r.top+r.height/2)*2.05+'px';document.body.appendChild(t);
          const t0=__vt();window.__onframe=vt=>{const u=Math.min(1,(vt-t0)/350);t.style.transform=`translate(-50%,-50%) scale(${.3+u})`;t.style.opacity=1-u}}"""
        cues[int(1.75 * FPS)] = "()=>{const b=document.querySelector('#bForm button[type=submit]');b.style.transform='';b.style.filter='';b.textContent='Vydávám…'}"
        await film.record(pg, name, 3, cues=cues)
        # (cues se předávají níž – record s cues)
    elif name == "h3b_avatar":   # převlékání panáčka do rytmu slov
        av = {"coat": "#2f6f9f", "hat": "zadna", "pet": "zadny", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}
        await pg.evaluate(TRAIN % (16, roster(8), ticket(av)))
        await pg.evaluate("()=>{Game.flyTo(1,0)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Uvnitř sedíš ty</div><div class="ttl">Tvůj<br><y>panáček</y></div><div class="chip" id="avchip">vyber si, co mu sluší</div>'))
        def ch(hat=None, pet=None, chip=""):
            js = "()=>{"
            if hat: js += f"myTicket.avatar.hat='{hat}';"
            if pet: js += f"myTicket.avatar.pet='{pet}';"
            js += f"Game.refreshWagon();document.getElementById('avchip').innerHTML={json.dumps(chip)}}}"
            return js
        cues = {int(2.45 * FPS): ch("cepice", None, "na hlavě: <b>kulich</b>"),
                int(3.20 * FPS): ch("koruna", None, "na hlavě: <b>koruna</b>"),
                int(3.85 * FPS): ch(None, "pes", "+ spolucestující: <b>pes</b>")}
        await film.record(pg, name, 6, cues=cues)
    elif name == "h4_story":   # sdílení do Stories
        av = {"coat": "#2f6f9f", "hat": "koruna", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}
        await pg.evaluate(TRAIN % (16, roster(8), ticket(av)))
        await pg.evaluate("()=>{Game.flyTo(1,0)}"); await steps(pg, 150)
        url = await pg.evaluate("""async()=>{const b=await makeShareImage(Game.capture(1080,1300),myTicket);return URL.createObjectURL(b)}""")
        await pg.evaluate("()=>{Game.flyTo(1,.45)}"); await steps(pg, 90)
        await pg.evaluate(ov('<div class="eb">Pak se pochlub</div><div class="ttl">Sdílej svůj<br><y>vagón</y></div>'))
        await pg.evaluate("""url=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='98';
          f.innerHTML=`<div id="dim" style="position:absolute;inset:0;background:rgba(20,35,45,.35)"></div>
          <button id="shb" style="position:absolute;left:50%;top:1150px;transform:translate(-50%,-50%);font:800 64px 'Instrument Sans';background:#f0a03a;color:#1d1408;border:0;border-radius:28px;padding:36px 70px;box-shadow:0 14px 34px rgba(0,0,0,.25)">Sdílet do Stories</button>
          <div id="story" style="position:absolute;left:50%;top:760px;width:640px;height:1138px;transform:translate(-50%,1300px);border-radius:36px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.4);border:8px solid #fff;background:#000">
            <img src="${url}" style="width:100%;height:100%;object-fit:cover;display:block">
            <div style="position:absolute;left:18px;right:18px;top:16px;height:7px;background:rgba(255,255,255,.4);border-radius:4px;overflow:hidden"><i id="prog" style="display:block;height:100%;width:0;background:#fff"></i></div>
            <div style="position:absolute;left:22px;top:38px;display:flex;gap:12px;align-items:center;font:700 26px 'Instrument Sans';color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.5)"><span style="width:44px;height:44px;border-radius:50%;background:#2f6f9f;border:3px solid #fff"></span>tvuj.nick <span style="opacity:.8;font-weight:500">teď</span></div>
          </div>`;
          const t0=__vt();window.__onframe=vt=>{const t=(vt-t0)/1000;const b=document.getElementById('shb'),s=document.getElementById('story');
            if(t>1.1&&t<1.45){b.style.transform=`translate(-50%,-50%) scale(${t<1.25?.93:1})`}
            const u=Math.min(1,Math.max(0,(t-1.45)/.55)),e=1-Math.pow(1-u,3);s.style.transform=`translate(-50%,${(1-e)*1300}px)`;
            b.style.opacity=u>0?Math.max(0,1-u*2):1;
            document.getElementById('prog').style.width=Math.max(0,Math.min(100,(t-2)*28))+'%'}}""", url)
        await film.record(pg, name, 5.2)
    elif name == "h5a_map":
        await pg.evaluate(film.MAP)
        await pg.add_style_tag(content="#ov .opts div{transition:none}#ov .opts div.on{background:#ffd23f;color:#1e2a33;box-shadow:0 10px 0 #c9a12a;transform:scale(1.08)}")
        await pg.evaluate(ov('<div class="eb">Pořád stojíme v Praze</div><div class="ttl">Kam<br><y>vyjedeme?</y></div><div style="height:470px"></div><div class="opts"><div id="o0">Kolín</div><div id="o1">Plzeň</div><div id="o2">Ústí</div><div id="o3">Tábor</div></div>'))
        def on(i):
            return "()=>{document.querySelectorAll('#ov .opts div').forEach(d=>d.classList.remove('on'));" + (f"document.getElementById('o{i}').classList.add('on')" if i >= 0 else "") + "}"
        cues = {int(1.35 * FPS): on(0), int(1.95 * FPS): on(1), int(2.55 * FPS): on(2), int(3.2 * FPS): on(3), int(3.9 * FPS): on(-1)}
        await film.record(pg, name, 5, cues=cues)
    elif name == "h5b_cta":
        await pg.evaluate("()=>{document.getElementById('full').style.display='none'}")
        await pg.evaluate(TRAIN % (16, roster(8), "null"))
        await pg.evaluate("()=>{Game.flyTo(0,.22)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Piš do<br><y>komentářů</y></div><div class="chip">jízdenka je <b>v biu</b></div>'))
        cues = {int(1.15 * FPS): ov('<div class="eb">@vlak.followeru</div><div class="ttl huge" style="font-size:200px">A <y>nastup!</y></div><div class="chip">jízdenka je <b>v biu</b></div>'),
                int(.2 * FPS): "()=>{Game.flyTo(1,.36)}"}
        await film.record(pg, name, 3.6, cues=cues)

H3A_CUES = None

async def main():
    names = sys.argv[1:] or ["h1_hook", "h2_pan", "h3a_type", "h3b_avatar", "h4_story", "h5a_map", "h5b_cta"]
    os.makedirs(f"{ROOT}/clips", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for n in names:
            ctx, pg = await mkpage(b)
            await shot(pg, n)
            await ctx.close()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
