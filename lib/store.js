// Úložiště JSON souborů s podmíněným zápisem (ETag/verze).
// Na Vercelu Upstash Redis (KV_REST_API_URL), dříve Vercel Blob; lokálně (LOCAL_STORE_DIR) obyčejné soubory.
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { recoveredDb, recoveredState } from './recovered.js';

export class ConflictError extends Error {}

const LOCAL = process.env.LOCAL_STORE_DIR;

/* ---------- lokální souborové úložiště pro testy ---------- */
const local = {
  async read(name) {
    try {
      const text = await fs.readFile(path.join(LOCAL, name), 'utf8');
      return { data: JSON.parse(text), etag: createHash('sha1').update(text).digest('hex') };
    } catch (e) {
      if (e.code === 'ENOENT') return null;
      throw e;
    }
  },
  // Podmíněný zápis musí být atomický jako u Blobu: zámek v procesu + zápis přes přejmenování.
  lock: Promise.resolve(),
  write(name, data, { etag, create }) {
    const run = async () => {
      await fs.mkdir(LOCAL, { recursive: true });
      const cur = await local.read(name);
      if (create && cur) throw new ConflictError('exists');
      if (!create && (!cur || cur.etag !== etag)) throw new ConflictError('etag');
      const tmp = path.join(LOCAL, `${name}.${process.pid}.${Math.random().toString(36).slice(2)}`);
      await fs.writeFile(tmp, JSON.stringify(data));
      await fs.rename(tmp, path.join(LOCAL, name));
    };
    const p = local.lock.then(run, run);
    local.lock = p.catch(() => {});
    return p;
  },
};

/* ---------- Vercel Blob ---------- */
let sdk;
const loadSdk = async () => (sdk ||= await import('@vercel/blob'));
const blob = {
  async read(name, { fresh = true } = {}) {
    const b = await loadSdk();
    const r = await b.get(name, { access: 'private', useCache: !fresh });
    if (!r || r.statusCode !== 200) return null;
    const text = await new Response(r.stream).text();
    // CDN u komprimovaných souborů vrací slabý ETag (W/"…"), podmíněný zápis potřebuje silný.
    return { data: JSON.parse(text), etag: String(r.blob.etag || '').replace(/^W\//, '') };
  },
  async write(name, data, { etag, create }) {
    const b = await loadSdk();
    const opts = {
      access: 'private',
      contentType: 'application/json',
      addRandomSuffix: false,
      cacheControlMaxAge: 60,
    };
    if (create) opts.allowOverwrite = false;
    else { opts.allowOverwrite = true; opts.ifMatch = etag; }
    try {
      await b.put(name, JSON.stringify(data), opts);
    } catch (e) {
      if (e instanceof b.BlobPreconditionFailedError) throw new ConflictError('etag');
      if (create && /exist/i.test(String(e && e.message))) throw new ConflictError('exists');
      throw e;
    }
  },
};

/* ---------- Upstash Redis přes REST (bez závislostí) ---------- */
// Dokument leží v klíči vf:<jméno>, jeho verze v vf:<jméno>:v. Zápis je atomický Lua skript:
// zapíše jen tehdy, když se verze mezitím nezměnila (stejně jako ifMatch u Blobu).
const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const CAS = "local v=redis.call('GET',KEYS[2]) or '' if v~=ARGV[1] then return 0 end redis.call('SET',KEYS[1],ARGV[2]) redis.call('SET',KEYS[2],ARGV[3]) return 1";
async function kv(cmd) {
  const r = await fetch(KV_URL, { method: 'POST', headers: { authorization: `Bearer ${KV_TOKEN}`, 'content-type': 'application/json' }, body: JSON.stringify(cmd) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error(`Úložiště: ${j.error || r.status}`);
  return j.result;
}
// Krátká paměť v rámci jedné běžící funkce: veřejná čtení (fresh: false) nešetří jen čas, ale hlavně operace.
const memo = new Map();
// Prázdné nové úložiště začne ze stavu před výpadkem (první zápis ho tam opravdu uloží).
const FALLBACK = { 'state.json': recoveredState, 'tickets.json': recoveredDb };
const MEMO_MS = 10_000;
const redis = {
  async read(name, { fresh = true } = {}) {
    const hit = memo.get(name);
    if (!fresh && hit && Date.now() - hit.at < MEMO_MS) return hit.val;
    const [text, ver] = await kv(['MGET', `vf:${name}`, `vf:${name}:v`]);
    const fb = text == null && FALLBACK[name];
    const val = text != null ? { data: JSON.parse(text), etag: ver || '' } : (fb ? { data: fb(), etag: '' } : null);
    memo.set(name, { at: Date.now(), val });
    return val;
  },
  async write(name, data, { etag, create }) {
    const ver = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    const ok = await kv(['EVAL', CAS, '2', `vf:${name}`, `vf:${name}:v`, create ? '' : String(etag || ''), JSON.stringify(data), ver]);
    if (ok !== 1) throw new ConflictError(create ? 'exists' : 'etag');
    memo.delete(name);
  },
};

const impl = LOCAL ? local : (KV_URL && KV_TOKEN ? redis : blob);
export const STORE_KIND = LOCAL ? 'local' : (KV_URL && KV_TOKEN ? 'redis' : 'blob');

/** Přečte JSON soubor. Vrací { data, etag } nebo null. */
export function readJSON(name, opts) {
  return impl.read(name, opts);
}

/**
 * Bezpečně upraví soubor: přečte, zavolá fn(data), zapíše jen když se mezitím nezměnil.
 * Při souběhu to zkusí znovu. fn musí být čistá (může se volat víckrát).
 * fn vrací výsledek; když vrátí { skipWrite: true, result }, nic se nezapisuje.
 */
export async function mutateJSON(name, init, fn) {
  for (let attempt = 0; attempt < 8; attempt++) {
    const cur = await impl.read(name, { fresh: true });
    const data = cur ? cur.data : init();
    const out = await fn(data);
    if (out && out.skipWrite) return out.result;
    try {
      await impl.write(name, data, cur ? { etag: cur.etag } : { create: true });
      return out;
    } catch (e) {
      if (!(e instanceof ConflictError)) throw e;
      await new Promise((r) => setTimeout(r, 40 + Math.random() * 160 * (attempt + 1)));
    }
  }
  const err = new Error('Server je zrovna vytížený, zkus to prosím za chvilku.');
  err.status = 503;
  throw err;
}
