# Díl 5: „Vlak nám na chvíli zastavil!“ výpadek, návrat do vagónu, Kolín, hlasování jen s jízdenkou, stálý závěr.
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film, film2, film3, film4
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ov, T, steps, fx, ease = film2.ov, film3.T, film3.steps, film4.fx, film4.ease
PHONE = os.environ.get("PHONE_PNG", "/tmp/claude-0/ep5/phone.png")
ME = {"nick": "tvuj.nick", "wagon": 3, "status": "pending", "public": True,
      "avatar": {"coat": "#2f6f9f", "hat": "koruna", "pet": "pes", "item": "nic", "hair": "#6b3f22", "skin": "#f1c9a5"}}

EXTRA = r"""
.svgi{display:inline-block;vertical-align:middle}
.phone{position:absolute;left:50%;top:560px;width:560px;height:1212px;margin-left:-280px;border-radius:70px;background:#111;padding:18px;box-shadow:0 40px 90px rgba(0,0,0,.45)}
.phone .scr{position:relative;width:100%;height:100%;border-radius:54px;overflow:hidden;background:#000 url(/__phone.png) center/cover}
.phone .notch{position:absolute;left:50%;top:14px;width:150px;height:36px;margin-left:-75px;background:#111;border-radius:20px;z-index:3}
.ptoast{position:absolute;left:24px;right:24px;top:150px;background:#3f8a5c;color:#fff;border-radius:18px;padding:18px 20px;font:700 30px/1.25 IS,sans-serif;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,.3);transform:scale(0)}
.glow{position:absolute;left:30px;right:30px;top:520px;height:560px;border-radius:30px;box-shadow:0 0 0 0 rgba(255,210,63,0);}
.cmts{position:absolute;left:70px;right:70px;top:640px;background:#fff;border-radius:40px;padding:34px 36px;box-shadow:0 30px 70px rgba(0,0,0,.3);font-family:IS,sans-serif}
.cm{display:flex;gap:18px;align-items:center;padding:16px 0;border-bottom:2px solid #f0ece4;opacity:0;transform:translateY(30px)}
.cm:last-child{border-bottom:0}
.cm .av{flex:none;width:76px;height:76px;border-radius:50%}
.cm .t{flex:1;font:500 38px/1.2 IS,sans-serif;color:#1e2a33}
.cm .t b{font-weight:800;margin-right:10px}
.cm .tag{flex:none;font:800 28px/1 IS,sans-serif;padding:12px 16px;border-radius:14px}
.cm .ok{background:#e3f3e7;color:#2b6342}
.cm .no{background:#f6e3e0;color:#a33a2a}
.cm.dead .t{color:#a9a39a;text-decoration:line-through}
.rule{position:absolute;left:70px;right:70px;top:1330px;background:#ffd23f;color:#1e2a33;border-radius:28px;padding:26px 30px;text-align:center;font:900 64px/1.05 BS,sans-serif;text-transform:uppercase;box-shadow:0 12px 0 #c9a12a;transform:scale(0) rotate(-2deg)}
.steps3{position:absolute;left:70px;right:70px;top:1040px;display:grid;gap:22px}
.st3{display:flex;gap:26px;align-items:center;background:#fffaf0;border:6px solid #f0a03a;border-radius:34px;padding:22px 30px;box-shadow:0 20px 50px rgba(0,0,0,.25);opacity:0;transform:translateX(-120px)}
.st3 i{flex:none;width:96px;height:96px;border-radius:50%;background:#f0a03a;color:#fff;font:900 66px/96px BS,sans-serif;text-align:center;font-style:normal}
.st3 span{font:800 50px/1.1 IS,sans-serif;color:#1e2a33}
.st3 span b{color:#c4453a}
.smoke{position:absolute;border-radius:50%;background:rgba(80,80,80,.55)}
"""

WARN = '<svg class="svgi" width="210" height="190" viewBox="0 0 100 90"><path d="M50 4 L96 86 H4 Z" fill="#ffd23f" stroke="#1e2a33" stroke-width="6" stroke-linejoin="round"/><rect x="45" y="30" width="10" height="32" rx="4" fill="#1e2a33"/><circle cx="50" cy="73" r="6" fill="#1e2a33"/></svg>'
CHECK = '<svg class="svgi" width="200" height="200" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="#3f8a5c" stroke="#fff" stroke-width="6"/><path d="M28 52 L44 67 L73 36" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></svg>'

async def mk(b):
    ctx, pg = await film4.mk(b)
    await pg.add_style_tag(content=EXTRA)
    data = open(PHONE, "rb").read() if os.path.exists(PHONE) else b""
    await pg.route("**/__phone.png", lambda r: r.fulfill(body=data, content_type="image/png"))
    return ctx, pg

N = 160

async def train(pg, me=None, drv=False):
    await pg.evaluate("()=>{const f=document.getElementById('full');f.style.display='none';f.innerHTML=''}")
    await pg.evaluate(film2.TRAIN % (N, film3.roster(N), json.dumps(me) if me else "null"))
    await pg.evaluate("()=>{S.peak=%d;S.kmPerPassenger=1}" % N)
    await pg.evaluate(film3.DRV if drv else film3.NODRV)

async def setfull(pg, html, z=90):
    await pg.evaluate("([h,z])=>{const f=document.getElementById('full');f.style.display='block';f.style.zIndex=String(z);f.innerHTML=h}", [html, z])

async def shot(pg, name):
    if name == "v1_brake":   # 0–3,23: Ty vole… vlak nám na chvíli zastavil!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(8,.45)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="ttl huge">Ty vole…</div>'))
        await setfull(pg, ('<div id="red" style="position:absolute;inset:0;background:radial-gradient(circle,rgba(207,70,48,0) 40%,rgba(207,70,48,.55));opacity:0"></div><div id="wn" style="position:absolute;left:0;right:0;top:820px;text-align:center;transform:scale(0)">' + WARN + '<div style="margin-top:10px;font:900 150px/1 BS,sans-serif;color:#fff;text-transform:uppercase;text-shadow:0 8px 0 #8f2b1c">Výpadek!</div></div>'))
        cues = {0: "()=>{Game.flyTo(14,.45)}",
                T(1.1): fx(ease + "const c=document.querySelector('canvas');const k=Math.exp(-t*2.2);c.style.transform=`translate(${Math.sin(t*61)*26*k}px,${Math.cos(t*47)*18*k}px)`;document.getElementById('red').style.opacity=Math.min(1,t/.2)*(.75+.25*Math.sin(t*12));const w=document.getElementById('wn');w.style.transform=`scale(${t<.35?B(t/.35):1+.04*Math.sin(t*10)})`"),
                T(1.15): ov('<div class="eb">Pozor</div><div class="ttl">Vlak nám<br><y>zastavil!</y></div>')}
        await film.record(pg, name, 3.5, cues=cues)
    elif name == "v2_server":   # 3,23–5,72: přišlo vás tolik, že nám to shodilo web
        await pg.evaluate(ov('<div class="eb">Po posledním videu</div><div class="ttl">Přišlo vás<br><y>tolik…</y></div>'))
        rack = ''.join(f'<div style="height:110px;margin:16px;border-radius:14px;background:#2b2f3a;display:flex;align-items:center;gap:16px;padding:0 26px"><i class="led" style="width:26px;height:26px;border-radius:50%;background:#7cc26b"></i><i class="led" style="width:26px;height:26px;border-radius:50%;background:#7cc26b"></i><span style="flex:1;height:14px;border-radius:7px;background:#3b4150"></span></div>' for _ in range(4))
        await setfull(pg, ('<div style="position:absolute;inset:0;background:linear-gradient(#2a3442,#1b222c)"></div><div style="position:absolute;left:0;right:0;top:600px;text-align:center"><div style="font:600 36px PM,monospace;letter-spacing:.16em;color:#9fb0c4;text-transform:uppercase">zhlédnutí</div><div id="vw" style="font:900 230px/1 BS,sans-serif;color:#fff">0</div></div><div id="rk" style="position:absolute;left:290px;right:290px;top:1010px;background:#141920;border-radius:24px;padding:6px 0;border:4px solid #3b4150">' + rack + '</div><div id="sm"></div>'))
        await pg.evaluate(fx(ease + """const n=Math.round(E(t/1.3)*5000);document.getElementById('vw').textContent=(n>=5000?'5 000+':n.toLocaleString('cs-CZ'));
          const bad=t>1.2;document.querySelectorAll('.led').forEach((l,i)=>{l.style.background=bad?((Math.floor(t*8)+i)%2?'#cf4630':'#5a1a12'):'#7cc26b'});
          document.getElementById('rk').style.transform=bad?`translate(${Math.sin(t*70)*6}px,0)`:'';
          const sm=document.getElementById('sm');if(bad){let h='';for(let i=0;i<9;i++){const p=((t-1.2)*0.9+i/9)%1;h+=`<div class="smoke" style="left:${470+Math.sin(i*2.1+t)*90}px;top:${1000-p*560}px;width:${90+p*160}px;height:${90+p*160}px;opacity:${(1-p)*.8}"></div>`}sm.innerHTML=h}"""))
        cues = {T(1.25): ov('<div class="eb">Po posledním videu</div><div class="ttl">…že spadl<br><y>web!</y></div>')}
        await film.record(pg, name, 2.8, cues=cues)
    elif name == "v3_go":   # 5,72–7,11: ale už jedeme dál!
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(10,.5)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Opraveno</div><div class="ttl">Už jedeme<br><y>dál!</y></div>'))
        await setfull(pg, ('<div id="ck" style="position:absolute;left:0;right:0;top:900px;text-align:center;transform:scale(0)">' + CHECK + '</div>'))
        cues = {0: fx(ease + "document.getElementById('ck').style.transform=`scale(${t<.35?B(t/.35):1})`") , 1: "()=>{Game.flyTo(40,.5)}"}
        await film.record(pg, name, 1.7, cues=cues)
    elif name == "v4_phone":   # 7,11–11,9: jestli ti zmizel vagón, otevři web na mobilu… vrátí se ti sám
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(30,1)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Zmizel ti vagón?</div><div class="ttl">Otevři web<br><y>na mobilu</y></div>'))
        await setfull(pg, ('<div style="position:absolute;inset:0;background:rgba(20,35,45,.35)"></div><div class="phone" id="ph" style="transform:translateY(1500px)"><div class="scr"><div class="notch"></div><div class="ptoast" id="pt">Vítej zpátky, @tvuj.nick! Tvůj vagón № 3 je zase ve vlaku.</div></div></div>'))
        cues = {0: fx(ease + "const u=E((t-.0)/.6);document.getElementById('ph').style.transform=`translateY(${(1-u)*1500}px) rotate(${(1-u)*8}deg)`;const k=t-3.49;document.getElementById('pt').style.transform=`scale(${k<0?0:(k<.35?B(k/.35):1)})`"),
                T(1.35): ov('<div class="eb">Zmizel ti vagón?</div><div class="ttl">Otevři web<br><y>na mobilu</y></div><div class="chip">tam, kde sis ho <b>vyzvedl</b></div>'),
                T(3.49): ov('<div class="eb">Hotovo</div><div class="ttl">Vagón se<br><y>vrátí sám!</y></div>')}
        await film.record(pg, name, 5.0, cues=cues)
    elif name == "v5_kolin":   # 11,9–15,0: je nás přes 150 a vlak stojí v Kolíně
        await train(pg, drv=True)
        await pg.evaluate("()=>{Game.flyTo(90,.6)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Vlak followerů</div><div class="ttl huge">Je nás<br><y>150+</y></div>'))
        await pg.evaluate("()=>{const s=document.createElement('div');s.className='sign';s.id='sign';s.textContent='Kolín';s.style.transform='translateX(-50%) translateY(-2200px)';document.body.appendChild(s)}")
        cues = {0: "()=>{Game.flyTo(0,.42)}",
                T(1.4): fx(ease + "const u=E(t/.45);document.getElementById('sign').style.transform=`translateX(-50%) translateY(${(1-u)*-2200+Math.sin(Math.max(0,t-.45)*14)*Math.exp(-Math.max(0,t-.45)*5)*30}px)`"),
                T(1.5): ov('<div class="eb">Stanice</div><div class="ttl huge">Stojíme v<br><y>Kolíně!</y></div>')}
        await film.record(pg, name, 3.4, cues=cues)
    elif name == "v6a_vote":   # 15,0–17,74: kudy dál? Pardubice, nebo Havlíčkův Brod?
        await pg.evaluate(film4.MAP4.replace('__N__', str(N)).replace('__P__', str(N)))
        await pg.evaluate("()=>{const k=__P('kolin'),p=__P('pardubice'),h=__P('hbrod');const xs=[k[0],p[0],h[0]],ys=[k[1],p[1],h[1]];__vb((Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2+8,Math.max((Math.max(...xs)-Math.min(...xs))*1.9,(Math.max(...ys)-Math.min(...ys))*1.9*988/588))}")
        await pg.evaluate(ov('<div class="eb">Hlasování</div><div class="ttl">Kudy<br><y>dál?</y></div><div style="height:690px"></div><div class="opts two"><div id="o0">Pardubice</div><div id="o1">Havl. Brod</div></div>'))
        on = lambda i: "()=>{document.querySelectorAll('#ov .opts div').forEach(d=>d.classList.remove('on'));" + (f"document.getElementById('o{i}').classList.add('on')" if i >= 0 else "") + "}"
        cues = {T(.73): on(0), T(1.6): on(1), T(2.5): on(-1)}
        await film.record(pg, name, 3.0, cues=cues)
    elif name == "v6b_rule":   # 17,74–21,64: piš do komentářů… ale počítají se jen hlasy lidí s jízdenkou
        await train(pg)
        await pg.evaluate("()=>{Game.flyTo(20,.8)}"); await steps(pg, 150)
        await pg.evaluate(ov('<div class="eb">Hlasování</div><div class="ttl">Piš do<br><y>komentářů</y></div>'))
        cm = [("#e07a9b", "jana.n", "Pardubice!!", True), ("#2f6f9f", "petr_k", "Brod, jasně", True),
              ("#a8a29a", "nekdo_bez", "Pardubice", False), ("#3f8a5c", "eva.v", "pardubice 🚂", True)]
        rows = ''.join(f'<div class="cm{"" if ok else " dead"}" id="c{i}"><div class="av" style="background:{c}"></div><div class="t"><b>{n}</b>{txt}</div><div class="tag {"ok" if ok else "no"}">{"🎫 platí" if ok else "bez jízdenky"}</div></div>' for i, (c, n, txt, ok) in enumerate(cm))
        await setfull(pg, (f'<div style="position:absolute;inset:0;background:rgba(20,35,45,.4)"></div><div class="cmts">{rows}</div><div class="rule" id="rl">Počítají se jen hlasy s jízdenkou</div>'))
        await pg.evaluate(fx(ease + "for(let i=0;i<4;i++){const u=E((t-.15-i*.22)/.35);const e=document.getElementById('c'+i);e.style.opacity=u;e.style.transform=`translateY(${(1-u)*30}px)`}const k=t-1.2;document.getElementById('rl').style.transform=`scale(${k<0?0:(k<.35?B(k/.35):1)}) rotate(-2deg)`"))
        cues = {T(1.2): ov('<div class="eb">Pozor</div><div class="ttl">Hlasuj<br><y>s jízdenkou</y></div>')}
        await film.record(pg, name, 4.2, cues=cues)
    elif name == "v7_outro":   # stálý závěr: dej follow a nastup do svého vagónu přes odkaz v biu
        await train(pg, me=ME)
        await pg.evaluate("()=>{Game.flyTo(3,0)}"); await steps(pg, 220)
        await pg.evaluate(ov('<div class="eb">@vlak.followeru</div><div class="ttl">Nastup do<br><y>vlaku!</y></div>'))
        st = [("1", "Dej <b>follow</b>"), ("2", "Klikni na <b>odkaz v biu</b>"), ("3", "Nastup do <b>svého vagónu</b>")]
        await setfull(pg, ('<div class="steps3">' + ''.join(f'<div class="st3" id="s{i}"><i>{n}</i><span>{t}</span></div>' for i, (n, t) in enumerate(st)) + '</div>'))
        at = os.environ.get("OUTRO_AT", "0.25,1.05,2.0").split(",")
        await pg.evaluate(fx(ease + "const A=[" + ",".join(at) + "];for(let i=0;i<3;i++){const u=E((t-A[i])/.35);const e=document.getElementById('s'+i);e.style.opacity=u;e.style.transform=`translateX(${(1-u)*-120}px) scale(${1+.06*Math.max(0,1-Math.abs(t-A[i]-.35)*4)})`}"))
        await film.record(pg, name, float(os.environ.get("OUTRO_LEN", "4.9")))

ALL = ["v1_brake", "v2_server", "v3_go", "v4_phone", "v5_kolin", "v6a_vote", "v6b_rule", "v7_outro"]

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
