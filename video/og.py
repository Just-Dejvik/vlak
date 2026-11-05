import asyncio,sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await b.new_context(viewport={"width":1200,"height":630})
        pg=await ctx.new_page()
        await pg.add_init_script(film.INIT)
        await pg.route("**/three.min.js",lambda r:r.fulfill(body=film.THREE,content_type="application/javascript"))
        await pg.route("https://fonts.*/**",lambda r:r.abort())
        await pg.route("**/__f/*",lambda r:r.fulfill(body=film.FONTS[r.request.url.rsplit("/",1)[1]],content_type="font/ttf"))
        await pg.goto(os.environ.get("VLAK_URL", "http://localhost:3457/"),wait_until="domcontentloaded")
        for _ in range(30):
            await pg.evaluate("__step(33.33)");await pg.wait_for_timeout(40)
        await pg.add_style_tag(content=film.CSS+"""
#ov{align-items:flex-start;padding-left:70px}
#ov .eb{margin-top:70px;font-size:22px}
#ov .ttl{font-size:120px;text-align:left;padding:0;margin-top:18px}
#ov .chip{font-size:30px;margin-top:22px;padding:10px 22px}
#labels{display:none}""")
        await pg.evaluate("""()=>{const o=document.createElement('div');o.id='ov';document.body.appendChild(o);document.querySelector('#boarding').hidden=true;
          ONLINE=true;S.followers=40;setRoster([]);myTicket=null;Game.setN(40);Game.refreshWagon();Game.flyTo(1,.62)}""")
        for _ in range(200): await pg.evaluate("__step(33.33)")
        await pg.evaluate("""()=>{document.getElementById('ov').innerHTML='<div class="eb">vlak-followeru.vercel.app</div><div class="ttl">Vlak<br><y>followerů</y></div><div class="chip">Každý follow = <b>jeden vagón</b></div>'}""")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "og.jpg"),type="jpeg",quality=88)
        await b.close()
asyncio.run(main())
