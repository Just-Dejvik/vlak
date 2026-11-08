// Správa: propojení s Instagramem a počítání hlasů z komentářů. Chráněno heslem správy.
import { readJSON } from '../lib/store.js';
import { emptyDb, HttpError, seedState } from '../lib/core.js';
import { allComments, clearToken, countVotes, recentMedia, setToken, status } from '../lib/ig.js';
import { body, requireAdmin, send, wrap } from '../lib/http.js';

export default wrap(async (req, res) => {
  await requireAdmin(req);
  if (req.method === 'GET') return send(res, 200, await status());
  if (req.method !== 'POST') return send(res, 405, { error: 'Nepodporovaná metoda.' });
  const b = await body(req);

  if (b.action === 'set-token') {
    const st = await readJSON('state.json');
    return send(res, 200, await setToken(b.token, b.igId, (st && st.data.instagram) || 'vlak.followeru'));
  }
  if (b.action === 'disconnect') { await clearToken(); return send(res, 200, { ok: true }); }
  if (b.action === 'media') return send(res, 200, { media: await recentMedia() });

  if (b.action === 'count') {
    const [st, db, stat] = await Promise.all([readJSON('state.json'), readJSON('tickets.json'), status()]);
    const state = st ? st.data : seedState();
    const v = state.vote;
    if (!v || !v.options || !v.options.length) throw new HttpError(409, 'Teď neprobíhá žádné hlasování.');
    const options = v.options.map((o) => ({ to: o.to, name: (state.nodes[o.to] && state.nodes[o.to].name) || o.to }));
    const tickets = (db ? db.data : emptyDb()).tickets;
    const passengers = new Set(Object.values(tickets).filter((t) => t.status === 'pending' || t.status === 'verified').map((t) => t.nick));
    const ids = (Array.isArray(b.media) ? b.media : [b.media]).filter(Boolean).slice(0, 5);
    if (!ids.length) throw new HttpError(400, 'Vyber video.');
    const comments = (await Promise.all(ids.map(allComments))).flat();
    return send(res, 200, { at: v.at, ...countVotes(comments, options, passengers, String(stat.username || '').toLowerCase()) });
  }

  throw new HttpError(400, 'Neznámá akce.');
});
