# Natáčení záběrů pro Reels: virtuální čas, 1080x1920, titulky přímo ve scéně.
import asyncio, base64, json, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
THREE = open(f"{ROOT}/three.min.js", "rb").read()
FONTS = {"bs": open(f"{ROOT}/fonts/bs.ttf", "rb").read(), "is": open(f"{ROOT}/fonts/is.ttf", "rb").read(), "pm": open(f"{ROOT}/fonts/pm.ttf", "rb").read()}
FPS = 30

INIT = r"""
(()=>{
  let vt=0;const q=[];
  performance.now=()=>vt;
  window.requestAnimationFrame=cb=>{q.push(cb);return q.length};
  window.__step=ms=>{vt+=ms;const c=q.splice(0);c.forEach(f=>{try{f(vt)}catch(e){console.error(e)}});if(window.__onframe)window.__onframe(vt)};
  window.__vt=()=>vt;
  try{sessionStorage.setItem("vf.seen","1")}catch(e){}
})();
"""

CSS = r"""
@font-face{font-family:BS;src:url(/__f/bs) format("truetype");font-weight:100 900}
@font-face{font-family:IS;src:url(/__f/is) format("truetype");font-weight:100 900}
@font-face{font-family:PM;src:url(/__f/pm) format("truetype");font-weight:600}
.hud-top,.hud-bottom,#hint,.boarding,.sheet,.toast,.local-chip{display:none!important}
#ov{position:fixed;inset:0;pointer-events:none;z-index:99;display:flex;flex-direction:column;align-items:center}
#ov .eb{margin-top:200px;font:600 34px PM,monospace;letter-spacing:.18em;text-transform:uppercase;color:#fff;background:rgba(20,35,45,.55);padding:10px 22px;border-radius:999px}
#ov .ttl{margin-top:26px;font:900 132px/0.9 BS,sans-serif;text-transform:uppercase;text-align:center;color:#fff;padding:0 60px;
  text-shadow:0 6px 0 rgba(20,40,60,.55),0 10px 40px rgba(10,30,50,.45);letter-spacing:.01em}
#ov .ttl y{color:#ffd23f;display:inline}
#ov .chip{margin-top:34px;font:700 44px IS,sans-serif;color:#1e2a33;background:#fffaf0;border:4px solid #f0a03a;padding:16px 34px;border-radius:24px;box-shadow:0 12px 30px rgba(20,40,60,.3)}
#ov .chip b{font:inherit;color:#b45f12}
#ov .big{margin-top:30px;font:900 220px/1 BS,sans-serif;color:#fff;text-shadow:0 8px 0 rgba(20,40,60,.5);font-variant-numeric:tabular-nums}
#ov .opts{margin-top:40px;display:grid;grid-template-columns:1fr 1fr;gap:22px;width:860px}
#ov .opts div{font:900 76px/1 BS,sans-serif;text-transform:uppercase;text-align:center;background:#3d8a5a;color:#fff;border-radius:22px;padding:24px 0;box-shadow:0 10px 0 #2b6642}
#full{position:fixed;inset:0;z-index:50;display:none}
.lbl{font-size:28px!important;padding:8px 20px!important}
.lbl.big{font-size:46px!important;padding:16px 36px!important;border-radius:24px!important}
.lbl.big small{font-size:26px!important}
"""

async def mkpage(b):
    ctx = await b.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg = await ctx.new_page()
    pg.on("pageerror", lambda e: print("PAGEERR", e, file=sys.stderr))
    await pg.add_init_script(INIT)
    await pg.route("**/three.min.js", lambda r: r.fulfill(body=THREE, content_type="application/javascript"))
    await pg.route("https://fonts.*/**", lambda r: r.abort())
    await pg.route("**/__f/*", lambda r: r.fulfill(body=FONTS[r.request.url.rsplit("/", 1)[1]], content_type="font/ttf"))
    await pg.goto(os.environ.get("VLAK_URL", "http://localhost:3457/"), wait_until="domcontentloaded")
    for _ in range(40):
        await pg.evaluate("__step(33.33)")
        await pg.wait_for_timeout(50)
    await pg.add_style_tag(content=CSS)
    await pg.evaluate("""()=>{const o=document.createElement('div');o.id='ov';document.body.appendChild(o);
      const f=document.createElement('div');f.id='full';document.body.appendChild(f);
      document.querySelector('#boarding').hidden=true;document.fonts&&document.fonts.load('900 100px BS')}""")
    await pg.wait_for_timeout(400)
    return ctx, pg

async def snap(pg, path, quality=90):
    sess = getattr(pg, "_vf_cdp", None)
    if sess is None:
        sess = await pg.context.new_cdp_session(pg)
        pg._vf_cdp = sess
    r = await sess.send("Page.captureScreenshot", {"format": "jpeg", "quality": quality})
    with open(path, "wb") as f: f.write(base64.b64decode(r["data"]))

async def record(pg, name, seconds, warm=0, cues=None):
    out = f"{ROOT}/frames/{name}"
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for _ in range(int(warm * FPS)):
        await pg.evaluate("__step(33.333)")
    n = 1 if os.environ.get("PREVIEW") else int(seconds * FPS)
    pv = [float(x) for x in os.environ.get("PREVIEW_AT", "").split(",") if x]
    if pv:
        last = int(max(pv) * FPS)
        for i in range(last + 1):
            if cues and i in cues: await pg.evaluate(cues[i])
            await pg.evaluate("__step(33.333)")
            if any(int(t * FPS) == i for t in pv):
                await snap(pg, f"{out}/p_{i:05d}.jpg", 80)
        print("preview", name, flush=True)
        return
    for i in range(n):
        if cues and i in cues: await pg.evaluate(cues[i])
        await pg.evaluate("__step(33.333)")
        await snap(pg, f"{out}/{i:05d}.jpg", 90)
    os.system(f"ffmpeg -y -loglevel error -framerate {FPS} -i {out}/%05d.jpg -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p {ROOT}/clips/{name}.mp4")
    print("clip", name, n, "frames", flush=True)

def ov(html):
    return f"()=>{{document.getElementById('ov').innerHTML={json.dumps(html)}}}"

TRAIN = "()=>{ONLINE=true;S.followers=%d;setRoster(%s);myTicket=%s;Game.setN(wagonCount());Game.refreshWagon()}"

async def shot(pg, name):
    if name == "s1_follow":   # dlouhý vlak, kamera jede podél
        await pg.evaluate(TRAIN % (60, "[]", "null"))
        await pg.evaluate("()=>{Game.flyTo(0,.56)}")
        for _ in range(160): await pg.evaluate("__step(33.333)")
        await pg.evaluate(ov('<div class="eb">Vlak followerů</div><div class="ttl">Každý follower<br>= <y>jeden vagón</y></div><div class="chip">1 follow = <b>25 m vlaku</b></div>'))
        cues = {int(k * 1.6 * FPS): f"()=>{{Game.flyTo({k + 1},.56)}}" for k in range(5)}
        await record(pg, name, 7, cues=cues)
    elif name == "s2_ticket":   # tvůj vagón zevnitř s nickem
        tk = json.dumps({"nick": "tvuj.nick", "wagon": 1, "status": "verified", "public": True,
                         "avatar": {"coat": "#c4453a", "hat": "ksilt", "pet": "kocka", "item": "kniha", "hair": "#6b3f22", "skin": "#f1c9a5"}})
        await pg.evaluate(TRAIN % (60, "[]", tk))
        await pg.evaluate("()=>{Game.flyTo(1,.35)}")
        for _ in range(120): await pg.evaluate("__step(33.333)")
        await pg.evaluate(ov('<div class="eb">Odkaz v biu</div><div class="ttl">Vyzvedni si<br><y>jízdenku</y></div>'))
        await pg.evaluate("()=>{Game.flyTo(1,0)}")
        await record(pg, name, 8)
    elif name == "s3_start":   # jediný vagón v Praze
        await pg.evaluate(TRAIN % (1, "[]", "null"))
        await pg.evaluate("()=>{Game.flyTo(1,.75)}")
        for _ in range(150): await pg.evaluate("__step(33.333)")
        await pg.evaluate(ov('<div class="eb">Praha hl. n. · start</div><div class="ttl">Zatím<br><y>1 vagón</y></div><div class="chip">délka vlaku: <b>25 m</b></div>'))
        await pg.evaluate("()=>{Game.flyTo(0,.5)}")
        await record(pg, name, 5)
    elif name == "s4_earth":
        await pg.evaluate(EARTH)
        await pg.evaluate(ov('<div class="eb">Cíl hry</div><div class="ttl">Obepnout<br><y>celou Zemi</y></div><div class="big" id="km">0 km</div><div class="chip">= <b>1 603 000</b> followerů</div>'))
        await record(pg, name, 6)
    elif name == "s5_vote":
        await pg.evaluate(MAP)
        await pg.evaluate(ov('<div class="eb">Rozhodnete vy</div><div class="ttl">Kam<br><y>vyjedeme?</y></div><div style="height:470px"></div><div class="opts"><div>Kolín</div><div>Plzeň</div><div>Ústí</div><div>Tábor</div></div>'))
        await record(pg, name, 8)
    elif name == "s6_cta":
        await pg.evaluate("()=>{document.getElementById('full').style.display='none'}")
        await pg.evaluate(TRAIN % (8, "[]", "null"))
        await pg.evaluate("()=>{Game.flyTo(0,.22)}")
        for _ in range(150): await pg.evaluate("__step(33.333)")
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Dej follow<br><y>a nastup</y></div><div class="chip">jízdenka je <b>v biu</b></div>'))
        await pg.evaluate("()=>{Game.flyTo(1,.36)}")
        await record(pg, name, 5)

EARTH = r"""()=>{
  const f=document.getElementById('full');f.style.display='block';
  f.innerHTML='<canvas id="earth" width="1080" height="1920" style="width:100%;height:100%"></canvas>';
  const c=document.getElementById('earth'),g=c.getContext('2d');
  const rnd=(s=>()=>((s=Math.imul(s^s>>>15,1|s)+0x6D2B79F5|0)>>>0)/4294967296)(7);
  const blobs=Array.from({length:9},()=>({a:rnd()*Math.PI*2,lat:(rnd()-.5)*1.6,r:.18+rnd()*.22}));
  const t0=__vt();
  window.__onframe=vt=>{
    const t=(vt-t0)/1000,W=1080,H=1920,cx=540,cy=1300,R=290;
    const sky=g.createLinearGradient(0,0,0,H);sky.addColorStop(0,'#4f9fe0');sky.addColorStop(.6,'#9fd0f2');sky.addColorStop(1,'#e4f3fb');g.fillStyle=sky;g.fillRect(0,0,W,H);
    const sea=g.createRadialGradient(cx-R*.35,cy-R*.4,R*.1,cx,cy,R);sea.addColorStop(0,'#7cc3f0');sea.addColorStop(1,'#2468a8');
    g.save();g.beginPath();g.arc(cx,cy,R,0,7);g.fillStyle=sea;g.fill();g.clip();
    const rot=t*.35;g.fillStyle='#6fae55';
    for(const b of blobs){const lon=b.a+rot;const x=Math.sin(lon)*Math.cos(b.lat);const vis=Math.cos(lon);if(vis<-.1)continue;
      g.beginPath();g.ellipse(cx+x*R,cy+Math.sin(b.lat)*R,b.r*R*Math.max(.15,vis),b.r*R*.8,0,0,7);g.fill()}
    g.strokeStyle='rgba(255,255,255,.35)';g.lineWidth=3;for(let i=-2;i<=2;i++){g.beginPath();g.ellipse(cx,cy+i*R/3,Math.sqrt(R*R-(i*R/3)**2),12,0,0,7);g.stroke()}
    g.restore();
    const p=Math.min(1,Math.max(0,(t-.4)/4.2)),e=1-Math.pow(1-p,3);
    g.lineCap='round';g.lineWidth=34;g.strokeStyle='rgba(255,255,255,.55)';g.beginPath();g.arc(cx,cy,R+60,0,7);g.stroke();
    const a0=-Math.PI/2,a1=a0+Math.PI*2*Math.max(.003,e);
    g.strokeStyle='#f0a03a';g.lineWidth=26;g.beginPath();g.arc(cx,cy,R+60,a0,a1);g.stroke();
    g.setLineDash([22,14]);g.strokeStyle='#8a4508';g.lineWidth=6;g.beginPath();g.arc(cx,cy,R+60,a0,a1);g.stroke();g.setLineDash([]);
    const hx=cx+(R+60)*Math.cos(a1),hy=cy+(R+60)*Math.sin(a1);g.fillStyle='#cf4630';g.beginPath();g.arc(hx,hy,26,0,7);g.fill();g.strokeStyle='#fff';g.lineWidth=7;g.stroke();
    const km=document.getElementById('km');if(km)km.textContent=Math.round(40075*e).toLocaleString('cs-CZ')+' km';
  };
}"""

MAP = r"""()=>{
  const f=document.getElementById('full');f.style.display='block';
  f.innerHTML='<div style="position:absolute;inset:0;background:linear-gradient(#4f9fe0,#9fd0f2 55%,#e4f3fb)"></div><div id="mapbox" style="position:absolute;left:40px;right:40px;top:590px;height:420px;background:#eef3e4;border-radius:36px;border:6px solid #fff;box-shadow:0 20px 50px rgba(20,40,60,.3);overflow:hidden"><svg id="map" viewBox="0 0 1060 680" style="width:100%;height:auto;display:block;min-width:0"></svg></div>';
  ONLINE=true;S.followers=1;S.route=['praha'];S.vote={at:'praha',deadline:'',options:['kolin','plzen','usti','tabor'].map(to=>({to,votes:1}))};
  renderMap();
  const svg=document.getElementById('map');svg.setAttribute('viewBox','190 150 640 268');svg.style.height='100%';svg.style.width='100%';
  svg.querySelectorAll('text').forEach(t=>{if(/%$/.test(t.textContent))t.textContent='?'});
  window.__onframe=null;
}"""

async def main():
    names = sys.argv[1:] or ["s1_follow", "s2_ticket", "s3_start", "s4_earth", "s5_vote", "s6_cta"]
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
