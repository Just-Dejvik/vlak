# Kreslený palec (bílý s černým obrysem) jako v rytmických videích „hýbej palcem do rytmu“.
# Kreslí se nahoru od zápěstí v bodě (0,0); natáčí se kolem zápěstí v pravém dolním rohu.
THUMB_PATH = ("M-470,260 C-440,40 -330,-170 -250,-420 C-205,-560 -190,-760 -175,-900 "
              "C-160,-1030 -110,-1085 -50,-1080 C20,-1072 45,-1010 38,-930 "
              "C30,-820 15,-700 30,-600 C48,-480 95,-390 175,-300 C260,-200 330,-80 420,40 L520,260 Z")
NAIL = "M-150,-940 C-146,-1010 -112,-1048 -66,-1046 C-28,-1043 -12,-1004 -16,-960 C-20,-925 -60,-912 -104,-916 C-138,-919 -152,-928 -150,-940 Z"
CREASE = "M-205,-620 C-170,-600 -120,-598 -80,-612 M-190,-575 C-160,-560 -128,-558 -100,-566"
KNUCKLE = "M-280,-250 C-240,-205 -180,-185 -120,-195"

def thumb_svg(el_id, x=1120, y=2030, scale=1.18, mirror=False):
    sx = -scale if mirror else scale
    return (f'<svg id="{el_id}" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;pointer-events:none">'
            f'<g transform="translate({x},{y}) scale({sx},{scale})"><g class="tr">'
            f'<path d="{THUMB_PATH}" fill="#fdfdfb" stroke="#151515" stroke-width="11" stroke-linejoin="round"/>'
            f'<path d="{NAIL}" fill="#f4f1ec" stroke="#151515" stroke-width="7"/>'
            f'<path d="{CREASE}" fill="none" stroke="#151515" stroke-width="6" stroke-linecap="round" opacity=".55"/>'
            f'<path d="{KNUCKLE}" fill="none" stroke="#151515" stroke-width="6" stroke-linecap="round" opacity=".45"/>'
            '</g></g></svg>')

def thumb_js(el_id, beat, t0=0.0, up=-9, down=-57, every=2):
    """Palec nahoru na silnou dobu (každou `every`-tou), dolů na další dobu. Rychlé přepnutí jako v předloze."""
    return ("{const g=document.querySelector('#%s .tr');if(g){const tt=t-%f;const ph=tt/%f;const bi=Math.floor(ph),f=ph-bi;"
            "const isUp=(((bi%%%d)+%d)%%%d)===0;const tg=isUp?%f:%f,pv=isUp?%f:%f;const u=tt<0?1:Math.min(1,f/.16);const e=u*u*(3-2*u);"
            "const a=pv+(tg-pv)*e;const sq=isUp?1+.04*Math.max(0,1-f*5):1;g.setAttribute('transform',`rotate(${a}) scale(${sq})`)}}"
            % (el_id, t0, beat, every, every, every, up, down, down, up))
