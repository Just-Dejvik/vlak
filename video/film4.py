# Díl 4: „Jsme v Kolíně! A měníme pravidla.“ 1 cestující = 1 vagón + 1 km, zásoba, Pardubice vs. Brod.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps = film2.ov, film3.T, film3.steps
N = 110

EXTRA = r"""
#map{height:100%!important;width:100%!important}
#ov .ttl.huge{font-size:200px}
.card4{position:absolute;left:70px;right:70px;background:#fffaf0;border-radius:44px;border:6px solid #f0a03a;box-shadow:0 30px 70px rgba(0,0,0,.3);text-align:center;font-family:IS,sans-serif;color:#1e2a33}
.eq{font:900 120px/1.05 BS,sans-serif;text-transform:uppercase}
.eq .p{display:block;opacity:0;transform:scale(.4);transition:none}
.eq .p.on{opacity:1;transform:scale(1)}
.eq .y{color:#e08a12}
.eq .g{color:#3f8a5c}
.big-n{font:900 300px/0.9 BS,sans-serif;color:#fff;text-shadow:0 10px 0 rgba(20,40,60,.35)}
.gauge{height:70px;border-radius:999px;background:#e9e0cf;overflow:hidden;box-shadow:inset 0 4px 0 rgba(0,0,0,.08)}
.gauge i{display:block;height:100%;width:0;border-radius:999px;background:linear-gradient(90deg,#f0a03a,#ffd23f)}
.stampG{display:inline-block;margin-top:22px;padding:14px 34px;border-radius:22px;font:900 70px/1 BS,sans-serif;text-transform:uppercase;color:#fff;transform:rotate(-4deg) scale(0)}
.sign{position:absolute;left:50%;top:1250px;z-index:95;transform:translateX(-50%) translateY(-1400px);background:#1d4f91;color:#fff;border:10px solid #fff;outline:6px solid #1d4f91;border-radius:18px;padding:18px 90px 22px;font:800 150px/1 IS,sans-serif;box-shadow:0 30px 60px rgba(0,0,0,.35)}
.sign:before,.sign:after{content:"";position:absolute;top:-130px;width:16px;height:130px;background:#4a5560}
.sign:before{left:80px}.sign:after{right:80px}
"""

def fx(js):
    """JS spuštěný jako animace: dostane t (s od startu)."""
    return "()=>{const t0=__vt();window.__onframe=vt=>{const t=(vt-t0)/1000;" + js + "}}"

ease = "const E=u=>u<=0?0:u>=1?1:1-Math.pow(1-u,3);const B=u=>u<=0?0:u>=1?1:Math.sin(u*Math.PI*.5)*(1+.35*Math.sin(u*Math.PI));"

MAP4 = r"""()=>{
  const f=document.getElementById('full');f.style.display='block';f.style.zIndex='90';
  f.innerHTML='<div style="position:absolute;inset:0;background:linear-gradient(#4f9fe0,#9fd0f2 55%,#e4f3fb)"></div><div id="mapbox" style="position:absolute;left:40px;right:40px;top:600px;height:600px;background:#eef3e4;border-radius:36px;border:6px solid #fff;box-shadow:0 20px 50px rgba(20,40,60,.3);overflow:hidden"><svg id="map" style="display:block"></svg></div><div id="xtra"></div>';
  ONLINE=true;S.kmPerPassenger=1;S.followers=__N__;S.peak=__P__;S.route=['praha','kolin'];S.vote={at:'kolin',deadline:'',options:['pardubice','hbrod'].map(to=>({to,votes:1}))};
  const svg=document.getElementById('map');svg.setAttribute('preserveAspectRatio','xMidYMid meet');
  window.__rm=()=>{renderMap();svg.querySelectorAll('text').forEach(t=>{if(/%$/.test(t.textContent))t.textContent='?'})};__rm();
  window.__P=id=>proj(S.nodes[id]);const AR=(1080-80-12)/(600-12);
  window.__vb=(cx,cy,w)=>{const h=w/AR;svg.setAttribute('viewBox',`${cx-w/2} ${cy-h/2} ${w} ${h}`)};
  window.__onframe=null;
}"""

async def mk(b):
    ctx, pg = await film3.mk(b)
    await pg.add_style_tag(content=EXTRA)
    return ctx, pg

async def train(pg, drv=False):
    await pg.evaluate("()=>{document.getElementById('full').style.display='none'}")
    await pg.evaluate(film2.TRAIN % (N, film3.roster(N), "null"))
    await pg.evaluate("()=>{S.peak=%d;S.kmPerPassenger=1}" % N)
    await pg.evaluate(film3.DRV if drv else film3.NODRV)

async def shot(pg, name):
    if name == "m1_arrive":   # 0–2,39: Ty vole, jsme v Kolíně!
        await train(pg, False)
        await pg.evaluate("()=>{Game.flyTo(0,.75)}"); await steps(pg, 150)
        await pg.evaluate("()=>{const s=document.createElement('div');s.className='sign';s.id='sign';s.textContent='Kolín';document.body.appendChild(s)}")
        await pg.evaluate(ov('<div class="ttl huge">Ty vole!</div>'))
        cues = {0: "()=>{Game.flyTo(0,.3)}",
                T(.15): fx(ease + "const u=E((t-.0)/.45);document.getElementById('sign').style.transform=`translateX(-50%) translateY(${(1-u)*-1400+Math.sin(Math.max(0,t-.45)*14)*Math.exp(-Math.max(0,t-.45)*5)*30}px) rotate(${Math.sin(Math.max(0,t-.45)*9)*Math.exp(-Math.max(0,t-.45)*3)*4}deg)`"),
                T(.85): ov('<div class="eb">Stanice</div><div class="ttl huge">Jsme v<br><y>Kolíně!</y></div>')}
        await film.record(pg, name, 2.7, cues=cues)
    elif name == "m2_rules":   # 2,39–4,93: A teď pozor… měníme pravidla.
        await pg.evaluate("""()=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='98';
          f.innerHTML='<div id="rays" style="position:absolute;left:50%;top:50%;width:2800px;height:2800px;margin:-1400px 0 0 -1400px;background:repeating-conic-gradient(#ffd23f 0 10deg,#ffbf1f 10deg 20deg)"></div><div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(255,255,255,.55),rgba(255,255,255,0) 55%)"></div><div id="pz" style="position:absolute;left:0;right:0;top:700px;text-align:center;font:900 130px/1 BS,sans-serif;text-transform:uppercase;color:#1e2a33">A teď pozor…</div><div id="stamp" style="position:absolute;left:50%;top:55%;transform:translate(-50%,-50%) scale(0) rotate(-8deg);font:900 240px/0.88 BS,sans-serif;text-transform:uppercase;color:#1e2a33;text-align:center;text-shadow:0 10px 0 rgba(255,255,255,.7)">Nová<br><span style="color:#c4453a">pravidla!</span></div>';
          document.getElementById('ov').innerHTML=''}""")
        await pg.evaluate(fx(ease + "document.getElementById('rays').style.transform=`rotate(${t*35}deg)`;const k=t-1.03;const pz=document.getElementById('pz');pz.style.opacity=k>0?0:1;pz.style.transform=`scale(${.9+E(t/.3)*.1})`;document.getElementById('stamp').style.transform=`translate(-50%,-50%) scale(${k<0?0:(k<.35?B(k/.35):1+.03*Math.sin((k-.35)*9))}) rotate(-8deg)`"))
        await film.record(pg, name, 2.8)
    elif name == "m3_eq":   # 4,93–9,71: každý, kdo nastoupí, přidá vagón… a posune vlak o celý kilometr
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(20,.5)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Nová pravidla</div><div class="ttl">Každý, kdo<br><y>nastoupí</y></div>'))
        await pg.evaluate("""()=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='90';
          f.innerHTML='<div class="card4" style="top:760px;padding:50px 30px 56px"><div class="eq"><span class="p on" id="e1">1 cestující</span><span class="p y" id="e2">= 1 vagón</span><span class="p g" id="e3" style="font-size:190px">+ 1 km</span></div></div>'}""")
        pop = lambda i: fx(ease + f"const e=document.getElementById('e{i}');e.classList.add('on');const s=B(t/.35);e.style.transform=`scale(${{t<.35?s:1}})`;e.style.opacity=Math.min(1,t/.1)")
        cues = {0: "()=>{Game.flyTo(40,.5)}", T(1.15): pop(2), T(2.27): pop(3),
                T(2.3): ov('<div class="eb">Nová pravidla</div><div class="ttl">Vlak jede<br><y>o kilometr!</y></div>')}
        await film.record(pg, name, 5.0, cues=cues)
    elif name == "m4_count":   # 9,71–12,94: je nás 110, takže máme 110 kilometrů
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(110,1)}"); await steps(pg, 150)
        await pg.evaluate(ov(''))
        await pg.evaluate("""()=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='90';
          f.innerHTML='<div style="position:absolute;inset:0;background:rgba(20,35,45,.35)"></div><div style="position:absolute;left:0;right:0;top:420px;text-align:center"><div style="font:600 40px PM,monospace;letter-spacing:.18em;color:#fff;text-transform:uppercase">Je nás</div><div class="big-n" id="n1">0</div><div style="font:800 64px IS,sans-serif;color:#fff">cestujících</div></div><div class="card4" id="kmc" style="top:1120px;padding:36px 30px 40px;transform:scale(0)"><div style="font:600 34px PM,monospace;letter-spacing:.16em;color:#8a4508;text-transform:uppercase">to je</div><div style="font:900 200px/0.95 BS,sans-serif;color:#3f8a5c" id="n2">0 km</div></div>'}""")
        cues = {0: fx(ease + f"const n=Math.round(E(t/1.25)*{N});document.getElementById('n1').textContent=n;const k=t-1.0;document.getElementById('kmc').style.transform=`scale(${{k<0?0:(k<.35?B(k/.35):1)}})`;document.getElementById('n2').textContent=Math.round(E(Math.max(0,k)/1.0)*{N})+' km'"),
                T(.1): "()=>{Game.flyTo(60,1)}"}
        await film.record(pg, name, 3.5, cues=cues)
    elif name == "m5_map":   # 12,94–17,77: do Kolína jich bylo jen 62… takže 48 máme v zásobě
        await pg.evaluate(MAP4.replace('__N__', str(N)).replace('__P__', '0'))
        await pg.evaluate("()=>{S.peak=0;S.followers=0;__rm();const a=__P('praha'),b=__P('kolin');__vb((a[0]+b[0])/2+20,(a[1]+b[1])/2,380)}")
        await pg.evaluate(ov('<div class="eb">Praha → Kolín</div><div class="ttl">Do Kolína<br>jen <y>62 km</y></div>'))
        await pg.evaluate("""()=>{document.getElementById('xtra').innerHTML='<div class="card4" id="res" style="top:1290px;padding:30px 50px 40px;transform:scale(0);text-align:left"><div style="display:flex;justify-content:space-between;align-items:baseline"><span style="font:900 64px BS,sans-serif;text-transform:uppercase">V zásobě</span><span style="font:900 100px BS,sans-serif;color:#e08a12" id="rk">0 km</span></div><div class="gauge" style="margin-top:14px"><i id="rg"></i></div></div>'}""")
        cues = {0: fx(ease + f"const k=Math.round(E(t/1.6)*62);if(k!==S.peak){{S.peak=k;S.followers=k;__rm()}}const r=t-2.18;document.getElementById('res').style.transform=`scale(${{r<0?0:(r<.35?B(r/.35):1)}})`;const g=E(Math.max(0,r-.2)/.9);document.getElementById('rg').style.width=(g*100)+'%';document.getElementById('rk').textContent=Math.round(g*48)+' km'"),
                T(2.18): ov('<div class="eb">Praha → Kolín</div><div class="ttl"><y>48 km</y><br>v zásobě!</div>')}
        await film.record(pg, name, 5.1, cues=cues)
    elif name in ("m6a_pard", "m6b_brod"):
        pard = name == "m6a_pard"
        to, km = ("pardubice", 42) if pard else ("hbrod", 80)
        await pg.evaluate(MAP4.replace('__N__', str(N)).replace('__P__', str(N)))
        await pg.evaluate("()=>{const a=__P('kolin'),b=__P('%s');__vb((a[0]+b[0])/2,(a[1]+b[1])/2,Math.max(300,Math.hypot(b[0]-a[0],b[1]-a[1])*2.4))}" % to)
        title = ('Pardubice<br>za <y>42 km</y>' if pard else 'Havl. Brod<br>za <y>80 km</y>')
        await pg.evaluate(ov(f'<div class="eb">Z Kolína</div><div class="ttl">{title}</div>'))
        stamp = ('<div class="stampG" id="st" style="background:#3f8a5c;box-shadow:0 10px 0 #2b6342">Dojedeme hned ✓</div>' if pard
                 else '<div class="stampG" id="st" style="background:#c4453a;box-shadow:0 10px 0 #8f2b1c">Chybí 32 lidí</div>')
        fill = 100 if pard else 48 / 80 * 100
        await pg.evaluate("""h=>{document.getElementById('xtra').innerHTML=h}""",
            f'<div class="card4" style="top:1290px;padding:30px 50px 36px;text-align:left"><div style="display:flex;justify-content:space-between;align-items:baseline"><span style="font:900 56px BS,sans-serif;text-transform:uppercase">Zásoba 48 km</span><span style="font:900 56px BS,sans-serif;color:#8a4508">/ {km} km</span></div><div class="gauge" style="margin-top:14px"><i id="rg" style="background:{"linear-gradient(90deg,#3f8a5c,#7cc26b)" if pard else "linear-gradient(90deg,#f0a03a,#ffd23f)"}"></i></div><div style="text-align:center">{stamp}</div></div>')
        at = 2.05 if pard else 2.15
        cues = {0: fx(ease + f"document.getElementById('rg').style.width=(E(t/1.0)*{fill})+'%';const k=t-{at};document.getElementById('st').style.transform=`rotate(-4deg) scale(${{k<0?0:(k<.35?B(k/.35):1)}})`")}
        await film.record(pg, name, 3.6 if pard else 4.7, cues=cues)
    elif name == "m7a_vote":   # 25,57–26,94: tak kam to pošleme?
        await pg.evaluate(MAP4.replace('__N__', str(N)).replace('__P__', str(N)))
        await pg.evaluate("()=>{const k=__P('kolin'),p=__P('pardubice'),h=__P('hbrod');const xs=[k[0],p[0],h[0]],ys=[k[1],p[1],h[1]];__vb((Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2+8,Math.max((Math.max(...xs)-Math.min(...xs))*1.9,(Math.max(...ys)-Math.min(...ys))*1.9*988/588))}")
        await pg.evaluate(ov('<div class="eb">Hlasování</div><div class="ttl">Kam to<br><y>pošleme?</y></div><div style="height:690px"></div><div class="opts two"><div id="o0">Pardubice</div><div id="o1">Havl. Brod</div></div>'))
        on = lambda i: "()=>{document.querySelectorAll('#ov .opts div').forEach(d=>d.classList.remove('on'));" + (f"document.getElementById('o{i}').classList.add('on')" if i >= 0 else "") + "}"
        cues = {T(.25): on(0), T(.75): on(1), T(1.2): on(-1)}
        await film.record(pg, name, 1.6, cues=cues)
    elif name == "m7b_cta":   # 26,94–konec: piš do komentářů… a nastup, ať vlak jede dál!
        await train(pg, True)
        await pg.evaluate("()=>{Game.flyTo(0,.6)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Piš do<br><y>komentářů!</y></div>'))
        cues = {0: "()=>{Game.flyTo(0,.36)}",
                T(1.11): ov('<div class="eb">@vlak.followeru</div><div class="ttl">A <y>nastup,</y><br>ať vlak jede!</div>')}
        await film.record(pg, name, 4.7, cues=cues)

ALL = ["m1_arrive", "m2_rules", "m3_eq", "m4_count", "m5_map", "m6a_pard", "m6b_brod", "m7a_vote", "m7b_cta"]

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
