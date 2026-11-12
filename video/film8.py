# Díl 8: „Tak tohle jsem ještě neviděl!“ Splněná přání (bazén, Mona Lisa, terárium), jsme v Berlíně, kam dál?
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4, film5, film6, film7
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
setfull = film5.setfull
N = 993
ROUTE = ['praha', 'kolin', 'pardubice', 'hradec', 'liberec', 'vratislav', 'poznan', 'berlin']
# výherci přání: skuteční panáčci z webu (přání napsali veřejně do komentářů, nick mají veřejný)
WIN = {
    264: ["mr__chesee", {"coat": "#7a4fa3", "hat": "zadna", "pet": "kocka", "item": "hrnek", "hair": "#6b3f22", "skin": "#6e4a33"}, ["terarium"]],
    401: ["dudonlukas", {"coat": "#2f6f9f", "hat": "zadna", "pet": "pes", "item": "kytara", "hair": "#6b3f22", "skin": "#9c6b48"}, ["monalisa"]],
    541: ["karaulovzachar", {"coat": "#c4453a", "hat": "koruna", "pet": "kocka", "item": "hrnek", "hair": "#c9a35a", "skin": "#f1c9a5"}, ["bazen"]],
}

def roster():
    r = json.loads(film3.roster(600))
    for w, (nick, av, ex) in WIN.items():
        r[w - 1] = [w, nick, av, ex]
    return json.dumps(r)

EXTRA = r"""
.ring{position:absolute;width:330px;height:330px;margin:-165px 0 0 -165px;border:12px solid #ffd23f;border-radius:50%;box-shadow:0 0 0 6px rgba(20,32,44,.35),inset 0 0 0 6px rgba(20,32,44,.35);opacity:0}
.tag8{position:absolute;background:#ffd23f;color:#1e2a33;border-radius:999px;padding:16px 30px;font:900 60px/1 BS,sans-serif;text-transform:uppercase;box-shadow:0 12px 30px rgba(0,0,0,.3);transform:translate(-50%,0) scale(0);white-space:nowrap}
.cm{position:absolute;background:#fff;border-radius:30px;padding:18px 28px;font:700 44px/1.15 IS,sans-serif;color:#1e2a33;box-shadow:0 14px 34px rgba(0,0,0,.25);opacity:0;max-width:820px}
.cm small{display:block;font:600 30px PM,monospace;color:#7d8a7e;margin-bottom:6px}
.top3{position:absolute;left:70px;right:70px;top:1180px;display:grid;gap:22px}
.top3 div{background:#fffaf0;border:6px solid #f0a03a;border-radius:30px;padding:22px 32px;font:800 58px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 14px 34px rgba(0,0,0,.25);opacity:0;transform:scale(.4)}
.top3 b{color:#e08a12;margin-right:18px}
.feat{position:absolute;left:70px;right:70px;top:1330px;display:flex;gap:18px;justify-content:center}
.feat div{background:#fffaf0;border:6px solid #f0a03a;border-radius:28px;padding:18px 26px;font:800 48px/1 IS,sans-serif;color:#1e2a33;box-shadow:0 14px 34px rgba(0,0,0,.25);opacity:0;transform:scale(.4)}
.opt{position:absolute;left:70px;right:70px;display:flex;gap:18px;justify-content:center;top:1300px}
.opt div{background:#fff;border-radius:999px;padding:20px 34px;font:900 64px/1 BS,sans-serif;text-transform:uppercase;color:#2b6342;box-shadow:0 12px 30px rgba(0,0,0,.25);opacity:0;transform:scale(.4)}
"""

STATE = "()=>{ONLINE=true;S.kmPerPassenger=1;S.followers=%d;S.peak=%d;S.route=%s;S.vote={at:'berlin',deadline:'',options:[]};renderHud()}" % (N, N, json.dumps(ROUTE))

async def mk(b):
    ctx, pg = await film6.mk(b)
    await pg.add_style_tag(content=EXTRA)
    await pg.evaluate(STATE)
    return ctx, pg

async def train(pg):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, roster(), "null"))
    await pg.evaluate(STATE)
    await pg.evaluate(film3.NODRV)

# kroužek kolem věci ve vagónu: souřadnice uvnitř interiéru → obrazovka
def ring_js(x, y, z, t0, tag=None, dy=210):
    js = (f"{{const v=new THREE.Vector3(__G.interior.position.x+({x}),{y},{z}).project(__G.camera);const px=(v.x*.5+.5)*1080,py=(-v.y*.5+.5)*1920;"
          f"const e=document.getElementById('rg');const k=t-{t0};e.style.left=px+'px';e.style.top=py+'px';e.style.opacity=k<0?0:Math.min(1,k/.15);e.style.transform=`scale(${{k<0?1.6:(k<.35?1.6-.6*E(k/.35):1+.04*Math.sin(t*8))}})`;")
    if tag:
        js += f"const g=document.getElementById('tg');g.style.left=px+'px';g.style.top=(py+{dy})+'px';g.style.transform=`translate(-50%,0) scale(${{k<.2?0:(k<.55?B((k-.2)/.35):1)}})`;"
    return js + "}"

def ring_html(tag=None):
    return '<div class="ring" id="rg"></div>' + (f'<div class="tag8" id="tg">{tag}</div>' if tag else '')

async def shot(pg, name):
    if name == "y1_hook":   # 0–4,99: Tak tohle jsem ještě neviděl! Zachar chce do vagónu… BAZÉN!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(533,.6)}"); await steps(pg, 200)
        await pg.evaluate(ov('<div class="ttl huge">Tohle jsem<br><y>neviděl!</y></div>'))
        await setfull(pg, ring_html('🏊 Bazén!'))
        await pg.evaluate(fx(ease + "const c=document.querySelector('canvas');const k=t>3.75?Math.exp(-(t-3.75)*3):0;c.style.transform=`translate(${Math.sin(t*63)*26*k}px,${Math.cos(t*51)*18*k}px) scale(${1+.05*k})`;" + ring_js(-1.75, 1.55, .68, 3.8, None)))
        cues = {0: "()=>{Game.flyTo(541,.6)}",
                T(2.2): ov('<div class="eb">@karaulovzachar · vagón 541</div><div class="ttl">Zachar chce<br><y>do vagónu…</y></div>'),
                T(2.3): "()=>{Game.flyTo(541,0)}",
                T(3.75): ov('<div class="eb">@karaulovzachar · vagón 541</div><div class="ttl huge"><y>Bazén!</y></div>')}
        await film.record(pg, name, 5.1, cues=cues)
    elif name == "y2_got":   # 4,99–7,42: Tak ho dostal! A to není všechno.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(541,0)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">@karaulovzachar · vagón 541</div><div class="ttl">Tak ho<br><y>dostal!</y></div>'))
        await setfull(pg, ring_html('🏊 Splněno!'))
        await pg.evaluate(fx(ease + ring_js(-1.75, 1.55, .68, 0.0, True)))
        cues = {T(1.16): ov('<div class="eb">Přání do vagónu</div><div class="ttl">A to není<br><y>všechno!</y></div>')}
        await film.record(pg, name, 2.6, cues=cues)
    elif name == "y3_comments":   # 7,42–14,62: ptal jsem se vás… přes 200 komentářů. Vybral jsem tři nejšílenější.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(200,.75)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Minulé video</div><div class="ttl">Co chceš<br><y>ve vagónu?</y></div>'))
        cms = [("🐍 terárium", 70, 560), ("🍕 pizza automat", 420, 700), ("🏊 bazén", 110, 860), ("🎮 PlayStation", 470, 1010), ("🖼️ Mona Lisa", 90, 1160), ("🛋️ vířivka", 520, 1300), ("🐶 další pes", 140, 1450)]
        top = [("1.", "🏊 Bazén"), ("2.", "🖼️ Mona Lisa"), ("3.", "🐍 Terárium")]
        await setfull(pg, '<div style="position:absolute;inset:0;background:rgba(20,35,45,.3)"></div>'
                      '<div id="cnt" style="position:absolute;left:0;right:0;top:1640px;text-align:center"><span class="stampG" style="background:#2f6f9f;box-shadow:0 10px 0 #1f4f8a;transform:rotate(-3deg)" id="cn">💬 0 komentářů</span></div>'
                      '<div id="cms">' + ''.join(f'<div class="cm" id="c{i}" style="left:{x}px;top:{y}px">{n}</div>' for i, (n, x, y) in enumerate(cms)) + '</div>'
                      '<div class="top3" id="top">' + ''.join(f'<div id="p{i}"><b>{a}</b>{b}</div>' for i, (a, b) in enumerate(top)) + '</div>')
        js = ease + """const n=Math.round(E((t-.4)/4.2)*251);document.getElementById('cn').textContent='💬 '+(n>=200?'200+':n)+' komentářů';
          const q=t-4.9;for(let i=0;i<7;i++){const k=t-.3-i*.42;const e=document.getElementById('c'+i);e.style.opacity=k<0?0:(q>0?Math.max(0,1-q/.3):1);e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)}) translateY(${Math.sin(t*2+i)*10}px) rotate(${Math.sin(i*1.7)*4}deg)`}
          document.getElementById('cnt').style.opacity=q>0?Math.max(0,1-q/.3):1;
          for(let i=0;i<3;i++){const k=t-5.1-i*.38;const e=document.getElementById('p'+i);e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}"""
        await pg.evaluate(fx(js))
        cues = {T(2.85): ov('<div class="eb">Minulé video</div><div class="ttl">Přes 200<br><y>komentářů!</y></div>'),
                T(5.03): ov('<div class="eb">Přání do vagónu</div><div class="ttl">Tři<br><y>nejšílenější</y></div>')}
        await film.record(pg, name, 7.3, cues=cues)
    elif name == "y4_mona":   # 14,62–19,89: Lukáš chtěl Monu Lisu. Tady ji má, i s provazem…
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(380,.5)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">@dudonlukas · vagón 401</div><div class="ttl">Lukáš chtěl<br><y>Monu Lisu</y></div>'))
        await setfull(pg, ring_html('🖼️ Mona Lisa'))
        await pg.evaluate(fx(ease + ring_js(-2.4, 2.75, -1.33, 2.0, True, 200)))
        cues = {0: "()=>{Game.flyTo(401,0)}",
                T(2.02): ov('<div class="eb">@dudonlukas · vagón 401</div><div class="ttl huge">Tady ji<br><y>má!</y></div>'),
                T(2.88): ov('<div class="eb">@dudonlukas · vagón 401</div><div class="ttl">I s<br><y>provazem!</y></div>')}
        await film.record(pg, name, 5.4, cues=cues)
    elif name == "y5_terra":   # 19,89–25,88: A Sýr chtěl terárium s hadem, želvou a ještěrkou. Všichni tři už jedou s ním.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(240,.5)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">@mr__chesee · vagón 264</div><div class="ttl">Sýr chtěl<br><y>terárium</y></div>'))
        await setfull(pg, ring_html('🐍 🐢 🦎') + '<div class="feat"><div id="f0">🐍 had</div><div id="f1">🐢 želva</div><div id="f2">🦎 ještěrka</div></div>')
        await pg.evaluate(fx(ease + ring_js(2.35, 2.1, -.95, 1.6, True, 190) + "const A=[2.1,2.7,3.25];for(let i=0;i<3;i++){const k=t-A[i];const e=document.getElementById('f'+i);e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}"))
        cues = {0: "()=>{Game.flyTo(264,0)}",
                T(3.86): ov('<div class="eb">@mr__chesee · vagón 264</div><div class="ttl">Všichni tři<br><y>jedou s ním!</y></div>')}
        await film.record(pg, name, 6.1, cues=cues)
    elif name == "y6_berlin":   # 25,88–31,97: Mezitím nás je skoro tisíc. Takže jsme… v Berlíně! Koukněte, co za námi stojí.
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(0,.62)}"); await steps(pg, 200)
        await pg.evaluate(ov(''))
        await setfull(pg, '<div id="bg6" style="position:absolute;inset:0;background:linear-gradient(#1f4f8a,#2f6f9f)"></div><div id="cnt" style="position:absolute;left:0;right:0;top:640px;text-align:center"><div style="font:600 44px PM,monospace;letter-spacing:.18em;color:#fff;text-transform:uppercase">Je nás</div><div class="big-n" id="n1">0</div></div>'
                      '<div id="dots" style="position:absolute;left:0;right:0;top:1150px;text-align:center;font:900 120px BS,sans-serif;color:#ffd23f;opacity:0">Takže jsme…</div>'
                      '<div id="fl" style="position:absolute;inset:0;background:#fff;opacity:0"></div>')
        js = ease + f"""const n=Math.round(E(t/1.6)*{N});document.getElementById('n1').textContent=n.toLocaleString('cs-CZ');
          document.getElementById('dots').style.opacity=t<2.23?0:Math.min(1,(t-2.23)/.2);
          const r=t-3.09;['bg6','cnt','dots'].forEach(i=>document.getElementById(i).style.opacity=r<0?(i==='dots'?document.getElementById('dots').style.opacity:1):0);
          document.getElementById('fl').style.opacity=r<0?0:Math.max(0,1-r/.45)"""
        await pg.evaluate(fx(js))
        cues = {T(3.09): ov('<div class="eb">Poznaň → Berlín</div><div class="ttl huge">V Berlíně!</div>'),
                T(3.2): "()=>{Game.flyTo(0,.45)}",
                T(4.3): ov('<div class="eb">Berlín</div><div class="ttl">Koukni,<br><y>co za námi stojí</y></div>')}
        await film.record(pg, name, 6.2, cues=cues)
    elif name == "y7_vote":   # 31,97–37,07: A teď kam dál? Hamburk, Kodaň, nebo rovnou Paříž? Napiš to do komentářů.
        await pg.evaluate(film7.map7(N))
        await pg.evaluate("()=>{S.vote={at:'berlin',deadline:'',options:[{to:'hamburk',votes:0},{to:'kodan',votes:0},{to:'pariz',votes:0}]};renderMap()}")
        await pg.evaluate(ov('<div class="eb">Výhybka v Berlíně</div><div class="ttl">Kam<br><y>dál?</y></div>'))
        await pg.evaluate("h=>{document.getElementById('xtra').innerHTML=h}", '<div class="opt" id="op"><div id="o0">Hamburk</div><div id="o1">Kodaň</div><div id="o2">Paříž</div></div>'
                          '<div style="position:absolute;left:0;right:0;top:1520px;text-align:center"><div class="stampG" id="st" style="background:#3f8a5c;box-shadow:0 10px 0 #2b6342">💬 Napiš do komentářů!</div></div>')
        js = ease + "const A=[1.09,1.75,2.55];for(let i=0;i<3;i++){const k=t-A[i];const e=document.getElementById('o'+i);e.style.opacity=k<0?0:1;e.style.transform=`scale(${k<0?.4:(k<.3?B(k/.3):1)})`}const s=t-3.78;document.getElementById('st').style.transform=`rotate(-4deg) scale(${s<0?0:(s<.35?B(s/.35):1)})`"
        await pg.evaluate(fx(js))
        cues = {T(2.55): ov('<div class="eb">Výhybka v Berlíně</div><div class="ttl">Nebo rovnou<br><y>Paříž?</y></div>')}
        await film.record(pg, name, 5.2, cues=cues)
    elif name == "y8_outro":
        os.environ["OUTRO_AT"] = "0.1,1.66,2.87"
        os.environ["OUTRO_LEN"] = "5.8"
        await film5.shot(pg, "v7_outro")

ALL = ["y1_hook", "y2_got", "y3_comments", "y4_mona", "y5_terra", "y6_berlin", "y7_vote", "y8_outro"]

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
