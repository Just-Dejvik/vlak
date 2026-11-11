# Díl 7: „To si snad ze mě děláte…?“ 800+, Berlín vyhrál o 4 hlasy, cesta k Berlínu, Matyáš (vagón 122), přání do vagónů.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 826
ROUTE = ['praha', 'kolin', 'pardubice', 'hradec', 'liberec', 'vratislav', 'poznan', 'berlin']
# Matyáš chtěl být ve videu (souhlasil, nick je veřejný) – jeho skutečný panáček z webu
MATYAS = [122, "maslowskimatyas", {"coat": "#2f6f9f", "hair": "#6b3f22", "hat": "ksilt", "item": "kytara", "pet": "pes", "skin": "#9c6b48"}]

def roster():
    r = json.loads(film3.roster(140))
    r[121] = MATYAS
    return json.dumps(r)

EXTRA = r"""
.bars{position:absolute;left:70px;right:70px;top:1050px;display:grid;gap:26px}
.bar2{background:#fffaf0;border-radius:30px;padding:22px 30px;box-shadow:0 20px 50px rgba(0,0,0,.25)}
.bar2 .l{display:flex;justify-content:space-between;font:900 76px/1 BS,sans-serif;text-transform:uppercase;color:#1e2a33}
.bar2 .g{height:46px;border-radius:999px;background:#e9e0cf;margin-top:14px;overflow:hidden}
.bar2 .g i{display:block;height:100%;width:0;border-radius:999px}
.stlist{position:absolute;left:70px;right:70px;top:1240px;display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.stc{background:#fff;border-radius:999px;padding:16px 30px;font:800 46px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 10px 30px rgba(0,0,0,.2);opacity:0;transform:scale(.5)}
.stc b{color:#3f8a5c}
.plus{position:absolute;font:900 90px/1 BS,sans-serif;color:#3f8a5c;text-shadow:0 6px 0 #fff}
.wishes{position:absolute;inset:0}
.wish{position:absolute;background:#fff;border-radius:999px;padding:20px 34px;font:800 52px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 14px 34px rgba(0,0,0,.25);opacity:0}
.feat{position:absolute;left:70px;right:70px;top:1330px;display:flex;gap:18px;justify-content:center}
.feat div{background:#fffaf0;border:6px solid #f0a03a;border-radius:28px;padding:18px 26px;font:800 48px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 14px 34px rgba(0,0,0,.25);opacity:0;transform:scale(.4)}
"""

MAP7 = r"""()=>{
  const f=document.getElementById('full');f.style.display='block';f.style.zIndex='90';
  f.innerHTML='<div style="position:absolute;inset:0;background:linear-gradient(#4f9fe0,#9fd0f2 55%,#e4f3fb)"></div><div id="mapbox" style="position:absolute;left:40px;right:40px;top:560px;height:640px;background:#eef3e4;border-radius:36px;border:6px solid #fff;box-shadow:0 20px 50px rgba(20,40,60,.3);overflow:hidden"><svg id="map" style="display:block"></svg></div><div id="xtra"></div>';
  ONLINE=true;S.kmPerPassenger=1;S.followers=__N__;S.peak=__P__;S.route=__R__;S.vote={at:'berlin',deadline:'',options:[]};
  const svg=document.getElementById('map');
  window.__rm=()=>{renderMap()};__rm();
  window.__P=id=>proj(S.nodes[id]);const AR=(1080-80-12)/(640-12);
  window.__vb=(cx,cy,w)=>{const h=w/AR;svg.setAttribute('viewBox',`${cx-w/2} ${cy-h/2} ${w} ${h}`)};
  window.__fit=(ids,pad)=>{const ps=ids.map(__P);const xs=ps.map(p=>p[0]),ys=ps.map(p=>p[1]);const w=Math.max((Math.max(...xs)-Math.min(...xs))*(pad||1.35)+80,(Math.max(...ys)-Math.min(...ys))*(pad||1.35)*AR+80);return[(Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2,w]};
  window.__onframe=null;
}"""

def map7(peak):
    return MAP7.replace('__N__', str(N)).replace('__P__', str(peak)).replace('__R__', json.dumps(ROUTE))

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=EXTRA)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, roster(), "null"))
    await pg.evaluate("()=>{S.peak=%d;S.kmPerPassenger=1}" % N)
    await pg.evaluate(film3.NODRV)

async def shot(pg, name):
    if name == "x1_hook":   # 0–2,38: To si snad ze mě děláte prdel?
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(40,.5)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="ttl huge">To si snad…</div>'))
        await pg.evaluate(fx("const c=document.querySelector('canvas');const k=t>1.0?Math.exp(-(t-1.0)*2.5):0;c.style.transform=`translate(${Math.sin(t*63)*24*k}px,${Math.cos(t*51)*16*k}px) scale(${1+.06*k})`"))
        cues = {0: "()=>{Game.flyTo(60,.5)}",
                T(.95): ov('<div class="eb">Ty jo</div><div class="ttl huge">Děláte si<br><y>prdel?!</y></div>')}
        await film.record(pg, name, 2.6, cues=cues)
    elif name == "x2_berlin":   # 2,38–7,28: už nás je přes 800… a Berlín vyhrál! O pouhé čtyři hlasy!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(400,1)}"); await steps(pg, 150)
        await pg.evaluate(ov(''))
        await setfull(pg, '<div style="position:absolute;inset:0;background:rgba(20,35,45,.38)"></div><div id="cnt" style="position:absolute;left:0;right:0;top:420px;text-align:center"><div style="font:600 40px PM,monospace;letter-spacing:.18em;color:#fff;text-transform:uppercase">Je nás</div><div class="big-n" id="n1">0</div></div>'
                      '<div class="bars" id="bars" style="opacity:0"><div class="bar2"><div class="l"><span>Berlín</span><span id="b1">0</span></div><div class="g"><i id="g1" style="background:#2b2f3a"></i></div></div><div class="bar2"><div class="l"><span>Vídeň</span><span id="b2">0</span></div><div class="g"><i id="g2" style="background:#c4453a"></i></div></div></div>'
                      '<div style="position:absolute;left:0;right:0;top:1520px;text-align:center"><div class="stampG" id="st" style="background:#c4453a;box-shadow:0 10px 0 #8f2b1c">O pouhé 4 hlasy!</div></div>')
        js = ease + f"""const n=Math.round(E(t/1.3)*{N});document.getElementById('n1').textContent=n>=800?'800+':n;
          const b=t-1.76;document.getElementById('bars').style.opacity=b<0?0:Math.min(1,b/.2);document.getElementById('cnt').style.opacity=b<0?1:1-E(b/.3);
          const u=E(Math.max(0,b)/1.2);const v1=Math.round(48*u),v2=Math.round(44*u);document.getElementById('b1').textContent=v1;document.getElementById('b2').textContent=v2;document.getElementById('g1').style.width=(v1/48*100)+'%';document.getElementById('g2').style.width=(v2/48*100)+'%';
          const k=t-3.04;document.getElementById('st').style.transform=`rotate(-4deg) scale(${{k<0?0:(k<.35?B(k/.35):1)}})`"""
        await pg.evaluate(fx(js))
        cues = {T(1.76): ov('<div class="eb">Hlasování</div><div class="ttl">Berlín<br><y>vyhrál!</y></div>')}
        await film.record(pg, name, 5.1, cues=cues)
    elif name == "x3_trip":   # 7,28–11,65: vlak už vyrazil… projel Hradec, Liberec, Vratislav i Poznaň
        await pg.evaluate(map7(104))
        await pg.evaluate("()=>{const f=__fit(['pardubice','berlin','praha']);__vb(...f)}")
        await pg.evaluate(ov('<div class="eb">Pardubice → Berlín</div><div class="ttl">Vlak<br><y>vyrazil!</y></div>'))
        sts = [("Hradec Králové", 1.6), ("Liberec", 2.2), ("Vratislav", 2.75), ("Poznaň", 3.4)]
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}", '<div class="stlist">' + ''.join(f'<div class="stc" id="s{i}"><b>✓</b> {n}</div>' for i, (n, _) in enumerate(sts)) + '</div>')
        at = ",".join(str(a) for _, a in sts)
        js = ease + f"""const p=Math.round(104+E(t/3.6)*({N}-104));if(p!==S.peak){{S.peak=p;S.followers=p;__rm();const f=__fit(['pardubice','berlin','praha']);__vb(...f)}}
          const A=[{at}];for(let i=0;i<4;i++){{const k=t-A[i];const e=document.getElementById('s'+i);e.style.opacity=k<0?0:1;e.style.transform=`scale(${{k<0?.5:(k<.3?B(k/.3):1)}})`}}"""
        await pg.evaluate(fx(js))
        cues = {T(1.26): ov('<div class="eb">Pardubice → Berlín</div><div class="ttl">Projel<br><y>4 města</y></div>')}
        await film.record(pg, name, 4.6, cues=cues)
    elif name == "x4_left":   # 11,65–17,67: do Berlína chybí pár desítek km… každý nový cestující ho posune o kilometr blíž
        await pg.evaluate(map7(N))
        await pg.evaluate("()=>{const f=__fit(['poznan','berlin'],1.6);__vb(...f)}")
        await pg.evaluate(ov('<div class="eb">Poznaň → Berlín</div><div class="ttl">Chybí<br><y>78 km!</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}", '<div class="card4" style="top:1260px;padding:30px 50px 40px;text-align:left"><div style="display:flex;justify-content:space-between;align-items:baseline"><span style="font:900 60px BS,sans-serif;text-transform:uppercase">Do Berlína</span><span style="font:900 100px BS,sans-serif;color:#e08a12" id="lk">78 km</span></div><div class="gauge" style="margin-top:14px"><i id="lg" style="width:90.4%"></i></div></div><div id="pl"></div>')
        js = ease + f"""const k=t-2.9;const add=k<0?0:Math.min(6,Math.floor(k/.45)+1);const p={N}+add;if(p!==S.peak){{S.peak=p;S.followers=p;__rm();const f=__fit(['poznan','berlin'],1.6);__vb(...f)}}
          document.getElementById('lk').textContent=(78-add)+' km';document.getElementById('lg').style.width=((722+add)/800*100)+'%';
          let h='';for(let i=0;i<add;i++){{const q=Math.min(1,(k-i*.45)/.9);h+=`<div class="plus" style="left:${{140+i*140}}px;top:${{1180-q*160}}px;opacity:${{1-q}}">+1</div>`}}document.getElementById('pl').innerHTML=h"""
        await pg.evaluate(fx(js))
        cues = {T(2.9): ov('<div class="eb">Poznaň → Berlín</div><div class="ttl">+1 cestující<br><y>= +1 km</y></div>')}
        await film.record(pg, name, 6.2, cues=cues)
    elif name == "x5_matyas":   # 17,67–22,94: Matyáš chtěl být ve videu… tak tady je! Vagón 122.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(60,.6)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Přání cestujícího</div><div class="ttl">Matyáš chtěl<br><y>do videa…</y></div>'))
        cues = {0: "()=>{Game.flyTo(122,.5)}",
                T(2.62): ov('<div class="eb">Vagón № 122</div><div class="ttl huge">Tak tady<br><y>je!</y></div>'),
                T(3.0): "()=>{Game.flyTo(122,0)}",
                T(3.58): ov('<div class="eb">@maslowskimatyas</div><div class="ttl">Vagón<br><y>№ 122</y></div>'),
                T(3.4): "()=>{const g=__G.petSlot.children[0];if(g){g.position.x=-1.45;g.position.z=.7}}"}
        await film.record(pg, name, 5.5, cues=cues)
    elif name == "x6_items":   # 22,94–26,02: má kšiltovku, kytaru… a dokonce i psa!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(122,0)}"); await steps(pg, 220)
        await pg.evaluate("()=>{const g=__G.petSlot.children[0];if(g){g.position.x=-1.45;g.position.z=.7}}")
        await pg.evaluate(ov('<div class="eb">@maslowskimatyas</div><div class="ttl">Vagón<br><y>№ 122</y></div>'))
        await setfull(pg, '<div class="feat"><div id="f0">🧢 kšiltovka</div><div id="f1">🎸 kytara</div><div id="f2">🐕 pes</div></div>')
        await pg.evaluate(fx(ease + "const A=[0,.95,1.57];for(let i=0;i<3;i++){const k=t-A[i];const e=document.getElementById('f'+i);e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}"))
        cues = {T(1.57): ov('<div class="eb">@maslowskimatyas</div><div class="ttl">A dokonce<br><y>i psa!</y></div>')}
        await film.record(pg, name, 3.3, cues=cues)
    elif name == "x7_wish":   # 26,02–32,92: chceš něco speciálního? napiš do komentářů… vybereme a splníme
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(30,.25)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Přání do vagónu</div><div class="ttl">Co chceš<br><y>ve vagónu?</y></div>'))
        ws = [("🛹 skateboard", 90, 760), ("🍕 pizza", 600, 820), ("🐈 kočka", 160, 980), ("🎮 konzole", 560, 1060), ("🌴 palma", 120, 1220), ("🥁 bubny", 600, 1300), ("🚀 raketa", 260, 1440)]
        await setfull(pg, '<div style="position:absolute;inset:0;background:rgba(20,35,45,.25)"></div><div class="wishes">' + ''.join(f'<div class="wish" id="w{i}" style="left:{x}px;top:{y}px">{n}</div>' for i, (n, x, y) in enumerate(ws)) + '</div><div style="position:absolute;left:0;right:0;top:1600px;text-align:center"><div class="stampG" id="st" style="background:#3f8a5c;box-shadow:0 10px 0 #2b6342">Splníme je!</div></div>')
        js = ease + "for(let i=0;i<7;i++){const k=t-.25-i*.32;const e=document.getElementById('w'+i);e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)}) translateY(${Math.sin(t*2+i)*10}px) rotate(${Math.sin(i*1.7)*5}deg)`}const s=t-4.66;document.getElementById('st').style.transform=`rotate(-4deg) scale(${s<0?0:(s<.35?B(s/.35):1)})`"
        await pg.evaluate(fx(js))
        cues = {T(2.5): ov('<div class="eb">Přání do vagónu</div><div class="ttl">Napiš do<br><y>komentářů!</y></div>'),
                T(4.66): ov('<div class="eb">Přání do vagónu</div><div class="ttl">Pár jich<br><y>vybereme</y></div>')}
        await film.record(pg, name, 7.1, cues=cues)
    elif name == "x8_outro":
        os.environ["OUTRO_AT"] = "0.3,1.4,2.3"
        os.environ["OUTRO_LEN"] = "4.9"
        await film5.shot(pg, "v7_outro")

ALL = ["x1_hook", "x2_berlin", "x3_trip", "x4_left", "x5_matyas", "x6_items", "x7_wish", "x8_outro"]

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
