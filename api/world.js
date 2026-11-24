// Veřejný stav světa a seznam ověřených cestujících. Krátce se cachuje na CDN.
import { readJSON } from '../lib/store.js';
import { counts, displayFollowers, driverView, hiddenWagons, passengerCount, peakPassengers, roster, seedState, emptyDb } from '../lib/core.js';
import { send, wrap } from '../lib/http.js';
import { cachedFollowers } from '../lib/ig.js';
import { ensureMap } from '../lib/europe.js';
import { bonusKm, currentEvent, publicEvent, readCoal } from '../lib/coal.js';

// Poslední úspěšná odpověď: když úložiště vypadne, ukážeme vlak tak, jak byl naposledy.
let lastGood = null;
let lastAt = 0;
const SNAP_MS = 20_000;

export default wrap(async (req, res) => {
  if (req.method !== 'GET') return send(res, 405, { error: 'Jen GET.' });
  if (lastGood && Date.now() - lastAt < SNAP_MS) return send(res, 200, lastGood, CACHE);
  let st, db, igN, coal;
  try {
    [st, db, igN, coal] = await Promise.all([
    readJSON('state.json', { fresh: false }),
    readJSON('tickets.json', { fresh: false }),
    cachedFollowers(),
    readCoal(false),
  ]);
  } catch (e) {
    if (lastGood) return send(res, 200, { ...lastGood, stale: true }, 'public, max-age=0, s-maxage=60');
    throw e;
  }
  const tickets = db ? db.data : emptyDb();
  const state = ensureMap(st ? st.data : seedState());
  lastGood = {
    online: true,
    state: {
      ...state,
      // během obnovy po výpadku ukazujeme vlak v plné délce, vagóny čekají na své cestující
      followers: passengerCount(tickets),
      peak: peakPassengers(tickets), igFollowers: igN ?? state.followers,
      bonusKm: bonusKm(coal), goldShovels: coal.goldShovels, coal: publicEvent(currentEvent(coal)),
    },
    back: tickets.recovering ? displayFollowers(state, tickets) : null,
    roster: roster(tickets),
    hidden: hiddenWagons(tickets),
    counts: counts(tickets),
    driver: driverView(state, tickets),
    recovering: !!tickets.recovering,
  };
  lastAt = Date.now();
  send(res, 200, lastGood, CACHE);
});

const CACHE = 'public, max-age=0, s-maxage=60, stale-while-revalidate=600, stale-if-error=86400';
