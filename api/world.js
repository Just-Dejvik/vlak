// Veřejný stav světa a seznam ověřených cestujících. Krátce se cachuje na CDN.
import { readJSON } from '../lib/store.js';
import { counts, displayFollowers, driverView, hiddenWagons, passengerCount, peakPassengers, roster, seedState, emptyDb } from '../lib/core.js';
import { send, wrap } from '../lib/http.js';
import { cachedFollowers } from '../lib/ig.js';

export default wrap(async (req, res) => {
  if (req.method !== 'GET') return send(res, 405, { error: 'Jen GET.' });
  const [st, db, igN] = await Promise.all([
    readJSON('state.json', { fresh: false }),
    readJSON('tickets.json', { fresh: false }),
    cachedFollowers(),
  ]);
  const tickets = db ? db.data : emptyDb();
  const state = st ? st.data : seedState();
  send(res, 200, {
    online: true,
    state: {
      ...state,
      // během obnovy po výpadku ukazujeme vlak v plné délce, vagóny čekají na své cestující
      followers: passengerCount(tickets),
      peak: peakPassengers(tickets), igFollowers: igN ?? state.followers,
    },
    back: tickets.recovering ? displayFollowers(state, tickets) : null,
    roster: roster(tickets),
    hidden: hiddenWagons(tickets),
    counts: counts(tickets),
    driver: driverView(state, tickets),
    recovering: !!tickets.recovering,
  }, 'public, max-age=0, s-maxage=30, stale-while-revalidate=300');
});
