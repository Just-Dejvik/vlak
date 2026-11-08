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
  assert.equal(displayFollowers({ followers: 70 }, db), 2);           // vlak = jen jízdenky, ne followeři
  verify(db, new Map([['a1', 1]]), t0 + 5 * 86400000);
  const st = { followers: 5, lastCheck: { at: t0 + 1000 } };
  assert.equal(displayFollowers(st, db), 1);                          // a2 bez followu propadla
  claim(db, { nick: 'a3', public: true }, 'x3', t0 + 2000);
  assert.equal(displayFollowers(st, db), 2);                          // nová jízdenka hned +1
  console.log('display OK');
}
import { renameTicket } from '../../lib/core.js';
{
  const db = emptyDb(); const t0 = 1_900_000_000_000;
  claim(db, { nick: 'trutnovak', public: true, avatar: { hat: 'koruna' } }, 'y1', t0);
  claim(db, { nick: 'obsazeny', public: true }, 'y2', t0);
  const w = db.tickets.trutnovak.wagon;
  verify(db, new Map([['trutnovak_', 1], ['novy.clovek', 1]]), t0 + 1000);
  assert.equal(db.tickets.trutnovak.status, 'pending');
  const t = renameTicket(db, 'trutnovak', 'trutnovak_', t0 + 2000);
  assert.equal(t.status, 'verified');                       // byl v posledním exportu → hned ověřený
  assert.equal(t.wagon, w); assert.equal(t.avatar.hat, 'koruna');
  assert.equal(db.tickets.trutnovak, undefined);
  assert.throws(() => renameTicket(db, 'trutnovak_', 'obsazeny'), /už jízdenku má/);
  const c = claim(db, { nick: 'novy.clovek', public: true }, 'y3', t0 + 3000);
  assert.equal(c.ticket.status, 'verified');                // nový cestující z exportu je ověřený rovnou
  const d = claim(db, { nick: 'cizi', public: true }, 'y4', t0 + 3000);
  assert.equal(d.ticket.status, 'pending');
  assert.ok(!JSON.stringify(db).includes('novy.clovek"]'));
  console.log('rename OK');
}
import { peakPassengers } from '../../lib/core.js';
{
  const db = emptyDb(); const t0 = 1_900_000_000_000;
  for (let i = 0; i < 5; i++) claim(db, { nick: 'p' + i, public: true }, 'z' + i, t0);
  assert.equal(peakPassengers(db), 5);
  delete db.peak;                                           // stará data bez maxima
  verify(db, new Map([['p0', 1]]), t0 + 5 * 86400000);      // 4 jízdenky propadnou
  assert.equal(Object.keys(db.tickets).length, 1);
  assert.equal(peakPassengers(db), 5);                       // ujeté km zůstanou
  console.log('peak OK');
}
import { restoreTicket } from '../../lib/core.js';
import { recoveredDb } from '../../lib/recovered.js';
{
  const db = recoveredDb(); const t0 = 1_900_000_000_000;
  const tok = 'x'.repeat(32);
  const r = restoreTicket(db, { nick: 'Kikinkaa', token: tok, wagon: 3, avatar: { hat: 'koruna' }, public: true }, 'ip1', t0);
  assert.equal(r.restored, true); assert.equal(r.ticket.wagon, 3); assert.equal(r.ticket.avatar.hat, 'koruna');
  assert.equal(restoreTicket(db, { nick: 'kikinkaa', token: tok, wagon: 3 }, 'ip1', t0).restored, false);   // znovu: nic
  assert.throws(() => restoreTicket(db, { nick: 'kikinkaa', token: 'y'.repeat(32), wagon: 3 }, 'ip2', t0), /někdo jiný/);
  const n = claim(db, { nick: 'novy', public: true }, 'ip3', t0);
  assert.equal(n.ticket.wagon, 161);                        // nový cestující nebere vagón někoho, kdo se ještě nevrátil
  assert.equal(peakPassengers(db), 160);
  delete db.recovering;
  assert.throws(() => restoreTicket(db, { nick: 'dalsi', token: tok, wagon: 9 }, 'ip1', t0), /skončila/);
  console.log('restore OK');
}
