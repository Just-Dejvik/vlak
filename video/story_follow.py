# Obrázek do Stories: „Máš jízdenku, ale nedal(a) jsi follow?“ (1080×1920 PNG)
import asyncio, base64, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/story-follow.png"

ME = json.dumps({"nick": "tvuj.nick", "wagon": 12, "status": "pending", "public": True,
                 "avatar": {"coat": "#2f6f9f", "hat": "cepice", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}})

CSS = r"""
#st{position:fixed;inset:0;z-index:99;pointer-events:none;font-family:IS,sans-serif}
#st .top{position:absolute;left:70px;right:70px;top:250px;text-align:center}
#st .eb{display:inline-block;font:600 34px PM,monospace;letter-spacing:.16em;text-transform:uppercase;color:#fff;background:#1e2a33;padding:12px 26px;border-radius:999px}
#st h1{margin:34px 0 0;font:900 150px/.88 BS,sans-serif;text-transform:uppercase;color:#fff;text-shadow:0 8px 0 rgba(20,40,60,.35),0 0 40px rgba(20,40,60,.25)}
#st h1 y{color:#ffd23f}
#st .warn{display:inline-block;margin-top:38px;background:#cf4630;color:#fff;font:800 58px/1.1 IS,sans-serif;padding:22px 38px;border-radius:28px;box-shadow:0 12px 0 #8f2b1c;transform:rotate(-2deg)}
#st .bot{position:absolute;left:60px;right:60px;bottom:250px;background:#fffaf0;border-radius:40px;border:6px solid #f0a03a;padding:34px 44px;box-shadow:0 24px 60px rgba(0,0,0,.3)}
#st .bot .h{font:900 64px/1 BS,sans-serif;text-transform:uppercase;color:#1e2a33;margin-bottom:18px}
#st .bot ol{margin:0;padding:0;list-style:none;display:grid;gap:16px}
#st .bot li{display:flex;gap:20px;align-items:center;font:600 42px/1.2 IS,sans-serif;color:#1e2a33}
#st .bot li i{flex:none;width:66px;height:66px;border-radius:50%;background:#f0a03a;color:#fff;font:900 44px/66px BS,sans-serif;text-align:center;font-style:normal}
#st .bot b{color:#c4453a}
.lbl{display:none!important}
"""

HTML = """<div class="top"><span class="eb">@vlak.followeru</span>
<h1>Máš jízdenku,<br>ale nedal(a)<br>jsi <y>follow?</y></h1>
<div class="warn">Do 4 dnů ti vagón propadne! 🚂</div></div>
<div class="bot"><div class="h">Zachraň svůj vagón</div><ol>
<li><i>1</i><span>Dej follow <b>@vlak.followeru</b></span></li>
<li><i>2</i><span>Na webu zkontroluj, že máš <b>správný nick</b></span></li></ol></div>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx, pg = await film2.mkpage(b)
        await pg.route("**/api/world*", lambda r: r.abort())
        await pg.evaluate(film2.TRAIN % (24, film3.roster(24), ME))
        await pg.evaluate("()=>{Game.flyTo(12,.12);Game.setShift(-.1)}")
        await film2.steps(pg, 160)
        await pg.add_style_tag(content=CSS)
        await pg.evaluate("h=>{const d=document.createElement('div');d.id='st';d.innerHTML=h;document.body.appendChild(d);document.getElementById('ov').innerHTML=''}", HTML)
        await film2.steps(pg, 3)
        sess = await pg.context.new_cdp_session(pg)
        r = await sess.send("Page.captureScreenshot", {"format": "png"})
        open(OUT, "wb").write(base64.b64decode(r["data"]))
        await ctx.close(); await b.close()
    print(OUT)

asyncio.run(main())
