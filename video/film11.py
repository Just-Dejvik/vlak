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
    r = json.loads(film3.roster(300))
    r[GW - 1][1] = GNICK
    return json.dumps(r)

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=EXTRA)
    return ctx, pg

async def train(pg, gold=False):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, roster(), "null"))
    await pg.evaluate("()=>{S.kmPerPassenger=1;S.peak=1478;S.supporters=%s}" % (json.dumps([GNICK]) if gold else "[]"))
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

async def shot(pg, name):
    if name == "g_test":   # zkouška proměny
        await train(pg)
        await pg.evaluate(f"()=>{{Game.flyTo({GW},.6)}}"); await steps(pg, 220)
        await pg.evaluate(CAM, [8.5, 2.6, 9.5, -1.5, 2.9, 0])
        await steps(pg, 5)
        await pg.evaluate(ov('<div class="eb">Pro podporovatele</div><div class="ttl">Vagón se mění<br><y>na ZLATÝ</y></div>'))
        await setfull(pg, morph_html())
        await pg.evaluate(fx(ease + "{const k=Math.max(0,t-.2);window.__cam=[8.5-k*.5,2.6+k*.05,9.5-k*.6,-1.5,2.9,0]}" + morph_js(1.0)))
        await film.record(pg, name, 4.0, cues={T(2.1): ov('<div class="eb">Pro podporovatele</div><div class="ttl huge"><y>ZLATÝ!</y> ✨</div>')})

async def main():
    names = sys.argv[1:] or ["g_test"]
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
