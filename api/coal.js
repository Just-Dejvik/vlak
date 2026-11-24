// Uhelný event: GET = stav a žebříček (krátce cachované), POST = připsat hody cestujícího.
import { readJSON } from '../lib/store.js';
import { authTicket, emptyDb, HttpError } from '../lib/core.js';
import { body, send, wrap } from '../lib/http.js';
import { coalMine, coalStats, currentEvent, isActive, markDone, publicEvent, readCoal, throwCoal } from '../lib/coal.js';

const DONE = new Set();
const CACHE = 'public, max-age=0, s-maxage=3, stale-while-revalidate=10';

async function ticketsDb(fresh) {
  const db = await readJSON('tickets.json', { fresh });
  return db ? db.data : emptyDb();
}

export default wrap(async (req, res) => {
  const now = Date.now();
  if (req.method === 'GET') {
    const doc = await readCoal(false);
    const ev = currentEvent(doc);
    if (!ev) return send(res, 200, { ev: null, now }, CACHE);
    const me = new URL(req.url, 'http://x').searchParams.get('me');
    const [st, db, mine] = await Promise.all([coalStats(ev.id, 10), ticketsDb(false), me ? coalMine(ev.id, me) : null]);
    // skryté nicky v žebříčku neukazujeme
    const top = st.top.map(([nick, n]) => { const t = db.tickets[nick]; return [t && t.public ? nick : null, n]; });
    return send(res, 200, { ev: publicEvent(ev), active: isActive(ev, now), total: st.total, players: st.players, top, now, ...(mine != null ? { mine } : {}) }, CACHE);
  }

  if (req.method !== 'POST') return send(res, 405, { error: 'Nepodporovaná metoda.' });
  const b = await body(req);
  const token = req.headers['x-ticket-token'];
  const n = Math.floor(Number(b.n));
  if (!(n >= 1 && n <= 200)) throw new HttpError(400, 'Neplatný počet.');

  const doc = await readCoal(false);
  const ev = currentEvent(doc);
  if (!isActive(ev, now) || (b.ev && b.ev !== ev.id)) throw new HttpError(409, 'Uhelný event teď neběží.');

  // jízdenky z krátké paměti; čerstvě vyzvednutou jízdenku dočteme znovu
  let t;
  try { t = authTicket(await ticketsDb(false), b.nick, token); }
  catch (e) { if (e.status !== 404 && e.status !== 403) throw e; t = authTicket(await ticketsDb(true), b.nick, token); }
  if (t.status !== 'pending' && t.status !== 'verified') throw new HttpError(403, 'Uhlí můžou házet jen cestující s platnou jízdenkou.');

  const r = await throwCoal(ev.id, t.nick, n, now);
  let done = !!ev.done || DONE.has(ev.id);
  if (!done && r.total >= ev.goal) { await markDone(ev.id, now); DONE.add(ev.id); done = true; }
  send(res, 200, { ...r, done, goal: ev.goal });
});
