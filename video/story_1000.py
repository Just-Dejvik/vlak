# Obrázek do Stories: „Díky za 1 000 sledujících!“ + výzva pro followery bez vagónu (1080×1920 PNG)
import asyncio, base64, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/story-1000.png"

ME = json.dumps({"nick": "tvuj.nick", "wagon": 12, "status": "pending", "public": True,
                 "avatar": {"coat": "#2f6f9f", "hat": "cepice", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}})

CSS = r"""
#st{position:fixed;inset:0;z-index:99;pointer-events:none;font-family:IS,sans-serif}
#st .top{position:absolute;left:70px;right:70px;top:250px;text-align:center}
#st .eb{display:inline-block;font:600 34px PM,monospace;letter-spacing:.16em;text-transform:uppercase;color:#fff;background:#1e2a33;padding:12px 26px;border-radius:999px}
#st h1{margin:30px 0 0;font:900 170px/.86 BS,sans-serif;text-transform:uppercase;color:#fff;text-shadow:0 8px 0 rgba(20,40,60,.35),0 0 40px rgba(20,40,60,.25)}
#st h1 y{color:#ffd23f}
#st .thx{display:inline-block;margin-top:30px;background:#fff;color:#1e2a33;font:800 50px/1.1 IS,sans-serif;padding:18px 34px;border-radius:999px;box-shadow:0 10px 0 rgba(20,40,60,.25)}
#st .conf{position:absolute;inset:0}
#st .warn{display:inline-block;margin-top:38px;background:#cf4630;color:#fff;font:800 58px/1.1 IS,sans-serif;padding:22px 38px;border-radius:28px;box-shadow:0 12px 0 #8f2b1c;transform:rotate(-2deg)}
#st .bot{position:absolute;left:60px;right:60px;bottom:250px;background:#fffaf0;border-radius:40px;border:6px solid #f0a03a;padding:34px 44px;box-shadow:0 24px 60px rgba(0,0,0,.3)}
#st .bot .h{font:900 60px/1 BS,sans-serif;text-transform:uppercase;color:#1e2a33;margin-bottom:18px}
#st .bot ol{margin:0;padding:0;list-style:none;display:grid;gap:16px}
#st .bot li{display:flex;gap:20px;align-items:center;font:600 42px/1.2 IS,sans-serif;color:#1e2a33}
#st .bot li i{flex:none;width:66px;height:66px;border-radius:50%;background:#f0a03a;color:#fff;font:900 44px/66px BS,sans-serif;text-align:center;font-style:normal}
#st .bot b{color:#c4453a}
.lbl{display:none!important}
"""

HTML = """<div class="conf"><i style="position:absolute;left:351px;top:294px;width:20px;height:31px;background:#ffd23f;transform:rotate(137deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:116px;top:514px;width:23px;height:31px;background:#e07a9b;transform:rotate(54deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:58px;top:228px;width:20px;height:43px;background:#ffd23f;transform:rotate(61deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:112px;top:704px;width:20px;height:31px;background:#e07a9b;transform:rotate(31deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:990px;top:368px;width:24px;height:48px;background:#ffd23f;transform:rotate(147deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:619px;top:546px;width:14px;height:37px;background:#ffd23f;transform:rotate(142deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:899px;top:276px;width:18px;height:43px;background:#c4453a;transform:rotate(138deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:140px;top:724px;width:18px;height:47px;background:#fff;transform:rotate(46deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:125px;top:735px;width:23px;height:36px;background:#3f8a5c;transform:rotate(24deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:580px;top:204px;width:23px;height:31px;background:#e07a9b;transform:rotate(52deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:528px;top:684px;width:20px;height:40px;background:#2f6f9f;transform:rotate(149deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:965px;top:604px;width:19px;height:39px;background:#c4453a;transform:rotate(46deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:735px;top:389px;width:15px;height:48px;background:#3f8a5c;transform:rotate(134deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:526px;top:491px;width:25px;height:44px;background:#3f8a5c;transform:rotate(155deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:1023px;top:214px;width:15px;height:46px;background:#2f6f9f;transform:rotate(42deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:795px;top:490px;width:16px;height:45px;background:#2f6f9f;transform:rotate(10deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:1005px;top:219px;width:26px;height:47px;background:#e07a9b;transform:rotate(80deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:368px;top:498px;width:23px;height:45px;background:#e07a9b;transform:rotate(116deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:90px;top:235px;width:18px;height:45px;background:#fff;transform:rotate(170deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:86px;top:202px;width:25px;height:39px;background:#fff;transform:rotate(147deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:1036px;top:596px;width:18px;height:42px;background:#fff;transform:rotate(88deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:43px;top:612px;width:19px;height:35px;background:#e07a9b;transform:rotate(29deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:525px;top:200px;width:17px;height:39px;background:#c4453a;transform:rotate(63deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:427px;top:540px;width:21px;height:32px;background:#c4453a;transform:rotate(114deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:431px;top:702px;width:18px;height:34px;background:#2f6f9f;transform:rotate(140deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:305px;top:565px;width:19px;height:42px;background:#c4453a;transform:rotate(38deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:104px;top:320px;width:16px;height:37px;background:#fff;transform:rotate(59deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:32px;top:636px;width:23px;height:35px;background:#3f8a5c;transform:rotate(72deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:24px;top:289px;width:20px;height:47px;background:#3f8a5c;transform:rotate(156deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:599px;top:466px;width:16px;height:46px;background:#e07a9b;transform:rotate(167deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:712px;top:195px;width:21px;height:47px;background:#2f6f9f;transform:rotate(101deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:428px;top:543px;width:15px;height:45px;background:#fff;transform:rotate(102deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:83px;top:335px;width:15px;height:36px;background:#2f6f9f;transform:rotate(41deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:132px;top:488px;width:23px;height:31px;background:#ffd23f;transform:rotate(0deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:600px;top:294px;width:22px;height:33px;background:#3f8a5c;transform:rotate(157deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:46px;top:212px;width:17px;height:42px;background:#c4453a;transform:rotate(162deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:278px;top:495px;width:23px;height:41px;background:#2f6f9f;transform:rotate(31deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:138px;top:639px;width:21px;height:45px;background:#2f6f9f;transform:rotate(79deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:107px;top:287px;width:15px;height:40px;background:#fff;transform:rotate(67deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:510px;top:305px;width:22px;height:30px;background:#c4453a;transform:rotate(135deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:390px;top:290px;width:25px;height:47px;background:#ffd23f;transform:rotate(135deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:325px;top:233px;width:25px;height:38px;background:#e07a9b;transform:rotate(93deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:950px;top:311px;width:19px;height:37px;background:#e07a9b;transform:rotate(138deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:817px;top:654px;width:19px;height:37px;background:#e07a9b;transform:rotate(49deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:845px;top:385px;width:20px;height:37px;background:#c4453a;transform:rotate(132deg);border-radius:4px;opacity:.95"></i><i style="position:absolute;left:524px;top:504px;width:25px;height:30px;background:#ffd23f;transform:rotate(71deg);border-radius:4px;opacity:.95"></i></div><div class="top"><span class="eb">@vlak.followeru</span>
<h1>Díky za<br><y>1 000</y><br>sledujících!</h1>
<div class="thx">Jste nejlepší posádka 🚂💛</div></div>
<div class="bot"><div class="h">Sleduješ nás, ale nemáš vagón?</div><ol>
<li><i>1</i><span>Klikni na <b>odkaz v biu</b></span></li>
<li><i>2</i><span>Napiš svůj <b>instagramový nick</b></span></li>
<li><i>3</i><span>Nastup do <b>svého vagónu</b> 🎫</span></li></ol></div>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome",
                                    args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx, pg = await film2.mkpage(b)
        await pg.route("**/api/world*", lambda r: r.abort())
        await pg.evaluate(film2.TRAIN % (60, film3.roster(60), "null"))
        await pg.evaluate("()=>{Game.flyTo(14,.5);Game.setShift(-.06)}")
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
