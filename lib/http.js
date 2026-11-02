import { HttpError, safeEqual, sha256 } from './core.js';

export function send(res, status, body, cache = 'no-store') {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', cache);
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.end(JSON.stringify(body));
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

export function clientIpHash(req) {
  const fwd = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  const ip = fwd || req.headers['x-real-ip'] || (req.socket && req.socket.remoteAddress) || 'unknown';
  return sha256('vlak-followeru:' + ip).slice(0, 20);
}

export async function requireAdmin(req) {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) throw new HttpError(500, 'Heslo správy není na serveru nastavené.');
  const given = req.headers['x-admin-password'];
  if (!given || !safeEqual(given, expected)) {
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
