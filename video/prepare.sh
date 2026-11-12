#!/usr/bin/env bash
# Připraví kopii webu pro natáčení a spustí ji na http://localhost:3457/
#  - zpřístupní 3D objekty jako window.__G (záběry s panáčkem je potřebují)
#  - na obrázku do Stories napíše skutečnou adresu místo localhostu
#  - úložiště je čisté: stav jako v produkci, žádné jízdenky skutečných lidí
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="$HERE/_site"; STORE="$HERE/_store"
rm -rf "$SITE" "$STORE"; mkdir -p "$SITE" "$STORE"
cp -r "$HERE/../index.html" "$HERE/../api" "$HERE/../lib" "$HERE/../qrcode.js" "$HERE/../og.jpg" "$HERE/../data.json" "$HERE/../package.json" "$SITE/"
python3 - "$SITE/index.html" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
a = "  return{ok:true,"
assert a in s, "nenašel jsem konec Game()"
s = s.replace(a, "  window.__G={avatarSlot,petSlot,interior,camera,scene,slots,loco,driverSlot,extrasSlot,lmFar,lmNear,stationSign};\n" + a, 1)
s = s.replace("g.fillText(location.host,540,1575,1000)", 'g.fillText("vlak-followeru.vercel.app",540,1575,1000)')
open(p, "w").write(s)
PY
cp "$HERE/dev/state.json" "$STORE/state.json"
cd "$SITE"
LOCAL_STORE_DIR="$STORE" exec node "$HERE/dev/server.mjs" "$SITE" 3457
