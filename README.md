# Vlak followerů

Hra pro Instagram: každý follower přidá jeden vagón (25 m). Vlak leží na trati od Prahy
až po lokomotivu, na výhybkách rozhoduje komunita. Cíl: obepnout Zemi (40 075 km).

## Jak to je postavené
- `index.html` – celá hra (3D vlak přes three.js) i správa na `/#sprava`
- `api/world.js` – veřejný stav světa a seznam ověřených cestujících
- `api/ticket.js` – vyzvednutí jízdenky, stav, úprava panáčka, smazání
- `api/admin.js` – správa (heslo v proměnné `ADMIN_PASSWORD`), denní kontrola followerů
- `lib/` – logika jízdenek a úložiště (privátní Vercel Blob, podmíněné zápisy přes ETag)
- `data.json` – ukázková data, použijí se jen když server neběží

## Denní kontrola followerů
1. Instagram → Nastavení → Centrum účtů → Vaše informace a oprávnění → Stáhnout informace
2. Jen „Sledující a sledovaní“, formát JSON, celé období
3. Ve správě nahraj `followers_1.json` a dej **Spustit kontrolu**

Kontrola ověří čekající jízdenky, odstěhuje lidi, kteří dali unfollow (vagón jim drží),
vrátí ty, kteří se vrátili, zruší jízdenky neověřené do 4 dnů a nastaví počet cestujících.

## Proměnné na Vercelu
- `BLOB_READ_WRITE_TOKEN` – nastaví Vercel po napojení Blob úložiště
- `ADMIN_PASSWORD` – heslo do správy
