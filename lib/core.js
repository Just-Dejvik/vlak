// Logika jízdenek a denní kontroly. Čisté funkce, bez sítě, aby šly snadno testovat.
import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import SEED from './seed.js';

export const DAY = 24 * 60 * 60 * 1000;
export const PENDING_DAYS = 4;
export const CLAIMS_PER_IP_PER_DAY = 3;

export const AV = {
  coats: ['#c4453a', '#2f6f9f', '#3f8a5c', '#d9a13b', '#7a4fa3', '#2b2f3a', '#e07a9b', '#e8e0cc'],
  hats: ['zadna', 'cepice', 'klobouk', 'ksilt', 'koruna'],
  pets: ['zadny', 'kocka', 'pes'],
  items: ['nic', 'kniha', 'hrnek', 'kytara'],
  hair: ['#2a1c14', '#6b3f22', '#c9a35a', '#a8a29a', '#b2462c'],
  skin: ['#f1c9a5', '#d9a27a', '#9c6b48', '#6e4a33'],
};

export class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

export const sha256 = (s) => createHash('sha256').update(String(s)).digest('hex');
export const newToken = () => randomBytes(24).toString('base64url');

export function safeEqual(a, b) {
  const x = Buffer.from(String(a ?? ''));
  const y = Buffer.from(String(b ?? ''));
  return x.length === y.length && timingSafeEqual(x, y);
}

export function cleanNick(v) {
  const nick = String(v ?? '').trim().replace(/^@+/, '').toLowerCase();
  if (!nick) throw new HttpError(400, 'Napiš svůj instagramový nick.');
  if (!/^[a-z0-9._]{1,30}$/.test(nick) || nick.startsWith('.') || nick.endsWith('.')) {
    throw new HttpError(400, 'Nick může mít jen písmena bez diakritiky, číslice, tečky a podtržítka (max. 30 znaků).');
  }
  return nick;
}

/** Ponechá jen povolené hodnoty vzhledu panáčka. */
export function cleanAvatar(a, fallback = {}) {
  const src = a && typeof a === 'object' ? a : {};
  const pick = (key, list, def) => (list.includes(src[key]) ? src[key] : (list.includes(fallback[key]) ? fallback[key] : def));
  return {
    coat: pick('coat', AV.coats, AV.coats[0]),
    hat: pick('hat', AV.hats, 'zadna'),
    pet: pick('pet', AV.pets, 'zadny'),
    item: pick('item', AV.items, 'nic'),
    hair: pick('hair', AV.hair, AV.hair[0]),
    skin: pick('skin', AV.skin, AV.skin[0]),
  };
}

export const emptyDb = () => ({ tickets: {}, rate: {} });
export const seedState = () => JSON.parse(JSON.stringify(SEED));

/** Co o jízdence smí vidět její majitel. */
export function ticketView(t) {
  return {
    nick: t.nick, wagon: t.wagon ?? null, lastWagon: t.lastWagon ?? null, status: t.status,
    public: !!t.public, avatar: t.avatar, createdAt: t.createdAt,
    verifiedAt: t.verifiedAt ?? null, leftAt: t.leftAt ?? null,
    expiresAt: t.status === 'pending' ? t.createdAt + PENDING_DAYS * DAY : null,
  };
}

/** Veřejný seznam: cestující ve vlaku (ověření i čekající), kteří souhlasili se zveřejněním nicku. */
export function roster(db) {
  return Object.values(db.tickets)
    .filter((t) => (t.status === 'verified' || t.status === 'pending') && t.public && t.wagon)
    .sort((a, b) => a.wagon - b.wagon)
    .map((t) => [t.wagon, t.nick, t.avatar]);
}

export function counts(db) {
  const c = { pending: 0, verified: 0, left: 0 };
  for (const t of Object.values(db.tickets)) c[t.status] = (c[t.status] || 0) + 1;
  return c;
}

/** Nejnižší volný vagón. Vagóny lidí, kteří vystoupili, se drží pro jejich návrat. */
export function assignWagon(db, preferred) {
  const held = new Set();
  const reserved = new Set();
  for (const t of Object.values(db.tickets)) {
    if ((t.status === 'pending' || t.status === 'verified') && t.wagon) held.add(t.wagon);
    if (t.status === 'left' && t.lastWagon) reserved.add(t.lastWagon);
  }
  if (preferred && !held.has(preferred)) return preferred;
  for (let n = 1; ; n++) if (!held.has(n) && !reserved.has(n)) return n;
}

export function authTicket(db, nickRaw, token) {
  const nick = cleanNick(nickRaw);
  const t = db.tickets[nick];
  if (!t) throw new HttpError(404, 'Jízdenka už neexistuje.');
  if (!token || !safeEqual(sha256(token), t.tokenHash)) throw new HttpError(403, 'K téhle jízdence nemáš přístup.');
  return t;
}

export function claim(db, { nick: nickRaw, public: pub, avatar }, ipHash, now = Date.now()) {
  const nick = cleanNick(nickRaw);
  const prev = db.tickets[nick];
  if (prev && (prev.status === 'pending' || prev.status === 'verified')) {
    throw new HttpError(409, 'Tenhle nick už jízdenku má. Pokud je tvůj, napiš nám zprávu na Instagram.');
  }
  // omezení zneužití: pár jízdenek z jednoho připojení za den
  for (const k of Object.keys(db.rate)) {
    db.rate[k] = db.rate[k].filter((ts) => now - ts < DAY);
    if (!db.rate[k].length) delete db.rate[k];
  }
  const recent = db.rate[ipHash] || [];
  if (recent.length >= CLAIMS_PER_IP_PER_DAY) {
    throw new HttpError(429, 'Z tohohle připojení už dnes bylo vyzvednuto dost jízdenek. Zkus to zítra.');
  }
  db.rate[ipHash] = [...recent, now];

  const token = newToken();
  const wagon = assignWagon(db, prev && prev.lastWagon);
  db.tickets[nick] = {
    nick, wagon, status: 'pending', public: !!pub,
    avatar: cleanAvatar(avatar, prev && prev.avatar),
    tokenHash: sha256(token), createdAt: now, lastWagon: null,
  };
  return { ticket: ticketView(db.tickets[nick]), token };
}

/** Ze všeho, co Instagram v exportu může poslat, vytáhne mapu nick → čas followu. */
export function normalizeFollowers(list) {
  const map = new Map();
  if (!Array.isArray(list)) throw new HttpError(400, 'Seznam followerů chybí.');
  for (const item of list) {
    const [n, ts] = Array.isArray(item) ? item : [item && item.nick, item && item.ts];
    try { map.set(cleanNick(n), Number(ts) || 0); } catch { /* neplatný řádek přeskočíme */ }
  }
  return map;
}

/**
 * Denní kontrola. followers: Map nick → čas followu (s).
 * - čekající, kteří sledují → ověření
 * - ověření, kteří už nesledují → vystoupili (vagón se jim drží)
 * - vystoupivší, kteří znovu sledují → vrátí se, do svého vagónu, pokud je volný
 * - čekající déle než 4 dny bez followu → jízdenka propadne
 */
export function verify(db, followers, now = Date.now()) {
  const report = { verified: [], left: [], returned: [], expired: [], pending: [] };
  const tickets = Object.values(db.tickets);
  for (const t of tickets) {
    const follows = followers.has(t.nick);
    if (t.status === 'verified' && !follows) {
      t.status = 'left'; t.lastWagon = t.wagon; t.wagon = null; t.leftAt = now;
      report.left.push(t.nick);
    }
  }
  for (const t of tickets) {
    const follows = followers.has(t.nick);
    if (t.status === 'pending') {
      if (follows) {
        t.status = 'verified'; t.verifiedAt = now; t.followedAt = followers.get(t.nick) || null;
        report.verified.push(t.nick);
      } else if (now - t.createdAt > PENDING_DAYS * DAY) {
        delete db.tickets[t.nick];
        report.expired.push(t.nick);
      } else {
        report.pending.push(t.nick);
      }
    }
  }
  for (const t of tickets) {
    if (t.status === 'left' && followers.has(t.nick) && db.tickets[t.nick]) {
      const preferred = t.lastWagon;
      t.lastWagon = null;
      t.wagon = assignWagon(db, preferred);
      t.status = 'verified'; t.verifiedAt = now; t.leftAt = null;
      report.returned.push(t.nick);
    }
  }
  return report;
}

/** Stav světa, jak ho uloží správa. Jízdenky do něj nepatří. */
export function cleanState(s) {
  if (!s || typeof s !== 'object' || !s.nodes || !Array.isArray(s.route) || typeof s.followers !== 'number') {
    throw new HttpError(400, 'Tohle nejsou platná data vlaku.');
  }
  const out = { ...s };
  delete out.tickets;
  out.followers = Math.max(0, Math.floor(out.followers));
  return out;
}
