// Propojení s Instagramem (Instagram API with Instagram Login): jen vlastní účet projektu.
// Umí: počet followerů, poslední příspěvky a jejich komentáře. Seznam followerů API nedává.
// Přístupový klíč leží v soukromém úložišti (ig.json) a nikdy se neposílá do prohlížeče.
import { mutateJSON, readJSON } from './store.js';
import { HttpError } from './core.js';

const API = 'https://graph.instagram.com';
const V = 'v21.0';
const FILE = 'ig.json';
const DAY = 24 * 60 * 60 * 1000;

async function call(path, params, token) {
  const u = new URL(path.startsWith('http') ? path : `${API}/${path}`);
  for (const [k, v] of Object.entries(params || {})) u.searchParams.set(k, v);
  if (token) u.searchParams.set('access_token', token);
  const r = await fetch(u, { headers: { accept: 'application/json' } });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) {
    const msg = (j.error && j.error.message) || `Instagram odpověděl ${r.status}.`;
    const expired = j.error && (j.error.code === 190 || /expired|session/i.test(msg));
    throw new HttpError(expired ? 401 : 502, expired ? 'Klíč k Instagramu vypršel nebo byl zrušen. Vygeneruj nový a vlož ho znovu.' : `Instagram: ${msg}`);
  }
  return j;
}

const me = (token) => call(`${V}/me`, { fields: 'user_id,username,followers_count,media_count' }, token);

/** Uloží nový klíč po ověření, že funguje. */
export async function setToken(token) {
  const t = String(token || '').trim();
  if (t.length < 20) throw new HttpError(400, 'Tohle nevypadá jako přístupový klíč.');
  const info = await me(t);
  const now = Date.now();
  await mutateJSON(FILE, () => ({}), (cur) => {
    Object.assign(cur, { token: t, savedAt: now, refreshedAt: now, expiresAt: now + 60 * DAY, username: info.username });
    return { ok: true };
  });
  return { username: info.username, followers: info.followers_count };
}

export async function clearToken() {
  await mutateJSON(FILE, () => ({}), (cur) => { for (const k of Object.keys(cur)) delete cur[k]; return { ok: true }; });
}

/** Vrátí platný klíč; dlouhodobý klíč jednou za pár dní sám prodlouží o dalších 60 dní. */
async function token() {
  const f = await readJSON(FILE, { fresh: true });
  const d = f && f.data;
  if (!d || !d.token) throw new HttpError(409, 'Instagram zatím není propojený.');
  if (Date.now() - (d.refreshedAt || 0) > 3 * DAY) {
    try {
      const r = await call('refresh_access_token', { grant_type: 'ig_refresh_token' }, d.token);
      const now = Date.now();
      await mutateJSON(FILE, () => ({}), (cur) => {
        Object.assign(cur, { token: r.access_token, refreshedAt: now, expiresAt: now + (Number(r.expires_in) || 60 * 86400) * 1000 });
        return { ok: true };
      });
      return r.access_token;
    } catch (e) {
      if (e.status === 401) throw e; // vypršel úplně
      // krátkodobý problém s prodloužením: zkusíme to příště, starý klíč ještě platí
    }
  }
  return d.token;
}

export async function status() {
  const f = await readJSON(FILE, { fresh: true });
  const d = f && f.data;
  if (!d || !d.token) return { connected: false };
  try {
    const info = await me(await token());
    const g = (await readJSON(FILE, { fresh: true })).data;
    return { connected: true, username: info.username, followers: info.followers_count, media: info.media_count, expiresAt: g.expiresAt };
  } catch (e) {
    return { connected: false, error: e.message, username: d.username };
  }
}

export async function recentMedia() {
  const t = await token();
  const j = await call(`${V}/me/media`, { fields: 'id,caption,media_type,media_product_type,permalink,timestamp,comments_count,thumbnail_url,media_url', limit: '12' }, t);
  return (j.data || []).map((m) => ({
    id: m.id, permalink: m.permalink, timestamp: m.timestamp, comments: m.comments_count || 0,
    caption: String(m.caption || '').slice(0, 90), thumb: m.thumbnail_url || (m.media_type === 'IMAGE' ? m.media_url : null),
  }));
}

/** Všechny komentáře pod příspěvkem (i odpovědi), max. pár tisíc. */
export async function allComments(mediaId) {
  if (!/^\d{5,30}$/.test(String(mediaId))) throw new HttpError(400, 'Neplatné video.');
  const t = await token();
  const out = [];
  let next = null;
  let j = await call(`${V}/${mediaId}/comments`, { fields: 'id,text,username,timestamp,replies{id,text,username,timestamp}', limit: '50' }, t);
  for (let page = 0; page < 80; page++) {
    for (const c of j.data || []) {
      out.push({ username: c.username, text: c.text, ts: c.timestamp });
      for (const r of (c.replies && c.replies.data) || []) out.push({ username: r.username, text: r.text, ts: r.timestamp });
    }
    next = j.paging && j.paging.next;
    if (!next) break;
    j = await call(next, null, null);
  }
  return out;
}

// --- počítání hlasů (čistá logika, testovatelná bez sítě) ---

export const fold = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

/** Slova, podle kterých poznáme volbu: celé jméno, delší slova a zkratka (Hradec Králové → hk). */
export function aliases(name) {
  const f = fold(name).replace(/[^a-z0-9 ]+/g, ' ').trim();
  const words = f.split(/\s+/).filter(Boolean);
  const a = new Set([f]);
  for (const w of words) if (w.length >= 4) a.add(w);
  if (words.length >= 2) a.add(words.map((w) => w[0]).join(''));
  return [...a];
}

/**
 * Sečte hlasy. Jeden člověk = jeden hlas (platí jeho poslední komentář s jasnou volbou).
 * Komentář, který zmíní víc voleb, se nepočítá. passengers: Set nicků s platnou jízdenkou.
 */
export function countVotes(comments, options, passengers, self) {
  const al = options.map((o) => ({ to: o.to, re: aliases(o.name).map((w) => new RegExp(`(^|[^a-z0-9])${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^a-z0-9])`)) }));
  const last = new Map();
  let ambiguous = 0;
  const sorted = [...comments].sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
  for (const c of sorted) {
    const u = String(c.username || '').toLowerCase();
    if (!u || u === self) continue;
    const t = fold(c.text);
    const hit = al.filter((o) => o.re.some((r) => r.test(t))).map((o) => o.to);
    if (hit.length === 1) last.set(u, hit[0]);
    else if (hit.length > 1) ambiguous++;
  }
  const all = Object.fromEntries(options.map((o) => [o.to, 0]));
  const riders = Object.fromEntries(options.map((o) => [o.to, 0]));
  const voters = [];
  for (const [u, to] of last) {
    all[to]++;
    const p = passengers.has(u);
    if (p) riders[to]++;
    voters.push({ nick: u, to, passenger: p });
  }
  return {
    all, riders, voters: voters.sort((a, b) => b.passenger - a.passenger || a.nick.localeCompare(b.nick)),
    comments: comments.length, people: new Set(comments.map((c) => String(c.username || '').toLowerCase())).size, ambiguous,
  };
}
