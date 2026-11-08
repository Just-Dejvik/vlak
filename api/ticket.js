// Jízdenky návštěvníků: vyzvednutí, stav, úprava panáčka, smazání.
import { mutateJSON, readJSON } from '../lib/store.js';
import { authTicket, claim, cleanAvatar, emptyDb, HttpError, renameTicket, restoreTicket, ticketView } from '../lib/core.js';
import { body, clientIpHash, send, wrap } from '../lib/http.js';
import { renameDriver } from '../lib/driver.js';

const FILE = 'tickets.json';


export default wrap(async (req, res) => {
  const token = req.headers['x-ticket-token'];

  if (req.method === 'GET') {
    const url = new URL(req.url, 'http://x');
    const db = await readJSON(FILE, { fresh: true });
    const t = authTicket(db ? db.data : emptyDb(), url.searchParams.get('nick'), token);
    return send(res, 200, { ticket: ticketView(t) });
  }

  if (req.method !== 'POST') return send(res, 405, { error: 'Nepodporovaná metoda.' });
  const b = await body(req);

  if (b.action === 'claim') {
    const ipHash = clientIpHash(req);
    const out = await mutateJSON(FILE, emptyDb, (db) => claim(db, b, ipHash));
    return send(res, 201, out);
  }

  if (b.action === 'restore') {
    const ipHash = clientIpHash(req);
    const out = await mutateJSON(FILE, emptyDb, (db) => {
      const r = restoreTicket(db, { ...b, token }, ipHash);
      return r.restored ? r : { skipWrite: true, result: r };
    });
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
    return send(res, 200, { ticket: out.ticket });
  }

  if (b.action === 'delete') {
    await mutateJSON(FILE, emptyDb, (db) => {
      const t = authTicket(db, b.nick, token);
      delete db.tickets[t.nick];
      return { ok: true };
    });
    return send(res, 200, { ok: true });
  }

  throw new HttpError(400, 'Neznámá akce.');
});
