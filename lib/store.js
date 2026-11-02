// Úložiště JSON souborů s podmíněným zápisem (ETag).
// Na Vercelu používá privátní Vercel Blob, lokálně (LOCAL_STORE_DIR) obyčejné soubory.
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';

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
    return { data: JSON.parse(text), etag: r.blob.etag };
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

const impl = LOCAL ? local : blob;

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
