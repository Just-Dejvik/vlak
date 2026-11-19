// Jízdenky návštěvníků: vyzvednutí, stav, úprava panáčka, smazání.
import { mutateJSON, readJSON } from '../lib/store.js';
import { authTicket, claim, cleanAvatar, emptyDb, HttpError, renameTicket, restoreTicket, ticketView } from '../lib/core.js';
import { body, clientIpHash, readTicketCookie, send, setTicketCookie, wrap } from '../lib/http.js';
import { renameDriver } from '../lib/driver.js';

const FILE = 'tickets.json';


export default wrap(async (req, res) => {
  const token = req.headers['x-ticket-token'];

  if (req.method === 'GET') {
    const url = new URL(req.url, 'http://x');
    const db = await readJSON(FILE, { fresh: true });
    const data = db ? db.data : emptyDb();
    if (url.searchParams.get('me') === '1') {
      // obnova jízdenky z cookie, když prohlížeč smazal místní úložiště
      const c = readTicketCookie(req);
      if (!c) throw new HttpError(404, 'Žádná uložená jízdenka.');
      let t;
      try { t = authTicket(data, c.nick, c.token); }
      catch (e) { setTicketCookie(res, null); throw e; }
      setTicketCookie(res, t.nick, c.token);
      return send(res, 200, { ticket: ticketView(t), token: c.token });
    }
    const t = authTicket(data, url.searchParams.get('nick'), token);
    setTicketCookie(res, t.nick, token);
    return send(res, 200, { ticket: ticketView(t) });
  }

  if (req.method !== 'POST') return send(res, 405, { error: 'Nepodporovaná metoda.' });
  const b = await body(req);

  if (b.action === 'claim') {
    if (b.age !== true) throw new HttpError(400, 'Potvrď prosím, že je ti aspoň 15 let, nebo že s tím souhlasí rodiče.');
    const ipHash = clientIpHash(req);
    const out = await mutateJSON(FILE, emptyDb, (db) => claim(db, b, ipHash));
    if (out && out.ticket && out.token) setTicketCookie(res, out.ticket.nick, out.token);
    return send(res, 201, out);
  }

  if (b.action === 'restore') {
    const ipHash = clientIpHash(req);
    const out = await mutateJSON(FILE, emptyDb, (db) => {
      const r = restoreTicket(db, { ...b, token }, ipHash);
      return r.restored ? r : { skipWrite: true, result: r };
    });
    if (out.ticket && token) setTicketCookie(res, out.ticket.nick, token);
    return send(res, out.restored ? 201 : 200, out);
  }

  if (b.action === 'update') {
    const out = await mutateJSON(FILE, emptyDb, (db) => {
      const t = authTicket(db, b.nick, token);
      if ('public' in b) t.public = !!b.public;
      if (b.avatar) t.avatar = cleanAvatar(b.avatar, t.avatar);
      return { ticket: ticketView(t) };
    });
    return send(res, 200, out);
  }

  if (b.action === 'rename') {
    const out = await mutateJSON(FILE, emptyDb, (db) => {
      const t = authTicket(db, b.nick, token);
      const from = t.nick;
      return { from, ticket: ticketView(renameTicket(db, from, b.to)) };
    });
    await renameDriver(out.from, out.ticket.nick);
    setTicketCookie(res, out.ticket.nick, token);
    return send(res, 200, { ticket: out.ticket });
  }

  if (b.action === 'delete') {
    await mutateJSON(FILE, emptyDb, (db) => {
      const t = authTicket(db, b.nick, token);
      delete db.tickets[t.nick];
      return { ok: true };
    });
    setTicketCookie(res, null);
    return send(res, 200, { ok: true });
  }

  throw new HttpError(400, 'Neznámá akce.');
});
