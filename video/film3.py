# Díl 3: „Kolín vyhrál, vyrážíme!“ + strojvedoucí. Záběry po 2–5 s, něco se děje každé 1–2 s.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 30
ov = film2.ov

# vymyšlené nicky (žádní skuteční cestující)
FAKE = ["jana.n", "petr_k", "eva.v", "ondra.m", "klara.z", "tom_b", "misa.r", "adam_j", "lucka.p", "kuba_22",
        "terka.h", "vojta.s", "anet_k", "filip.d", "bara.m", "matej_v", "nela.r", "honza.t", "zuzka_b", "dan.k",
        "ema.l", "radek.p", "sara_n", "lukas.v", "ivet.k", "marek_s", "pavla.h", "ondra_b", "lenka.m", "vita_r",
        "kaja.s", "jirka_p", "verca.d", "tadeas.k", "nikol_h", "roman.z", "bety.k", "stepan_m", "alena.v", "milan.r",
        "dita.p", "patrik_s", "sona.b", "jakub.h", "evka_m", "robin.t", "hana.c"]
COATS = ["#c4453a", "#2f6f9f", "#3f8a5c", "#d9a13b", "#7a4fa3", "#e07a9b", "#2b2f3a", "#e8e0cc"]
HATS = ["koruna", "ksilt", "klobouk", "cepice", "zadna"]
DRIVER_AV = {"coat": "#c4453a", "hat": "ksilt", "pet": "zadny", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}

def roster(n=47):
    return json.dumps([[i + 1, FAKE[i % len(FAKE)], {"coat": COATS[i % 8], "hat": HATS[(i * 3) % 5], "pet": "zadny",
                        "item": "nic", "hair": "#2a1c14", "skin": "#f1c9a5"}] for i in range(n)])

TRAIN = film2.TRAIN
NODRV = "()=>{DRIVER=null;Game.setDriver(null)}"
DRV = "()=>{DRIVER=%s;Game.setDriver(DRIVER)}" % json.dumps({"nick": "tvuj.nick", "avatar": DRIVER_AV})

EXTRA = r"""
#ov .ttl.huge{font-size:210px}
#ov .ttl.mid{font-size:112px}
#ov .chip.pop{animation:none}
.lbl.drv{background:#1f7a5a!important;border-color:#ffd23f!important;color:#fff!important}
#ov .opts.two div{font-size:64px;padding:30px 0}
#ov .opts div.on{background:#ffd23f;color:#1e2a33;box-shadow:0 10px 0 #c9a12a;transform:scale(1.08)}
"""

# mapa: Praha → Kolín, rozcestí v Kolíně. vb() spočítá výřez kolem vybraných bodů.
MAP3 = r"""()=>{
  const f=document.getElementById('full');f.style.display='block';
  f.innerHTML='<div style="position:absolute;inset:0;background:linear-gradient(#4f9fe0,#9fd0f2 55%,#e4f3fb)"></div><div id="mapbox" style="position:absolute;left:40px;right:40px;top:640px;height:520px;background:#eef3e4;border-radius:36px;border:6px solid #fff;box-shadow:0 20px 50px rgba(20,40,60,.3);overflow:hidden"><svg id="map" style="width:100%;height:100%;display:block"></svg></div>';
  ONLINE=true;S.followers=47;S.route=['praha','kolin'];S.vote={at:'kolin',deadline:'',options:['pardubice','hbrod'].map(to=>({to,votes:1}))};
  renderMap();
  const svg=document.getElementById('map');svg.style.height='100%';svg.setAttribute('preserveAspectRatio','xMidYMid meet');
  svg.querySelectorAll('text').forEach(t=>{if(/%$/.test(t.textContent))t.textContent='?'});
  const P=id=>proj(S.nodes[id]);const I=info();
  const a=P(I.head.leg.from),b=P(I.head.leg.to);window.__HEAD=[a[0]+(b[0]-a[0])*I.head.t,a[1]+(b[1]-a[1])*I.head.t];
  window.__P=P;const AR=1000/520;
  window.__vb=(cx,cy,w)=>{const h=w/AR;svg.setAttribute('viewBox',`${cx-w/2} ${cy-h/2} ${w} ${h}`)};
  window.__onframe=null;
}"""

async def mk(b):
    ctx, pg = await film2.mkpage(b)
    await pg.add_style_tag(content=EXTRA)
    await pg.route("**/api/world*", lambda r: r.abort())  # žádné obnovování světa během natáčení
    return ctx, pg

async def steps(pg, n):
    await film2.steps(pg, n)

def T(t):
    return int(round(t * FPS))

async def shot(pg, name):
    if name == "k1_hook":   # 0–2,73: Kolín vyhrál! Vyrážíme z Prahy!
        await pg.evaluate(TRAIN % (47, roster(), "null")); await pg.evaluate(NODRV)
        await pg.evaluate("()=>{Game.flyTo(0,.85)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Hlasování skončilo</div><div class="ttl huge">Kolín<br><y>vyhrál!</y></div><div class="chip">Kolín <b>50 %</b> hlasů</div>'))
        cues = {0: "()=>{Game.flyTo(0,.42)}",
                T(1.3): ov('<div class="eb">Směr Kolín</div><div class="ttl huge">Vyrážíme<br><y>z Prahy!</y></div>')}
        await film.record(pg, name, 3.0, cues=cues)
    elif name == "k2_long":   # 2,73–6,47: Je nás 47 a vlak je dlouhý přes kilometr
        await pg.evaluate(TRAIN % (47, roster(), "null")); await pg.evaluate(NODRV)
        await pg.evaluate("()=>{Game.flyTo(0,.55)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Vlak followerů</div><div class="ttl huge">Je nás <y>47</y></div>'))
        cues = {0: "()=>{Game.flyTo(47,.55)}",
                T(1.55): ov('<div class="eb">Vlak followerů</div><div class="ttl huge">Je nás <y>47</y></div><div class="chip">vlak je dlouhý <b>1,18 km</b></div>'),
                T(3.0): "()=>{Game.flyTo(47,1)}"}
        await film.record(pg, name, 4.0, cues=cues)
    elif name == "k3_map":   # 6,47–10,65: Do Kolína 62 km… takže ještě kousek
        await pg.evaluate(MAP3); await steps(pg, 2)
        await pg.evaluate("()=>{const s=document.getElementById('map');s.style.height='100%';s.style.width='100%'}")
        await pg.evaluate("()=>{const a=__P('praha'),b=__P('kolin');__vb((a[0]+b[0])/2,(a[1]+b[1])/2+6,Math.max(380,Math.abs(b[0]-a[0])*3))}")
        await pg.evaluate(ov('<div class="eb">Praha → Kolín</div><div class="ttl">Do Kolína<br><y>62 km</y></div>'))
        zoom = r"""()=>{const a=__P('praha'),b=__P('kolin'),h=__HEAD;const c0=[(a[0]+b[0])/2,(a[1]+b[1])/2+6],w0=Math.max(380,Math.abs(b[0]-a[0])*3),w1=150;const t0=__vt();
          window.__onframe=vt=>{const u=Math.min(1,(vt-t0)/700),e=u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;const w=w0*Math.pow(w1/w0,e);const k=(w0-w)/(w0-w1);__vb(c0[0]+(h[0]-c0[0])*k,c0[1]+(h[1]-12-c0[1])*k,w)}}"""
        cues = {T(1.6): zoom,
                T(1.75): ov('<div class="eb">Praha → Kolín</div><div class="ttl">Zatím jsme ujeli<br><y>1,18 km</y></div>'),
                T(2.45): ov('<div class="eb">Praha → Kolín</div><div class="ttl">…takže ještě<br><y>kousek</y></div><div class="chip">zbývá <b>60,8 km</b></div>')}
        await film.record(pg, name, 4.4, cues=cues)
    elif name == "k4_new":   # 10,65–11,95: A teď novinka
        await pg.evaluate("""()=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='98';
          f.innerHTML='<div id="rays" style="position:absolute;left:50%;top:50%;width:2800px;height:2800px;margin:-1400px 0 0 -1400px;background:repeating-conic-gradient(#ffd23f 0 10deg,#ffbf1f 10deg 20deg)"></div><div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(255,255,255,.55),rgba(255,255,255,0) 55%)"></div><div id="stamp" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(0) rotate(-8deg);font:900 250px/0.9 BS,sans-serif;text-transform:uppercase;color:#1e2a33;text-align:center;text-shadow:0 10px 0 rgba(255,255,255,.7)">A teď<br><span style="color:#c4453a">novinka!</span></div>';
          document.getElementById('ov').innerHTML='';
          const t0=__vt();window.__onframe=vt=>{const t=(vt-t0)/1000;document.getElementById('rays').style.transform=`rotate(${t*40}deg)`;
            const u=Math.min(1,t/.35),s=u<1?1.25*Math.sin(u*Math.PI/2)/Math.sin(Math.PI/2)*(1+.18*Math.sin(u*Math.PI)):1;
            document.getElementById('stamp').style.transform=`translate(-50%,-50%) scale(${t<.35?s:1+.03*Math.sin((t-.35)*9)}) rotate(-8deg)`}}""")
        await film.record(pg, name, 1.5)
    elif name == "k5_driver":   # 11,95–17,31: strojvedoucí, jeho panáček řídí celý vlak
        await pg.evaluate(TRAIN % (47, roster(), "null")); await pg.evaluate(NODRV)
        await pg.evaluate("()=>{Game.flyTo(0,0);Game.setShift(-.24)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Na každé stanici</div><div class="ttl">Losujeme<br><y>strojvedoucího</y></div>'))
        pop = DRV[:-1] + r""";const g=__G.driverSlot.children[0];const t0=__vt();window.__onframe=vt=>{const u=Math.min(1,(vt-t0)/450);const s=u<1?Math.sin(u*Math.PI*.5)*(1+.35*Math.sin(u*Math.PI)):1;g.scale.setScalar(Math.max(.01,s))}}"""
        cues = {T(1.4): ov('<div class="eb">Na každé stanici</div><div class="ttl">Losujeme<br><y>strojvedoucího</y></div><div class="chip">kabina zatím <b>prázdná</b></div>'),
                T(2.86): pop,
                T(2.9): ov('<div class="eb">Strojvedoucí</div><div class="ttl">Tvůj panáček<br><y>řídí vlak!</y></div>'),
                T(4.1): "()=>{Game.setShift(0);Game.flyTo(0,.5)}"}
        await film.record(pg, name, 5.6, cues=cues)
    elif name == "k6_draw":   # 17,31–21,06: losujeme jen z lidí s jízdenkou, vyzvedni si ji v biu
        await pg.evaluate(TRAIN % (47, roster(), "null")); await pg.evaluate(NODRV)
        await pg.evaluate("()=>{Game.flyTo(6,.6)}"); await steps(pg, 150)
        names = [n for n in FAKE[5:35]] + ["tvuj.nick"]
        await pg.evaluate("""names=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex='98';
          f.innerHTML=`<div style="position:absolute;inset:0;background:rgba(20,35,45,.45)"></div>
          <div style="position:absolute;left:110px;right:110px;top:760px;background:#fffaf0;border-radius:40px;border:6px solid #f0a03a;box-shadow:0 30px 70px rgba(0,0,0,.35);padding:34px 0 40px;text-align:center">
            <div style="font:600 30px PM,monospace;letter-spacing:.18em;text-transform:uppercase;color:#8a4508">Losování · Kolín</div>
            <div style="font:900 70px/1 BS,sans-serif;text-transform:uppercase;color:#1e2a33;margin-top:10px">Strojvedoucí</div>
            <div id="win" style="margin:28px 50px 0;height:150px;overflow:hidden;border-radius:24px;background:#1f7a5a;position:relative;box-shadow:inset 0 0 0 5px #d9a13b">
              <div id="reel" style="position:absolute;left:0;right:0;top:0">${names.map(n=>`<div style="height:150px;line-height:150px;font:800 70px IS,sans-serif;color:#fff">@${n}</div>`).join('')}</div></div>
            <div id="tk" style="margin-top:26px;font:700 40px IS,sans-serif;color:#3f8a5c;opacity:0">má jízdenku · jede!</div></div>`;
          const N=names.length-1,t0=__vt();window.__onframe=vt=>{const t=(vt-t0)/1000;const u=Math.min(1,t/1.6),e=1-Math.pow(1-u,4);
            document.getElementById('reel').style.transform=`translateY(${-e*N*150}px)`;
            if(t>1.65){const w=document.getElementById('win');w.style.background='#ffd23f';w.querySelectorAll('#reel div')[N].style.color='#1e2a33';document.getElementById('tk').style.opacity=1}}}""", names)
        await pg.evaluate(ov('<div class="eb">Pozor</div><div class="ttl mid">Jen z lidí<br>s <y>jízdenkou</y></div>'))
        cues = {T(1.8): ov('<div class="eb">Pozor</div><div class="ttl mid">Jen z lidí<br>s <y>jízdenkou</y></div><div class="chip" style="margin-top:760px">jízdenka je <b>v biu</b></div>')}
        await film.record(pg, name, 4.0, cues=cues)
    elif name == "k7_split":   # 21,06–25,02: v Kolíně se trať dělí. Pardubice, nebo Havlíčkův Brod?
        await pg.evaluate(MAP3); await steps(pg, 2)
        await pg.evaluate("()=>{const s=document.getElementById('map');s.style.height='100%';s.style.width='100%'}")
        await pg.evaluate("()=>{const k=__P('kolin'),p=__P('pardubice'),h=__P('hbrod');const xs=[k[0],p[0],h[0]],ys=[k[1],p[1],h[1]];const cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;window.__C=[cx,cy];__vb(cx,cy+8,Math.max((Math.max(...xs)-Math.min(...xs))*1.9,(Math.max(...ys)-Math.min(...ys))*1.9*1000/520))}")
        await pg.evaluate("()=>{document.getElementById('mapbox').style.top='560px'}")
        await pg.evaluate(ov('<div class="eb">Stanice Kolín</div><div class="ttl">Tady se<br><y>trať dělí</y></div><div style="height:640px"></div><div class="opts two" id="op" style="opacity:0"><div id="o0">Pardubice</div><div id="o1">Havl. Brod</div></div>'))
        def on(i):
            return "()=>{document.querySelectorAll('#ov .opts div').forEach(d=>d.classList.remove('on'));" + (f"document.getElementById('o{i}').classList.add('on')" if i >= 0 else "") + "}"
        cues = {T(1.96): "()=>{document.getElementById('op').style.opacity=1;document.querySelector('#ov .ttl').innerHTML='Kudy<br><y>dál?</y>'}",
                T(2.15): on(0), T(2.85): on(1), T(3.6): on(-1)}
        await film.record(pg, name, 4.2, cues=cues)
    elif name == "k8_cta":   # 25,02–konec: piš do komentářů
        await pg.evaluate("()=>{document.getElementById('full').style.display='none'}")
        await pg.evaluate(TRAIN % (47, roster(), "null")); await pg.evaluate(DRV)
        await pg.evaluate("()=>{Game.flyTo(0,.55)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Piš do<br><y>komentářů!</y></div>'))
        cues = {0: "()=>{Game.flyTo(0,.38)}"}
        await film.record(pg, name, 2.8, cues=cues)

ALL = ["k1_hook", "k2_long", "k3_map", "k4_new", "k5_driver", "k6_draw", "k7_split", "k8_cta"]

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
