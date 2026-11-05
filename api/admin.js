// Správa projektu: stav světa, jízdenky a denní kontrola followerů. Chráněno heslem.
import { mutateJSON, readJSON } from '../lib/store.js';
import {
  cleanNick, cleanState, counts, emptyDb, HttpError, newToken, normalizeFollowers, seedState, sha256, ticketView, verify,
} from '../lib/core.js';
import { body, requireAdmin, send, wrap } from '../lib/http.js';

const listTickets = (db) => Object.values(db.tickets)
  .map(ticketView)
  .sort((a, b) => (a.wagon ?? a.lastWagon ?? 1e9) - (b.wagon ?? b.lastWagon ?? 1e9));

export default wrap(async (req, res) => {
  await requireAdmin(req);

  if (req.method === 'GET') {
    const [st, db] = await Promise.all([readJSON('state.json'), readJSON('tickets.json')]);
    const tickets = db ? db.data : emptyDb();
    return send(res, 200, {
      state: st ? st.data : seedState(),
      tickets: listTickets(tickets),
      counts: counts(tickets),
    });
  }

  if (req.method !== 'POST') return send(res, 405, { error: 'Nepodporovaná metoda.' });
  const b = await body(req);

  if (b.action === 'save-state') {
    const state = cleanState(b.state);
    await mutateJSON('state.json', seedState, (cur) => {
      for (const k of Object.keys(cur)) delete cur[k];
      Object.assign(cur, state);
      return { ok: true };
    });
    return send(res, 200, { ok: true });
  }

  if (b.action === 'verify') {
    const followers = normalizeFollowers(b.followers);
    if (!followers.size) throw new HttpError(400, 'V exportu jsem nenašel žádné followery.');
    const now = Date.now();
    const out = await mutateJSON('tickets.json', emptyDb, (db) => ({ report: verify(db, followers, now), counts: counts(db) }));
    const r = out.report;
    await mutateJSON('state.json', seedState, (s) => {
      if (b.setCount !== false) s.followers = followers.size;
      s.lastCheck = {
        at: now, followers: followers.size, verified: r.verified.length, left: r.left.length,
        returned: r.returned.length, expired: r.expired.length, pending: r.pending.length,
      };
      return { ok: true };
    });
    return send(res, 200, { ...out, followers: followers.size });
  }

  if (b.action === 'ticket-update') {
    const nick = cleanNick(b.nick);
    const out = await mutateJSON('tickets.json', emptyDb, (db) => {
      const t = db.tickets[nick];
      if (!t) throw new HttpError(404, 'Jízdenka neexistuje.');
      if (b.remove) delete db.tickets[nick];
      else if ('public' in b) t.public = !!b.public;
      return { ok: true };
    });
    return send(res, 200, out);
  }

  if (b.action === 'ticket-relink') {
    const nick = cleanNick(b.nick);
    const out = await mutateJSON('tickets.json', emptyDb, (db) => {
      const t = db.tickets[nick];
      if (!t) throw new HttpError(404, 'Jízdenka neexistuje.');
      const token = newToken();
      t.tokenHash = sha256(token);
      return { token };
    });
    return send(res, 200, { nick, token: out.token });
  }

  if (b.action === 'set-driver') {
    let driver = null;
    if (b.nick) {
      const nick = cleanNick(b.nick);
      const db = await readJSON('tickets.json');
      const t = db && db.data.tickets[nick];
      if (!t || (t.status !== 'verified' && t.status !== 'pending')) throw new HttpError(404, 'Tenhle nick nemá platnou jízdenku.');
      driver = { nick, at: Date.now() };
    }
    await mutateJSON('state.json', seedState, (cur) => {
      if (driver) cur.driver = driver; else delete cur.driver;
      return { ok: true };
    });
    return send(res, 200, { ok: true, driver });
  }

  if (b.action === 'check') return send(res, 200, { ok: true });

  throw new HttpError(400, 'Neznámá akce.');
});
