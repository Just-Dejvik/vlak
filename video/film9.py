# Díl 9: „Kolik je vlastně 1 121 vagónů?“ Celý vlak shora (28 km) a hlasování v Berlíně (vede Paříž).
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 1121
KM = "28"
ME = 640  # ukázkový „tvůj“ vagón (smyšlený nick)
ROUTE = ['praha', 'kolin', 'pardubice', 'hradec', 'liberec', 'vratislav', 'poznan', 'berlin']
VOTES = [("pariz", "Paříž", 18), ("kodan", "Kodaň", 4), ("hamburk", "Hamburk", 0)]

EXTRA = r"""
#ovPins .ovcap{display:none}
.ovpin{font-size:30px!important;padding:14px 20px!important;border-radius:14px!important}
.ovpin::after{border-width:12px!important;bottom:-12px!important;margin-left:-12px!important}
.ruler{position:absolute;height:0;border-top:8px solid #ffd23f;opacity:0}
.ruler:before,.ruler:after{content:"";position:absolute;top:-34px;width:8px;height:60px;background:#ffd23f}
.ruler:before{left:-4px}.ruler:after{right:-4px}
.ruler b{position:absolute;left:50%;top:-112px;transform:translateX(-50%);background:#ffd23f;color:#1e2a33;border-radius:999px;padding:12px 30px;font:900 70px/1 BS,sans-serif;white-space:nowrap}
.bars{position:absolute;left:80px;right:80px;top:1250px;display:grid;gap:26px}
.bar{display:grid;grid-template-columns:260px 1fr 110px;align-items:center;gap:20px;font:900 64px/1 BS,sans-serif;text-transform:uppercase;color:#fff;text-shadow:0 4px 0 rgba(20,40,60,.35)}
.bar i{display:block;height:64px;border-radius:18px;background:#fff;box-shadow:0 8px 20px rgba(0,0,0,.2);width:0}
.bar.win i{background:#ffd23f}.bar.win{color:#ffd23f}
.bar span{text-align:right}
"""

STATE = ("()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.route=%s;S.vote={at:'berlin',deadline:'',options:%s};renderHud()}"
         % (N, N, json.dumps(ROUTE), json.dumps([{"to": t, "votes": v} for t, _, v in VOTES])))

def roster():
    r = json.loads(film3.roster(700))
    r[ME - 1][1] = "ty.tvuj.nick"
    return json.dumps(r)

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=EXTRA)
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg, mine=False):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, roster(), "null"))
    await pg.evaluate(STATE)
    await pg.evaluate(film3.NODRV)
    if mine:
        await pg.evaluate("()=>{myTicket={wagon:%d,nick:'ty.tvuj.nick',avatar:null,public:true,status:'verified'}}" % ME)

async def shot(pg, name):
    if name == "z1_count":   # 0–8,57: Kolik je vlastně 1 121 vagónů? Každý… jeden vagón, a každý vagón má 25 metrů.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(40,.9)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Vlak followerů</div><div class="ttl">Kolik je<br><y>1 121 vagónů?</y></div>'))
        await setfull(pg, '<div class="ruler" id="ru"><b>25 m</b></div>')
        js = ease + """const ru=document.getElementById('ru');const k=t-6.0;
          if(k>-0.1){const c=__G.camera;const sl=__G.slots.find(s=>s.n===5&&s.g.visible);if(sl){const x=sl.g.position.x;
            const a=new THREE.Vector3(x-6,4.9,1.6).project(c),b=new THREE.Vector3(x+6,4.9,1.6).project(c);
            const ax=(a.x*.5+.5)*1080,bx=(b.x*.5+.5)*1080,y=(-a.y*.5+.5)*1920;const w=(bx-ax)*E(Math.max(0,k)/.45);
            ru.style.left=ax+'px';ru.style.top=(y-30)+'px';ru.style.width=Math.max(0,w)+'px';ru.style.opacity=k<0?0:1}}"""
        await pg.evaluate(fx(js))
        cues = {0: "()=>{Game.flyTo(12,.75)}",
                T(3.44): ov('<div class="eb">Pravidlo hry</div><div class="ttl">1 cestující =<br><y>1 vagón</y></div>'),
                T(3.5): "()=>{Game.flyTo(5,.42)}",
                T(5.91): ov('<div class="eb">Pravidlo hry</div><div class="ttl">Každý vagón<br><y>25 metrů</y></div>')}
        await film.record(pg, name, 8.6, cues=cues)
    elif name == "z2_reveal":   # 8,57–14,23: Takže… tohle je náš vlak. Celý. Osmadvacet kilometrů!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.55)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="eb">Vlak followerů</div><div class="ttl huge">Takže…</div>'))
        cues = {T(1.1): "()=>{Game.setOverview(true,true)}",
                T(1.27): ov('<div class="eb">Celý vlak shora</div><div class="ttl">Tohle je<br><y>náš vlak</y></div>'),
                T(2.84): ov('<div class="eb">Celý vlak shora</div><div class="ttl huge"><y>Celý!</y></div>'),
                T(3.68): ov(f'<div class="eb">{N:,} vagónů × 25 m'.replace(',', ' ') + f'</div><div class="ttl huge"><y>{KM} km!</y></div>')}
        await film.record(pg, name, 5.7, cues=cues)
    elif name == "z3_wiggle":   # 14,23–18,47: Tady se jen vlní, ať se vejde. Ve skutečnosti jede rovně dál.
        await train(pg)
        await pg.evaluate("()=>{Game.setOverview(true,true)}"); await steps(pg, 90)
        await pg.evaluate(ov('<div class="eb">Celý vlak shora</div><div class="ttl">Tady se jen<br><y>vlní</y></div>'))
        await setfull(pg, '<svg id="sq" viewBox="0 0 900 140" style="position:absolute;left:90px;top:1500px;width:900px;opacity:0"><path id="sqp" d="M20 70 C 120 -20, 200 160, 300 70 S 480 -20, 580 70 S 760 160, 880 70" fill="none" stroke="#ffd23f" stroke-width="16" stroke-linecap="round"/></svg>')
        js = ease + """const k=t-1.6;const sq=document.getElementById('sq');sq.style.opacity=t<.3?0:1;
          const p=document.getElementById('sqp');const u=E(Math.max(0,k)/.8);
          const y=a=>70+(a*(1-u)).toFixed(1)*1;p.setAttribute('d',`M20 70 C 120 ${70-90*(1-u)}, 200 ${70+90*(1-u)}, 300 70 S 480 ${70-90*(1-u)}, 580 70 S 760 ${70+90*(1-u)}, 880 70`)"""
        await pg.evaluate(fx(js))
        cues = {T(1.91): ov('<div class="eb">Ve skutečnosti</div><div class="ttl">Jede rovně<br><y>dál</y></div>')}
        await film.record(pg, name, 4.3, cues=cues)
    elif name == "z4_you":   # 18,47–23,58: A tohle jsi ty. Na webu si teď můžeš najít svůj vagón v celém vlaku.
        await train(pg, mine=True)
        await pg.evaluate("()=>{Game.setOverview(true,true)}"); await steps(pg, 90)
        await pg.evaluate(ov('<div class="eb">Celý vlak shora</div><div class="ttl">A tohle<br><y>jsi ty!</y></div>'))
        cues = {T(.25): "()=>{Game.ovLook(%d,420)}" % ME,
                T(1.67): ov('<div class="eb">Nové na webu</div><div class="ttl">Najdi svůj<br><y>vagón</y></div>'),
                T(3.4): "()=>{Game.ovLook(null)}"}
        await film.record(pg, name, 5.2, cues=cues)
    elif name == "z5_vote":   # 23,58–28,55: Mimochodem, v Berlíně se hlasuje, kam dál. Zatím jasně vede Paříž!
        await pg.evaluate(film7.map7(N))
        await pg.evaluate(STATE.replace("renderHud()", "renderMap()"))
        await pg.evaluate(ov('<div class="eb">Výhybka v Berlíně</div><div class="ttl">Kam<br><y>dál?</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          '<div class="bars">' + ''.join(f'<div class="bar{" win" if i == 0 else ""}" id="b{i}" style="opacity:0"><div>{n}</div><i id="bi{i}"></i><span id="bn{i}">0</span></div>' for i, (_, n, _v) in enumerate(VOTES)) + '</div>')
        js = ease + "const V=%s;const mx=Math.max(...V,1);for(let i=0;i<3;i++){const k=t-2.8-i*.15;document.getElementById('b'+i).style.opacity=k<0?0:1;const u=E(Math.max(0,k)/.9);document.getElementById('bi'+i).style.width=(V[i]/mx*100*u)+'%%';document.getElementById('bn'+i).textContent=Math.round(V[i]*u)}" % json.dumps([v for *_, v in VOTES])
        await pg.evaluate(fx(js))
        cues = {T(2.78): ov('<div class="eb">Zatím vede</div><div class="ttl huge"><y>Paříž!</y></div>')}
        await film.record(pg, name, 5.0, cues=cues)
    elif name == "z6_comment":   # 28,55–33,04: Kodaň a Hamburk ještě mají šanci, tak napiš do komentářů, kam chceš ty.
        await pg.evaluate(film7.map7(N))
        await pg.evaluate(STATE.replace("renderHud()", "renderMap()"))
        await pg.evaluate(ov('<div class="eb">Výhybka v Berlíně</div><div class="ttl">Kodaň? Hamburk?<br><y>Ještě je šance!</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}",
                          '<div class="bars">' + ''.join(f'<div class="bar{" win" if i == 0 else ""}"><div>{n}</div><i style="width:{v / 18 * 100:.0f}%"></i><span>{v}</span></div>' for i, (_, n, v) in enumerate(VOTES)) + '</div>'
                          '<div style="position:absolute;left:0;right:0;top:1580px;text-align:center"><div class="stampG" id="st" style="background:#3f8a5c;box-shadow:0 10px 0 #2b6342">💬 Napiš, kam chceš ty!</div></div>')
        js = ease + "const s=t-2.1;document.getElementById('st').style.transform=`rotate(-4deg) scale(${s<0?0:(s<.35?B(s/.35):1)})`"
        await pg.evaluate(fx(js))
        await film.record(pg, name, 4.5, cues={T(2.1): ov('<div class="eb">Hlasuj v komentářích</div><div class="ttl">Kam chceš<br><y>ty?</y></div>')})
    elif name == "z7_outro":
        os.environ["OUTRO_AT"] = "0.05,1.7,3.05"
        os.environ["OUTRO_LEN"] = "6.6"
        await film5.shot(pg, "v7_outro")

ALL = ["z1_count", "z2_reveal", "z3_wiggle", "z4_you", "z5_vote", "z6_comment", "z7_outro"]

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
