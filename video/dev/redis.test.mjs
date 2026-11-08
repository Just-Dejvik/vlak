// Úložiště přes Upstash REST s podvrženým serverem v paměti.
import assert from 'node:assert/strict';
process.env.KV_REST_API_URL = 'https://kv.test'; process.env.KV_REST_API_TOKEN = 't';
const db = new Map(); let calls = 0;
globalThis.fetch = async (url, opt) => {
  calls++;
  const cmd = JSON.parse(opt.body);
  let result;
  if (cmd[0] === 'MGET') result = cmd.slice(1).map((k) => db.get(k) ?? null);
  else if (cmd[0] === 'EVAL') {
    const [, , , k1, k2, expect, val, ver] = cmd;
    if ((db.get(k2) ?? '') !== expect) result = 0; else { db.set(k1, val); db.set(k2, ver); result = 1; }
  }
  return { ok: true, json: async () => ({ result }) };
};
const { readJSON, mutateJSON, STORE_KIND } = await import('../../lib/store.js');
assert.equal(STORE_KIND, 'redis');
const st = await readJSON('state.json');
assert.deepEqual(st.data.route, ['praha', 'kolin']);            // prázdné úložiště → stav před výpadkem
assert.equal((await readJSON('tickets.json')).data.peak, 160);
await mutateJSON('tickets.json', () => ({}), (d) => { d.tickets.a = { nick: 'a' }; return { ok: true }; });
assert.equal((await readJSON('tickets.json')).data.tickets.a.nick, 'a');
// souběh: dva zápisy ze stejné verze, druhý se musí zopakovat
const results = await Promise.all([1, 2, 3].map((i) => mutateJSON('tickets.json', () => ({}), (d) => { d.tickets['n' + i] = {}; return { ok: i }; })));
const final = (await readJSON('tickets.json')).data.tickets;
assert.deepEqual(Object.keys(final).sort(), ['a', 'n1', 'n2', 'n3']);
// veřejné čtení se drží v paměti
const before = calls; await readJSON('state.json', { fresh: false }); await readJSON('state.json', { fresh: false });
assert.ok(calls - before <= 1);
console.log('redis OK', results.length);
