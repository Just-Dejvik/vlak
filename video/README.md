# Natáčení videí (Reels)

Skripty, kterými vznikly Reel 1 a Reel 2. Na web nemají vliv – složka `video/` se na Vercel nenahrává (`.vercelignore`).

Potřeba: Python 3 + `playwright` (Chromium), `ffmpeg`, `Pillow`, Node 18+.

## Postup

1. **Spustit web pro natáčení** (kopie webu v `_site/`, čisté úložiště v `_store/`, stav jako v produkci, žádné skutečné jízdenky):
   ```
   ./prepare.sh          # běží na http://localhost:3457/
   ```
2. **Natočit záběry** (každý záběr = `clips/<jméno>.mp4`, trvá to ~30 min):
   ```
   python3 film.py            # díl 1 (s1…s6)
   python3 film2.py           # díl 2 (h1_hook … h5b_cta)
   python3 film2.py h4_story  # jen jeden záběr
   PREVIEW_AT=1.0,2.5 python3 film2.py h1_hook   # rychlý náhled snímků do frames/
   ```
3. **Složit video s hlasem a titulky**:
   ```
   python3 assemble2.py voiceover.mp3 reel-2.mp4 "0,1.41,5.53,…"
   ```
   Poslední argument = začátky vět v hlasu (sekundy). Titulky a přiřazení vět k záběrům je v `PLAN` uvnitř `assemble*.py`.

## Co je co

- `film.py` – společné věci: virtuální hodiny (plynulé snímky bez sekání), styly nadpisů, `record()`, díl 1.
- `film2.py` – záběry dílu 2. Nicky ve videu jsou vymyšlené (`NICKS`, `tvuj.nick`).
- `assemble.py`, `assemble2.py` – sestavení dílu 1 / 2.
- `og.py` – náhled odkazu `../og.jpg`.
- `fonts/` – Big Shoulders Display, Instrument Sans, IBM Plex Mono (OFL), `three.min.js` (MIT, r128).
- `dev/server.mjs` – lokální napodobenina Vercelu (statika + `/api`, soubory místo Blobu). `dev/*.test.mjs` – testy API.
- `dev/state.json` – výchozí stav světa (Praha, hlasování Kolín/Plzeň/Ústí/Tábor). Pro nové video ho uprav podle aktuálního stavu.
