# Díl 11: Podpora – „43 lidí, 0 Kč“ a proměna vagónu na ZLATÝ.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 1320
GW = 128           # vagón, který zezlátne (smyšlený nick)
GNICK = "tvuj.nick"

EXTRA = r"""
.band{position:absolute;top:0;bottom:0;width:420px;left:-500px;background:linear-gradient(100deg,rgba(255,255,255,0),rgba(255,240,180,.85),rgba(255,255,255,0));mix-blend-mode:screen;opacity:0}
.flash{position:absolute;inset:0;background:#fff7d6;opacity:0}
.cf{position:absolute;width:22px;height:34px;border-radius:4px;opacity:0}
.spk{position:absolute;width:60px;height:60px;margin:-30px 0 0 -30px;opacity:0;background:radial-gradient(circle,#fff 0,#ffe9a0 30%,rgba(255,210,90,0) 70%)}
.spk:before,.spk:after{content:"";position:absolute;left:28px;top:-10px;width:4px;height:80px;background:#fff;border-radius:2px}
.spk:after{transform:rotate(90deg)}
.zero{position:absolute;left:0;right:0;top:1150px;text-align:center}
.zero .n{font:900 300px/1 BS,sans-serif;color:#fff;text-shadow:0 10px 0 rgba(20,40,60,.35)}
.zero .k{font:800 60px/1 IS,sans-serif;color:#fff;margin-top:10px}
.cnt{position:absolute;left:0;right:0;top:700px;text-align:center;font:900 120px/1 BS,sans-serif;color:#1e2a33}
"""

def roster():
    r = json.loads(film3.roster(560))
    r[GW - 1][1] = GNICK
    return json.dumps(r)

ROUTE = ['praha', 'kolin', 'pardubice', 'hradec', 'liberec', 'vratislav', 'poznan', 'berlin', 'hannover', 'koln_r', 'brusel', 'lille', 'pariz']
STATE = "()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=1478;S.route=%s;S.vote={at:'pariz',deadline:'',options:[]};renderHud()}" % (N, json.dumps(ROUTE))

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=EXTRA)
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg, gold=False):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, roster(), "null"))
    await pg.evaluate(STATE)
    await pg.evaluate("()=>{S.supporters=%s}" % (json.dumps([GNICK]) if gold else "[]"))
    await pg.evaluate(film3.NODRV)

# Proměna: barva/lesk těla vagónu plynule přejde do zlata, pak se zapne skutečný zlatý vagón (třpytky, ozdoby).
def morph_js(t0, n=GW):
    return f"""{{const s=__G.slots.find(q=>q.n==={n}&&q.g.visible);const k=t-{t0};
      if(s){{if(!window.__mm&&k>=0){{const m=s.back.material.clone();m.envMap=__G.goldMat.envMap;m.envMapIntensity=0;window.__mm={{m,c0:m.color.clone(),m0:m.metalness,r0:m.roughness}};
          const r=__G.goldRoofMat.clone();r.color.copy(s.roof.material.color);r.metalness=0;r.envMapIntensity=0;window.__mr={{m:r,c0:r.color.clone()}};
          for(const q of [s.back,s.endA,s.endB,s.fLow,s.fUp,...s.pillars])q.material=m;s.roof.material=s.roof2.material=r}}
        if(window.__mm&&k>=0&&k<1.2){{const u=E(Math.min(1,k/1.0));const M=window.__mm;M.m.color.copy(M.c0).lerp(__G.goldMat.color,u);M.m.metalness=M.m0+(.92-M.m0)*u;M.m.roughness=M.r0+(.28-M.r0)*u;M.m.envMapIntensity=1.25*u;M.m.emissive.copy(__G.goldMat.emissive).multiplyScalar(u);M.m.emissiveIntensity=.25;
          const R=window.__mr;R.m.color.copy(R.c0).lerp(__G.goldRoofMat.color,u);R.m.metalness=.9*u;R.m.envMapIntensity=1.1*u}}
        if(k>=1.05&&!window.__gd){{window.__gd=1;S.supporters=['{GNICK}']}}}}
      const b=document.getElementById('bd');if(b){{const q=(k+.1)/1.0;b.style.opacity=q>0&&q<1?1:0;b.style.left=(-500+q*1600)+'px'}}
      const f=document.getElementById('fl');if(f)f.style.opacity=k<0?0:Math.max(0,.85-k*2.2);
      const c=document.querySelector('canvas');const z=k>0?Math.exp(-k*3):0;c.style.transform=`translate(${{Math.sin(t*63)*18*z}}px,${{Math.cos(t*51)*12*z}}px) scale(${{1+.03*z}})`;
      for(let i=0;i<40;i++){{const e=document.getElementById('cf'+i);if(!e)break;const q=k-1.05;if(q<0){{e.style.opacity=0;continue}}const a=i*2.399,v=700+((i*97)%500);e.style.opacity=Math.max(0,1-q/1.6);e.style.transform=`translate(${{Math.cos(a)*v*q}}px,${{Math.sin(a)*v*q*.7+900*q*q}}px) rotate(${{i*40+q*720}}deg)`}}
      for(let i=0;i<10;i++){{const e=document.getElementById('sk'+i);if(!e)break;const q=k+.6-i*.05;e.style.opacity=q<0||q>.9?0:Math.sin(q/.9*Math.PI);e.style.transform=`scale(${{.5+q}}) rotate(${{q*90}}deg)`}}}}"""

# Vlastní kamera u vagónu (3/4 pohled zblízka); o = [px,py,pz,lx,ly,lz] relativně ke středu vagónu.
CAM = """(o)=>{const c=__G.camera;window.__cam=o;if(!c.__p){c.__p=1;const L=c.lookAt.bind(c);c.lookAt=(x,y,z)=>{const q=window.__cam;const s=q&&__G.slots.find(v=>v.n===%d&&v.g.visible);if(!s)return L(x,y,z);const X=s.g.position.x;c.position.set(X+q[0],q[1],q[2]);L(X+q[3],q[4],q[5])}}}""" % GW

def morph_html():
    cols = ["#ffd23f", "#ffb020", "#fff3b0", "#e8a317", "#ffffff"]
    cf = ''.join(f'<div class="cf" id="cf{i}" style="left:540px;top:900px;background:{cols[i % 5]}"></div>' for i in range(40))
    sk = ''.join(f'<div class="spk" id="sk{i}" style="left:{180 + (i * 83) % 720}px;top:{760 + (i * 131) % 380}px"></div>' for i in range(10))
    return '<div class="band" id="bd"></div><div class="flash" id="fl"></div>' + sk + cf

MONA = 401
WIN401 = ["dudonlukas", {"coat": "#2f6f9f", "hat": "zadna", "pet": "pes", "item": "kytara", "hair": "#6b3f22", "skin": "#9c6b48"}, ["monalisa"]]

def roster401():
    r = json.loads(roster())
    r[MONA - 1] = [MONA] + WIN401
    return json.dumps(r)

def pop(ids, times):
    return "const A=%s;const I=%s;for(let i=0;i<I.length;i++){const k=t-A[i];const e=document.getElementById(I[i]);if(!e)continue;e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}" % (json.dumps(times), json.dumps(ids))

KOFI_CARD = """<div style="position:absolute;inset:0;background:linear-gradient(#ffe7c2,#ffd09a)"></div>
<div style="position:absolute;left:90px;right:90px;top:560px;background:#fff;border-radius:44px;box-shadow:0 24px 60px rgba(120,60,0,.25);padding:56px 50px;text-align:center">
<div style="font:900 64px/1 BS,sans-serif;color:#c2410c;text-transform:uppercase">☕ Podpoř vlak</div>
<div style="font:600 34px/1.3 IS,sans-serif;color:#6b5a4a;margin-top:18px">ko-fi.com/vlakfolloweru</div>
<div style="display:flex;justify-content:space-around;margin-top:56px">
<div><div id="v1" style="font:900 170px/1 BS,sans-serif;color:#1e2a33">0</div><div style="font:700 38px IS,sans-serif;color:#6b5a4a">👀 návštěv</div></div>
<div><div id="v2" style="font:900 170px/1 BS,sans-serif;color:#1e2a33;opacity:.15">?</div><div style="font:700 38px IS,sans-serif;color:#6b5a4a">💰 poslali</div></div></div></div>"""

async def shot(pg, name):
    if name == "q1_visits":   # 0–4,80: Na mou stránku pro podporu přišlo 43 lidí. A víte, kolik poslali?
        await setfull(pg, KOFI_CARD)
        await pg.evaluate(ov('<div class="eb">Moje stránka pro podporu</div><div class="ttl">Přišlo<br><y>43 lidí</y></div>'))
        js = ease + "document.getElementById('v1').textContent=Math.round(E(Math.min(1,t/2.2))*43);const k=t-3.2;const v=document.getElementById('v2');v.style.opacity=k<0?.15:1;v.style.transform=`scale(${k<0?1:(k<.4?1+.15*Math.sin(k/.4*Math.PI):1)})`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.8, cues={T(3.2): ov('<div class="eb">A víte, kolik</div><div class="ttl huge"><y>poslali?</y></div>')})
    elif name == "q2_zero":   # 4,80–6,70: …Nula. Nula korun.
        await setfull(pg, '<div style="position:absolute;inset:0;background:#1e2a33"></div><div class="zero" style="top:700px"><div class="n" id="z">0 Kč</div><div class="k" id="cr" style="opacity:0;font-size:80px">🦗 🦗 🦗</div></div>')
        await pg.evaluate(ov(''))
        js = ease + "const z=document.getElementById('z');z.style.transform=`scale(${t<.3?B(t/.3):1+.02*Math.sin(t*3)})`;const c=document.getElementById('cr');c.style.opacity=t<.8?0:1;c.style.transform=`translateX(${Math.sin(t*20)*6}px)`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 1.95, cues={T(.8): ov('<div class="eb">Ticho…</div><div class="ttl">Nula<br><y>korun</y></div>')})
    elif name == "q3_museum":   # 6,70–10,55: 43 lidí se přišlo jen podívat. Jako do muzea.
        await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
        await pg.evaluate(film2.TRAIN % (N, roster401(), "null"))
        await pg.evaluate(film3.NODRV)
        await pg.evaluate(STATE)
        await pg.evaluate(f"()=>{{Game.flyTo({MONA},0)}}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">43 lidí</div><div class="ttl">Jen se přišli<br><y>podívat</y></div>'))
        await film.record(pg, name, 3.85, cues={T(2.67): ov('<div class="eb">👀 👀 👀</div><div class="ttl huge">Jako do<br><y>muzea!</y></div>')})
    elif name == "q4_ok":   # 10,55–14,03: Nevadí, podpora je dobrovolná a vagón máte i bez ní.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(40,.75)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Nevadí 💛</div><div class="ttl">Podpora je<br><y>dobrovolná</y></div>'))
        await film.record(pg, name, 3.5, cues={0: "()=>{Game.flyTo(48,.75)}", T(1.9): ov('<div class="eb">Nevadí 💛</div><div class="ttl">Vagón máš<br><y>i bez ní</y></div>')})
    elif name == "q5_down":   # 14,03–19,52: Ale servery pro 1 300 vagónů nejsou zadarmo a včera nám kvůli tomu vlak spadl.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(300,1)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Ale…</div><div class="ttl">1 300 vagónů<br><y>není zadarmo</y></div>'))
        await setfull(pg, '<div id="dk" style="position:absolute;inset:0;background:#000;opacity:0"></div><div id="er" style="position:absolute;left:70px;right:70px;top:1200px;background:#cf4630;color:#fff;border-radius:30px;padding:34px 40px;font:800 58px/1.15 IS,sans-serif;text-align:center;box-shadow:0 20px 50px rgba(0,0,0,.35);transform:scale(0)">⚠️ Technická přestávka<div style="font:500 34px/1.3 PM,monospace;margin-top:12px;opacity:.9">Database has reached plan limits</div></div>')
        js = ease + "const k=t-2.9;document.getElementById('dk').style.opacity=k<0?0:Math.min(.55,k*1.5)*(Math.random()<.08?.4:1);document.getElementById('er').style.transform=`scale(${k<0?0:(k<.35?B(k/.35):1)}) rotate(${k<0?0:Math.sin(k*30)*Math.exp(-k*4)*4}deg)`;const c=document.querySelector('canvas');const z=k>0?Math.exp(-k*2.5):0;c.style.transform=`translate(${Math.sin(t*63)*24*z}px,${Math.cos(t*51)*16*z}px)`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 5.5, cues={T(2.9): ov('<div class="eb">Včera</div><div class="ttl huge">Vlak<br><y>spadl!</y></div>')})
    elif name == "q6_gold":   # 19,52–24,58: Tak jsem udělal tohle: kdo vlak podpoří, tomu se vagón promění… na ZLATÝ.
        await train(pg)
        await pg.evaluate(f"()=>{{Game.flyTo({GW},.6)}}"); await steps(pg, 220)
        await pg.evaluate(CAM, [8.5, 2.6, 9.5, -1.5, 2.9, 0])
        await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Novinka</div><div class="ttl">Tak jsem udělal<br><y>tohle…</y></div>'))
        await setfull(pg, morph_html())
        await pg.evaluate(fx(ease + "{const k=Math.max(0,t-.2);window.__cam=[8.5-k*.35,2.6+k*.04,9.5-k*.45,-1.5,2.9,0]}" + morph_js(3.2)))
        await film.record(pg, name, 5.1, cues={T(1.3): ov('<div class="eb">Kdo vlak podpoří</div><div class="ttl">Tomu se vagón<br><y>promění…</y></div>'),
                                               T(4.25): ov('<div class="eb">Pro podporovatele</div><div class="ttl huge"><y>ZLATÝ!</y> ✨</div>')})
    elif name == "q7_first":   # 24,58–29,79: Bude zářit v celém vlaku, a zlatý vagón zatím nemá nikdo. Kdo bude první?
        await train(pg, gold=True)
        await pg.evaluate("()=>{Game.setOverview(true,true)}"); await steps(pg, 90)
        await pg.evaluate(ov('<div class="eb">Celý vlak</div><div class="ttl">Bude zářit<br><y>v celém vlaku</y></div>'))
        await film.record(pg, name, 5.2, cues={T(.3): "()=>{Game.ovLook(%d,380)}" % GW,
                                               T(2.1): ov('<div class="eb">Zlatý vagón</div><div class="ttl">Zatím nemá<br><y>nikdo!</y></div>'),
                                               T(4.26): ov('<div class="eb">Zlatý vagón</div><div class="ttl huge">Kdo bude<br><y>první?</y></div>')})
    elif name == "q8_btn":   # 29,79–34,23: Tlačítko Podpořit najdeš na webu, odkaz je v profilu. Stačí i dvacka.
        await train(pg, gold=True)
        await pg.evaluate(f"()=>{{Game.flyTo({GW},.6)}}"); await steps(pg, 220)
        await pg.evaluate(CAM, [7.5, 2.65, 8.8, -1.5, 2.9, 0]); await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Na webu</div><div class="ttl">Tlačítko<br><y>Podpořit</y></div>'))
        await setfull(pg, '<div id="wb" style="position:absolute;left:50%;top:1300px;transform:translateX(-50%) scale(0);background:#fff;border-radius:30px;padding:26px 44px;box-shadow:0 18px 40px rgba(0,0,0,.3);font:800 66px/1 IS,sans-serif;color:#c2410c;white-space:nowrap">☕ Podpořit</div>'
                      '<div id="dv" style="position:absolute;left:0;right:0;top:1500px;text-align:center;opacity:0"><span class="stampG" style="transform:rotate(-4deg);font-size:80px">Stačí i 20 Kč!</span></div>')
        js = ease + "const s=t-.2;document.getElementById('wb').style.transform=`translateX(-50%) scale(${s<0?0:(s<.35?B(s/.35):1)})`;const d=t-3.34;const v=document.getElementById('dv');v.style.opacity=d<0?0:1;v.firstChild.style.transform=`rotate(-4deg) scale(${d<0?0:(d<.35?B(d/.35):1)})`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.45, cues={T(2.16): ov('<div class="eb">@vlak.followeru</div><div class="ttl">Odkaz je<br><y>v profilu</y></div>')})
    elif name == "q9_share":   # 34,23–37,92 (+dojezd): A kdo nemůže, nevadí: sdílej video, to pomůže taky.
        await train(pg, gold=True)
        await pg.evaluate("()=>{Game.flyTo(%d,.8)}" % (GW + 3)); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Nemůžeš? Nevadí 💛</div><div class="ttl">Sdílej<br><y>video!</y></div>'))
        await setfull(pg, '<div style="position:absolute;left:0;right:0;top:1250px;text-align:center"><span id="sh" style="display:inline-block;background:#fff;border-radius:999px;padding:24px 44px;font:800 62px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 12px 30px rgba(0,0,0,.25);transform:scale(0)">📤 Pošli kamarádům</span>'
                      '<div id="ht" style="margin-top:50px;font:900 70px BS,sans-serif;color:#fff;text-shadow:0 6px 0 rgba(20,40,60,.35);opacity:0">@vlak.followeru 🚂</div></div>')
        js = ease + "const s=t-1.6;document.getElementById('sh').style.transform=`scale(${s<0?0:(s<.35?B(s/.35):1)})`;document.getElementById('ht').style.opacity=t<3.2?0:Math.min(1,(t-3.2)/.3)"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.9, cues={T(2.71): ov('<div class="eb">Díky! 💛</div><div class="ttl">To pomůže<br><y>taky!</y></div>')})

ALL = ["q1_visits", "q2_zero", "q3_museum", "q4_ok", "q5_down", "q6_gold", "q7_first", "q8_btn", "q9_share"]

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
