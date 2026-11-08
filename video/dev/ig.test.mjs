import assert from 'node:assert/strict';
import { aliases, countVotes } from '../../lib/ig.js';
assert.deepEqual(aliases('Hradec Králové').sort(), ['hk', 'hradec', 'hradec kralove', 'kralove'].sort());
const opts = [{ to: 'hradec', name: 'Hradec Králové' }, { to: 'trebova', name: 'Česká Třebová' }];
const c = [
  { username: 'a', text: 'Hradec!!', ts: '1' },
  { username: 'b', text: 'jednoznačně ČESKÁ TŘEBOVÁ 🚂', ts: '2' },
  { username: 'a', text: 'ne počkat, třebová', ts: '3' },       // změna názoru: platí poslední
  { username: 'c', text: 'hk', ts: '4' },
  { username: 'd', text: 'hradec nebo třebová?', ts: '5' },     // obojí: nepočítá se
  { username: 'e', text: 'super video', ts: '6' },
  { username: 'f', text: 'ceskatrebova', ts: '7' },               // nepoznáme, nevadí
  { username: 'vlak.followeru', text: 'Hradec, nebo Třebová?', ts: '0' },
  { username: 'g', text: 'Chrudim', ts: '8' },
];
const r = countVotes(c, opts, new Set(['a', 'c']), 'vlak.followeru');
assert.deepEqual(r.all, { hradec: 1, trebova: 2 });
assert.deepEqual(r.riders, { hradec: 1, trebova: 1 });
assert.equal(r.ambiguous, 1);
console.log('ig OK', r);
