// Správa projektu: stav světa, jízdenky a denní kontrola followerů. Chráněno heslem.
import { mutateJSON, readJSON } from '../lib/store.js';
import {
  cleanExtras, cleanNick, cleanState, counts, emptyDb, peakPassengers, HttpError, newToken, normalizeFollowers, renameTicket, seedState, sha256, ticketView, verify,
} from '../lib/core.js';
import { body, requireAdmin, send, wrap } from '../lib/http.js';
import { renameDriver } from '../lib/driver.js';
import { ensureMap } from '../lib/europe.js';
import { bonusKm, cleanEventInput, COAL_FILE, coalStats, currentEvent, emptyCoal, isActive, publicEvent, readCoal } from '../lib/coal.js';

async function coalView() {
  const doc = await readCoal(true);
  const ev = currentEvent(doc);
  const stats = ev ? await coalStats(ev.id, 10) : null;
  return { ev: publicEvent(ev), active: isActive(ev), stats, bonusKm: bonusKm(doc), goldShovels: doc.goldShovels, past: doc.events.length };
}

const listTickets = (db) => Object.values(db.tickets)
  .map(ticketView)
  .sort((a, b) => (a.wagon ?? a.lastWagon ?? 1e9) - (b.wagon ?? b.lastWagon ?? 1e9));

export default wrap(async (req, res) => {
  await requireAdmin(req);

  if (req.method === 'GET') {
    const [st, db, coal] = await Promise.all([readJSON('state.json'), readJSON('tickets.json'), coalView()]);
    const tickets = db ? db.data : emptyDb();
    return send(res, 200, {
      coal,
      state: ensureMap(st ? st.data : seedState()),
      tickets: listTickets(tickets),
      counts: counts(tickets),
      peak: peakPassengers(tickets),
      recovering: tickets.recovering ? { upTo: Number(tickets.reservedUpTo) || 0 } : null,
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

  if (b.action === 'coal-start') {
    const { hours, goal, bonus } = cleanEventInput(b);
    const now = Date.now();
    await mutateJSON(COAL_FILE, emptyCoal, (doc) => {
      if (!Array.isArray(doc.events)) doc.events = [];
      if (isActive(currentEvent(doc), now)) throw new HttpError(409, 'Event už běží. Nejdřív ho ukonči.');
      doc.events.push({ id: 'e' + now.toString(36), start: now, end: now + Math.round(hours * 3600_000), goal, bonus, done: false });
      return { ok: true };
    });
    return send(res, 200, { coal: await coalView() });
  }

  if (b.action === 'coal-stop') {
    const now = Date.now();
    await mutateJSON(COAL_FILE, emptyCoal, (doc) => {
      const ev = currentEvent(doc);
      if (!isActive(ev, now)) return { skipWrite: true, result: { ok: true } };
      ev.end = now;
      return { ok: true };
    });
    return send(res, 200, { coal: await coalView() });
  }

  if (b.action === 'coal-award') {
    const count = Math.max(1, Math.min(20, Math.round(Number(b.count) || 5)));
    const doc0 = await readCoal(true);
    const ev0 = currentEvent(doc0);
    if (!ev0) throw new HttpError(404, 'Žádný uhelný event neproběhl.');
    if (isActive(ev0)) throw new HttpError(409, 'Event ještě běží. Lopaty rozdáš po jeho konci.');
    const db = await readJSON('tickets.json');
    const tickets = db ? db.data.tickets : {};
    const st = await coalStats(ev0.id, 50);
    const winners = st.top.map(([nick]) => nick).filter((nick) => tickets[nick] && (tickets[nick].status === 'pending' || tickets[nick].status === 'verified')).slice(0, count);
    await mutateJSON(COAL_FILE, emptyCoal, (doc) => {
      const ev = doc.events.find((e) => e.id === ev0.id);
      ev.awarded = winners;
      doc.goldShovels = [...new Set([...(doc.goldShovels || []), ...winners])];
      return { ok: true };
    });
    return send(res, 200, { winners, coal: await coalView() });
  }

  if (b.action === 'coal-shovels') {
    const list = [...new Set((Array.isArray(b.list) ? b.list : []).map((x) => cleanNick(x)))].slice(0, 500);
    await mutateJSON(COAL_FILE, emptyCoal, (doc) => { doc.goldShovels = list; return { ok: true }; });
    return send(res, 200, { coal: await coalView() });
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
      else if ('extras' in b) { const x = cleanExtras(b.extras); if (x.length) t.extras = x; else delete t.extras; }
      else if ('public' in b) t.public = !!b.public;
      return { ok: true };
    });
    return send(res, 200, out);
  }

  if (b.action === 'ticket-rename') {
    const from = cleanNick(b.nick);
    const out = await mutateJSON('tickets.json', emptyDb, (db) => {
      const t = renameTicket(db, from, b.to);
      // správa opravuje podle exportu, který právě nahrála: rovnou ověřit
      if (b.verify && t.status === 'pending') { t.status = 'verified'; t.verifiedAt = Date.now(); }
      return { ticket: ticketView(t) };
    });
    await renameDriver(from, out.ticket.nick);
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
