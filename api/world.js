// Veřejný stav světa a seznam ověřených cestujících. Krátce se cachuje na CDN.
import { readJSON } from '../lib/store.js';
import { counts, displayFollowers, driverView, hiddenWagons, roster, seedState, emptyDb } from '../lib/core.js';
import { send, wrap } from '../lib/http.js';

export default wrap(async (req, res) => {
  if (req.method !== 'GET') return send(res, 405, { error: 'Jen GET.' });
  const [st, db] = await Promise.all([
    readJSON('state.json', { fresh: false }),
    readJSON('tickets.json', { fresh: false }),
  ]);
  const tickets = db ? db.data : emptyDb();
  const state = st ? st.data : seedState();
  send(res, 200, {
    online: true,
    state: { ...state, followers: displayFollowers(state, tickets), igFollowers: state.followers },
    roster: roster(tickets),
    hidden: hiddenWagons(tickets),
    counts: counts(tickets),
    driver: driverView(state, tickets),
  }, 'public, max-age=0, s-maxage=15, stale-while-revalidate=60');
});
