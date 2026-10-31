# Vlak bez konečné

Statický web (jedna stránka, žádný build). Každý follower = jeden vagón dlouhý 25 m.
Vlak leží na trati od Prahy až po lokomotivu, na výhybkách rozhoduje komunita.

## Soubory
- `index.html` – celý web včetně správy (`/#sprava`)
- `data.json` – stav vlaku: počet cestujících, trasa, hlasování, kronika, speciální vagóny

## Jak aktualizovat vlak (bez databáze)
1. Otevři `/#sprava`, uprav počet cestujících, hlasy, kroniku…
2. Dole klikni na **Zkopírovat data**.
3. Na GitHubu otevři `data.json` → Edit → vlož → Commit.
4. Vercel web do minuty znovu nasadí a změny uvidí všichni.

## Nasazení na Vercel
1. Nahraj obsah této složky do nového repozitáře na GitHubu.
2. Na vercel.com → Add New → Project → vyber repozitář → Deploy (žádné nastavení není potřeba).

## Co zatím chybí do ostré verze
- Jízdenky se ukládají jen v prohlížeči návštěvníka → potřebují databázi (např. Vercel Postgres / Neon).
- Správa nemá heslo → před zveřejněním ji schováme za přihlášení.
- Kontrola jízdenek proti exportu sledujících z Instagramu (1× denně).
