import assert from 'node:assert/strict';
import { claim, verify, roster, emptyDb, DAY, assignWagon } from '../../lib/core.js';
const db = emptyDb(); const t0 = 1_800_000_000_000;
const a = claim(db, { nick: '@Jana.N', public: true }, 'ip1', t0);
assert.equal(a.ticket.nick, 'jana.n'); assert.equal(a.ticket.wagon, 1); assert.equal(a.ticket.status, 'pending');
const b = claim(db, { nick: 'petr', public: false }, 'ip1', t0);
const c = claim(db, { nick: 'eva', public: true, avatar: { coat: '#2f6f9f', hat: 'koruna', pet: 'drak' } }, 'ip1', t0);
assert.equal(c.ticket.avatar.hat, 'koruna'); assert.equal(c.ticket.avatar.pet, 'zadny');
assert.throws(() => claim(db, { nick: 'dalsi' }, 'ip1', t0), /dost jízdenek/);
assert.throws(() => claim(db, { nick: 'jana.n' }, 'ip2', t0), /už jízdenku má/);
assert.throws(() => claim(db, { nick: 'Ján' }, 'ip2', t0), /bez diakritiky/);
assert.deepEqual(roster(db).map((x) => x[1]).sort(), ['eva', 'jana.n']);
// den 1: jana a petr sledují, eva ne
let r = verify(db, new Map([['jana.n', 1], ['petr', 2], ['nekdo', 3]]), t0 + DAY);
assert.deepEqual(r.verified.sort(), ['jana.n', 'petr']); assert.deepEqual(r.pending, ['eva']);
assert.deepEqual(roster(db).map((x) => x[1]), ['jana.n', 'eva']); // petr je skrytý, eva čeká
// den 2: jana dala unfollow
r = verify(db, new Map([['petr', 2]]), t0 + 2 * DAY);
assert.deepEqual(r.left, ['jana.n']); assert.equal(db.tickets['jana.n'].lastWagon, 1);
// nový člověk nesmí dostat janin vagón 1
const d = claim(db, { nick: 'novy', public: true }, 'ip3', t0 + 2 * DAY);
assert.equal(d.ticket.wagon, 4);
// den 5: eva propadne, jana se vrátí do vagónu 1
r = verify(db, new Map([['petr', 2], ['jana.n', 9], ['novy', 10]]), t0 + 5 * DAY);
assert.deepEqual(r.expired, ['eva']); assert.deepEqual(r.returned, ['jana.n']); assert.equal(db.tickets['jana.n'].wagon, 1);
assert.equal(db.tickets.eva, undefined);
// po propadnutí je vagón 3 zase volný
assert.equal(assignWagon(db), 3);
console.log('core OK', JSON.stringify(roster(db)));
import { displayFollowers } from '../../lib/core.js';
{
  const db = emptyDb(); const t0 = 1_900_000_000_000;
  claim(db, { nick: 'a1', public: true }, 'x1', t0); claim(db, { nick: 'a2', public: true }, 'x2', t0);
  assert.equal(displayFollowers({ followers: 1 }, db), 2);            // před kontrolou: počet jízdenek
  verify(db, new Map([['a1', 1]]), t0 + 1000);
  const st = { followers: 5, lastCheck: { at: t0 + 1000 } };
  assert.equal(displayFollowers(st, db), 5);                          // po kontrole: export, a2 se nepočítá
  claim(db, { nick: 'a3', public: true }, 'x3', t0 + 2000);
  assert.equal(displayFollowers(st, db), 6);                          // nová jízdenka po kontrole hned +1
  console.log('display OK');
}
