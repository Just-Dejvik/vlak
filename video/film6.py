# Díl 6: „Pardubice vyhrály! Teď hlasujeme o velkém cíli: Vídeň, nebo Berlín?“
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull, train = film5.setfull, film5.train
N, RES = 557, 453
film5.N = N

EXTRA = r"""
.vs{position:absolute;inset:0;display:grid;grid-template-rows:1fr 1fr}
.vs>div{display:flex;align-items:center;justify-content:center;font:900 230px/1 BS,sans-serif;text-transform:uppercase;color:#fff;text-shadow:0 10px 0 rgba(0,0,0,.25)}
.vs .a{background:linear-gradient(135deg,#c4453a,#e07a5a)}
.vs .b{background:linear-gradient(135deg,#2b2f3a,#4a5560)}
.vs .x{position:absolute;left:50%;top:50%;width:250px;height:250px;margin:-125px 0 0 -125px;border-radius:50%;background:#ffd23f;color:#1e2a33;font:900 130px/250px BS,sans-serif;text-align:center;box-shadow:0 14px 0 #c9a12a;transform:scale(0)}
.dest{position:absolute;left:60px;right:60px;top:1240px;background:#fffaf0;border-radius:40px;border:6px solid #f0a03a;padding:30px 44px 36px;box-shadow:0 30px 70px rgba(0,0,0,.3);font-family:IS,sans-serif;color:#1e2a33}
.dest .n{font:900 96px/1 BS,sans-serif;text-transform:uppercase}
.dest .k{font:800 60px/1.1 IS,sans-serif;color:#8a4508;margin-top:6px}
.dest .v{font:600 36px/1.25 IS,sans-serif;color:#5a6670;margin-top:8px}
"""

MAP6 = r"""()=>{
  const f=document.getElementById('full');f.style.display='block';f.style.zIndex='90';
  f.innerHTML='<div style="position:absolute;inset:0;background:linear-gradient(#4f9fe0,#9fd0f2 55%,#e4f3fb)"></div><div id="mapbox" style="position:absolute;left:40px;right:40px;top:560px;height:640px;background:#eef3e4;border-radius:36px;border:6px solid #fff;box-shadow:0 20px 50px rgba(20,40,60,.3);overflow:hidden"><svg id="map" style="display:block"></svg></div><div id="xtra"></div>';
  ONLINE=true;S.kmPerPassenger=1;S.followers=__N__;S.peak=__N__;S.route=['praha','kolin','pardubice'];
  S.vote={at:'pardubice',deadline:'',options:[{to:'viden',votes:1},{to:'berlin',votes:1}]};
  const svg=document.getElementById('map');
  window.__rm=()=>{renderMap();svg.querySelectorAll('text').forEach(t=>{if(/%$/.test(t.textContent))t.textContent='?'})};__rm();
  window.__P=id=>proj(S.nodes[id]);const AR=(1080-80-12)/(640-12);
  window.__vb=(cx,cy,w)=>{const h=w/AR;svg.setAttribute('viewBox',`${cx-w/2} ${cy-h/2} ${w} ${h}`)};
  window.__fit=(ids,pad)=>{const ps=ids.map(__P);const xs=ps.map(p=>p[0]),ys=ps.map(p=>p[1]);const w=Math.max((Math.max(...xs)-Math.min(...xs))*(pad||1.35)+80,(Math.max(...ys)-Math.min(...ys))*(pad||1.35)*AR+80);return[(Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2,w]};
  // vlastní zvýrazněná trasa, která se dá „kreslit“
  window.__draw=(to,color)=>{const p=pathTo('pardubice',to);const d=p.path.map((id,i)=>(i?'L':'M')+__P(id).join(' ')).join('');
    const el=document.createElementNS('http://www.w3.org/2000/svg','path');el.setAttribute('d',d);el.setAttribute('fill','none');el.setAttribute('stroke',color);el.setAttribute('stroke-linecap','round');el.setAttribute('stroke-linejoin','round');el.setAttribute('pathLength','1');el.setAttribute('stroke-dasharray','1 1');el.setAttribute('stroke-dashoffset','1');el.id='draw_'+to;svg.appendChild(el);return p};
  window.__onframe=null;
}"""

def map6():
    return MAP6.replace('__N__', str(N))

async def mk(b):
    ctx, pg = await film5.mk(b)
    await pg.add_style_tag(content=EXTRA)
    return ctx, pg

async def shot(pg, name):
    if name == "w1_arrive":   # 0–2,47: Pardubice vyhrály a jsme tam!
        await train(pg, drv=False)
        await pg.evaluate("()=>{S.peak=%d}" % N)
        await pg.evaluate("()=>{Game.flyTo(0,.75)}"); await steps(pg, 150)
        await pg.evaluate("()=>{const s=document.createElement('div');s.className='sign';s.id='sign';s.textContent='Pardubice';s.style.transform='translateX(-50%) translateY(-2200px)';document.body.appendChild(s)}")
        await pg.evaluate(ov('<div class="eb">Hlasování</div><div class="ttl">Pardubice<br><y>vyhrály!</y></div>'))
        cues = {0: "()=>{Game.flyTo(0,.32)}",
                T(.25): fx(ease + "const u=E(t/.45);document.getElementById('sign').style.transform=`translateX(-50%) translateY(${(1-u)*-2200+Math.sin(Math.max(0,t-.45)*14)*Math.exp(-Math.max(0,t-.45)*5)*30}px)`"),
                T(1.55): ov('<div class="eb">Stanice</div><div class="ttl">A jsme<br><y>tam!</y></div>')}
        await film.record(pg, name, 2.7, cues=cues)
    elif name == "w2_reserve":   # 2,47–7,98: je nás přes 550… takže máme v zásobě přes 450 km
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(300,1)}"); await steps(pg, 150)
        await pg.evaluate(ov(''))
        await setfull(pg, f'<div style="position:absolute;inset:0;background:rgba(20,35,45,.35)"></div><div style="position:absolute;left:0;right:0;top:330px;text-align:center"><div style="font:600 40px PM,monospace;letter-spacing:.18em;color:#fff;text-transform:uppercase">Je nás</div><div class="big-n" id="n1">0</div><div style="font:800 64px IS,sans-serif;color:#fff">cestujících</div></div><div class="card4" id="res" style="top:1000px;padding:34px 50px 44px;transform:scale(0);text-align:left"><div style="font:600 34px PM,monospace;letter-spacing:.16em;color:#8a4508;text-transform:uppercase">v zásobě</div><div style="font:900 190px/0.95 BS,sans-serif;color:#e08a12" id="rk">0 km</div><div class="gauge" style="margin-top:16px"><i id="rg"></i></div></div>')
        cues = {0: fx(ease + f"const n=Math.round(E(t/1.4)*{N});document.getElementById('n1').textContent=n>=550?'550+':n;const r=t-1.98;document.getElementById('res').style.transform=`scale(${{r<0?0:(r<.35?B(r/.35):1)}})`;const g=E(Math.max(0,r-.15)/1.3);document.getElementById('rg').style.width=(g*100)+'%';document.getElementById('rk').textContent=(g>=1?'450+':Math.round(g*450))+' km'"),
                T(.1): "()=>{Game.flyTo(0,1)}"}
        await film.record(pg, name, 5.8, cues=cues)
    elif name == "w3_big":   # 7,98–13,67: nehlasujeme o zastávce… ale o velkém cíli. Vlak si cestu najde sám.
        await pg.evaluate(map6())
        await pg.evaluate("()=>{const f=__fit(['pardubice','viden','berlin','praha']);window.__F=f;__vb(f[0],f[1],f[2]*.55)}")
        await pg.evaluate(ov('<div class="eb">Novinka</div><div class="ttl">Žádné<br><y>zastávky…</y></div>'))
        zoom = fx(ease + "const [x1,y1,w1]=__F;const u=E(t/1.4);__vb(x1,y1,w1*(.55+.45*u))")
        draw = fx(ease + "for(const [to,c] of [['viden','#c4453a'],['berlin','#2b2f3a']]){let el=document.getElementById('draw_'+to);if(!el)el=(__draw(to,c),document.getElementById('draw_'+to));const vb=document.getElementById('map').viewBox.baseVal;el.setAttribute('stroke-width',vb.width/120);el.setAttribute('stroke-dashoffset',1-E(t/1.3))}")
        cues = {T(1.94): zoom,
                T(2.0): ov('<div class="eb">Novinka</div><div class="ttl">Hlasujeme o<br><y>velkém cíli!</y></div>'),
                T(3.58): draw,
                T(3.6): ov('<div class="eb">Novinka</div><div class="ttl">Cestu najde<br><y>vlak sám</y></div>')}
        await film.record(pg, name, 5.9, cues=cues)
    elif name == "w4_vs":   # 13,67–15,59: Vídeň, nebo Berlín?
        await setfull(pg, '<div class="vs"><div class="a" id="va" style="transform:translateX(-1100px)">Vídeň</div><div class="b" id="vb" style="transform:translateX(1100px)">Berlín</div><div class="x" id="vx">vs</div></div>', 98)
        await pg.evaluate("()=>{document.getElementById('ov').innerHTML=''}")
        await pg.evaluate(fx(ease + "const a=E(t/.3),b=E((t-.55)/.3);document.getElementById('va').style.transform=`translateX(${(1-a)*-1100}px)`;document.getElementById('vb').style.transform=`translateX(${(1-b)*1100}px)`;const k=t-.95;document.getElementById('vx').style.transform=`scale(${k<0?0:(k<.3?B(k/.3):1)}) rotate(${k<0?0:-8}deg)`"))
        await film.record(pg, name, 2.1)
    elif name in ("w5_viden", "w6_berlin"):
        vid = name == "w5_viden"
        to, col = ("viden", "#c4453a") if vid else ("berlin", "#2b2f3a")
        await pg.evaluate(map6())
        await pg.evaluate("()=>{const f=__fit(['pardubice','viden','berlin','praha']);__vb(...f)}")
        p = await pg.evaluate("t=>{const p=__draw(t,'%s');return {km:p.km,via:p.path.slice(1,-1).map(nodeName)}}" % col, to)
        title = ('Do Vídně<br><y>291 km</y>' if vid else 'Do Berlína<br><y>800 km</y>')
        await pg.evaluate(ov(f'<div class="eb">Cíl č. {1 if vid else 2}</div><div class="ttl">{title}</div>'))
        via = " · ".join(p["via"])
        if vid:
            card = f'<div class="dest" id="dc" style="transform:scale(0)"><div class="n">Vídeň</div><div class="k">{p["km"]} km</div><div class="v">přes {via}</div><div style="text-align:center"><div class="stampG" id="st" style="background:#3f8a5c;box-shadow:0 10px 0 #2b6342">Jsme tam hned ✓</div></div></div>'
        else:
            card = f'<div class="dest" id="dc" style="transform:scale(0)"><div class="n">Berlín</div><div class="k">{p["km"]} km</div><div class="v">přes {via}</div><div class="gauge" style="margin-top:16px"><i id="rg"></i></div><div style="display:flex;justify-content:space-between;font:700 32px IS,sans-serif;color:#8a4508;margin-top:8px"><span>zásoba {RES} km</span><span>{p["km"]} km</span></div><div style="text-align:center"><div class="stampG" id="st" style="background:#c4453a;box-shadow:0 10px 0 #8f2b1c">Chybí asi 250 lidí</div></div></div>'
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}", card)
        at = 2.6 if vid else 2.56
        zoomTo = "['pardubice','viden']" if vid else "['pardubice','berlin','liberec']"
        js = ease + f"""const [x0,y0,w0]=__fit(['pardubice','viden','berlin','praha']);const [x1,y1,w1]=__fit({zoomTo},1.25);const u=E(t/1.0);__vb(x0+(x1-x0)*u,y0+(y1-y0)*u,w0+(w1-w0)*u);
          const el=document.getElementById('draw_{to}');const vb=document.getElementById('map').viewBox.baseVal;el.setAttribute('stroke-width',vb.width/110);el.setAttribute('stroke-dashoffset',1-E((t-.2)/1.4));
          const c=t-.5;document.getElementById('dc').style.transform=`scale(${{c<0?0:(c<.35?B(c/.35):1)}})`;
          {"" if vid else "const g=document.getElementById('rg');g.style.width=(E((t-.9)/1.0)*" + str(round(RES / 800 * 100, 1)) + ")+'%';"}
          const k=t-{at};document.getElementById('st').style.transform=`rotate(-4deg) scale(${{k<0?0:(k<.35?B(k/.35):1)}})`"""
        await pg.evaluate(fx(js))
        await film.record(pg, name, 3.9 if vid else 6.0)
    elif name == "w7_rule":   # 25,07–28,94: piš do komentářů… počítají se jen hlasy lidí s jízdenkou
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(20,.8)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Hlasování</div><div class="ttl">Piš do<br><y>komentářů</y></div>'))
        cm = [("#e07a9b", "jana.n", "Vídeň!!", True), ("#2f6f9f", "petr_k", "Berlín, jasně", True),
              ("#a8a29a", "nekdo_bez", "Vídeň", False), ("#3f8a5c", "eva.v", "berlín 🚂", True)]
        rows = ''.join(f'<div class="cm{"" if ok else " dead"}" id="c{i}"><div class="av" style="background:{c}"></div><div class="t"><b>{n}</b>{txt}</div><div class="tag {"ok" if ok else "no"}">{"🎫 platí" if ok else "bez jízdenky"}</div></div>' for i, (c, n, txt, ok) in enumerate(cm))
        await setfull(pg, f'<div style="position:absolute;inset:0;background:rgba(20,35,45,.4)"></div><div class="cmts">{rows}</div><div class="rule" id="rl">Počítají se jen hlasy s jízdenkou</div>')
        await pg.evaluate(fx(ease + "for(let i=0;i<4;i++){const u=E((t-.1-i*.18)/.3);const e=document.getElementById('c'+i);e.style.opacity=u;e.style.transform=`translateY(${(1-u)*30}px)`}const k=t-1.24;document.getElementById('rl').style.transform=`scale(${k<0?0:(k<.35?B(k/.35):1)}) rotate(-2deg)`"))
        cues = {T(1.24): ov('<div class="eb">Pozor</div><div class="ttl">Hlasuj<br><y>s jízdenkou</y></div>')}
        await film.record(pg, name, 4.1, cues=cues)
    elif name == "w8_outro":
        os.environ.setdefault("OUTRO_AT", "0.3,1.3,2.25")
        os.environ.setdefault("OUTRO_LEN", "5.1")
        await film5.shot(pg, "v7_outro")

ALL = ["w1_arrive", "w2_reserve", "w3_big", "w4_vs", "w5_viden", "w6_berlin", "w7_rule", "w8_outro"]

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
