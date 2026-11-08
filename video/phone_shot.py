# Snímek webu „jako na mobilu“ pro záběr s telefonem (díl 5): vagón № 3 s panáčkem, bez toastu.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3
from playwright.async_api import async_playwright
OUT = sys.argv[1]
ME = {"nick": "tvuj.nick", "wagon": 3, "status": "pending", "public": True,
      "avatar": {"coat": "#2f6f9f", "hat": "koruna", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg = await ctx.new_page()
        await pg.route("**/three.min.js", lambda r: r.fulfill(body=film.THREE, content_type="application/javascript"))
        await pg.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(body="""@font-face{font-family:'Big Shoulders Display';src:url(/__f/bs);font-weight:100 900}@font-face{font-family:'Instrument Sans';src:url(/__f/is);font-weight:100 900}@font-face{font-family:'IBM Plex Mono';src:url(/__f/pm);font-weight:400 600}""", content_type="text/css"))
        await pg.route("**/__f/*", lambda r: r.fulfill(body=film.FONTS[r.request.url.rsplit("/", 1)[1]], content_type="font/ttf"))
        await pg.route("**/api/world*", lambda r: r.abort())
        await pg.add_init_script("sessionStorage.setItem('vf.seen','1')")
        await pg.goto(film2.URL); await pg.wait_for_timeout(2500)
        await pg.evaluate(film2.TRAIN % (160, film3.roster(40), json.dumps(ME)))
        await pg.evaluate("()=>{S.peak=160;S.kmPerPassenger=1;S.route=['praha','kolin'];S.vote={at:'kolin',deadline:'',options:[{to:'pardubice',votes:11},{to:'hbrod',votes:2}]};renderHud()}")
        await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{Game.flyTo(3,0)}"); await pg.wait_for_timeout(400); print(await pg.evaluate("()=>[Game.flying(), Game.N, Game.zoom, Game.center()]")); await pg.wait_for_timeout(45000); print(await pg.evaluate("()=>[Game.flying(), Game.zoom, Game.center()]"))
        await pg.screenshot(path=OUT)
        await b.close()
asyncio.run(main())
