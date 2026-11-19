import { createHmac } from 'node:crypto';
import { HttpError, safeEqual } from './core.js';
import { mutateJSON, readJSON } from './store.js';

export function send(res, status, body, cache = 'no-store') {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', cache);
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.end(JSON.stringify(body));
}

// Záloha jízdenky v prohlížeči. Instagram (iOS) občas smaže místní úložiště webu
// (po pár dnech bez návštěvy), cookie nastavená serverem vydrží. Je nezbytná pro hru
// (drží jen nick a klíč k jízdence), nic nesleduje, takže nepotřebuje souhlas.
const TCOOKIE = 'vf_t';
export function setTicketCookie(res, nick, token) {
  const v = nick && token ? encodeURIComponent(nick + '~' + token) : '';
  const age = v ? 60 * 60 * 24 * 400 : 0;
  res.setHeader('Set-Cookie', `${TCOOKIE}=${v}; Path=/api/ticket; Max-Age=${age}; HttpOnly; Secure; SameSite=Lax`);
}
export function readTicketCookie(req) {
  const m = String(req.headers.cookie || '').match(/(?:^|;\s*)vf_t=([^;]*)/);
  if (!m) return null;
  let v; try { v = decodeURIComponent(m[1]); } catch { return null; }
  const i = v.lastIndexOf('~');
  if (i < 1) return null;
  return { nick: v.slice(0, i), token: v.slice(i + 1) };
}

export async function body(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return {}; } }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const text = Buffer.concat(chunks).toString('utf8');
  if (!text) return {};
  try { return JSON.parse(text); } catch { throw new HttpError(400, 'Neplatný požadavek.'); }
}

function clientIp(req) {
  const fwd = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  return fwd || req.headers['x-real-ip'] || (req.socket && req.socket.remoteAddress) || 'unknown';
}

// Otisk připojení: tajný klíč + den. IP adresa se nikde neukládá a otisk se nedá zpětně
// převést na IP ani propojit mezi dny (klíč zná jen server).
const IP_SECRET = process.env.IP_SALT || process.env.KV_REST_API_TOKEN || process.env.ADMIN_PASSWORD || 'local-dev';
export function clientIpHash(req, now = Date.now()) {
  const day = new Date(now).toISOString().slice(0, 10);
  return createHmac('sha256', IP_SECRET).update(day + '|' + clientIp(req)).digest('hex').slice(0, 20);
}

// Ochrana hesla správy proti hádání: po 8 špatných pokusech z jednoho připojení 15 minut pauza,
// a když jich za hodinu přijde odkudkoli přes 60, správa se na hodinu zamkne úplně.
const GUARD = 'adminguard.json';
const MIN = 60 * 1000;
async function guardCheck(key, now) {
  const g = (await readJSON(GUARD, { fresh: false }).catch(() => null))?.data;
  if (!g) return;
  if (g.lockUntil && now < g.lockUntil) throw new HttpError(429, 'Správa je kvůli mnoha špatným pokusům na chvíli zamčená. Zkus to za hodinu.');
  const mine = (g.ip && g.ip[key]) || [];
  if (mine.filter((t) => now - t < 15 * MIN).length >= 8) throw new HttpError(429, 'Moc špatných pokusů. Zkus to za 15 minut.');
}
async function guardFail(key, now) {
  await mutateJSON(GUARD, () => ({ ip: {}, all: [] }), (g) => {
    g.ip = g.ip || {}; g.all = (g.all || []).filter((t) => now - t < 60 * MIN);
    for (const k of Object.keys(g.ip)) { g.ip[k] = g.ip[k].filter((t) => now - t < 15 * MIN); if (!g.ip[k].length) delete g.ip[k]; }
    g.ip[key] = [...(g.ip[key] || []), now];
    g.all.push(now);
    if (g.all.length > 60) g.lockUntil = now + 60 * MIN;
    return { ok: true };
  }).catch(() => {});
}

export async function requireAdmin(req) {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) throw new HttpError(500, 'Heslo správy není na serveru nastavené.');
  const now = Date.now();
  const key = clientIpHash(req, now);
  await guardCheck(key, now);
  const given = req.headers['x-admin-password'];
  if (!given || !safeEqual(given, expected)) {
    await guardFail(key, now);
    await new Promise((r) => setTimeout(r, 700));
    throw new HttpError(401, 'Špatné heslo.');
  }
}

export function wrap(handler) {
  return async (req, res) => {
    try {
      await handler(req, res);
    } catch (e) {
      const status = e.status || 500;
      if (status >= 500) console.error(e);
      send(res, status, { error: status >= 500 && !e.status ? 'Něco se pokazilo na serveru. Zkus to prosím znovu.' : e.message });
    }
  };
}
