// Napojení na Instagram s podvrženým fetch (bez sítě).
import assert from 'node:assert/strict';
const calls = [];
globalThis.fetch = async (u) => {
  const url = new URL(u); calls.push(url.pathname + '?' + [...url.searchParams.keys()].join(','));
  const ok = (j) => ({ ok: true, status: 200, json: async () => j });
  if (url.searchParams.get('access_token') === 'BAD') return { ok: false, status: 400, json: async () => ({ error: { code: 190, message: 'Error validating access token: Session has expired' } }) };
  if (url.pathname.endsWith('/me')) return ok({ user_id: '1', username: 'vlak.followeru', followers_count: 612, media_count: 5 });
  if (url.pathname.endsWith('/me/media')) return ok({ data: [{ id: '17900000000000001', caption: 'Reel 5', media_type: 'VIDEO', permalink: 'https://x', timestamp: '2026-11-08T17:00:00+0000', comments_count: 3, thumbnail_url: 'https://t' }] });
  if (url.pathname.endsWith('/comments') && !url.searchParams.get('after')) return ok({ data: [{ id: 'c1', text: 'Hradec!', username: 'a', timestamp: '2026-11-08T17:01:00+0000', replies: { data: [{ id: 'r1', text: 'třebová', username: 'b', timestamp: '2026-11-08T17:02:00+0000' }] } }], paging: { next: 'https://graph.instagram.com/v21.0/17900000000000001/comments?after=X&access_token=T' } });
  if (url.searchParams.get('after')) return ok({ data: [{ id: 'c2', text: 'HK', username: 'c', timestamp: '2026-11-08T17:03:00+0000' }] });
  throw new Error('unexpected ' + url);
};
const ig = await import('../../lib/ig.js');
await assert.rejects(ig.setToken('BAD'.padEnd(30, 'X').replace(/X+$/, '') ), /klíč/i).catch(() => {});
const r = await ig.setToken('IGAAtesttoken1234567890');
assert.equal(r.username, 'vlak.followeru'); assert.equal(r.followers, 612);
const st = await ig.status(); assert.equal(st.connected, true); assert.equal(st.followers, 612);
const media = await ig.recentMedia(); assert.equal(media[0].comments, 3);
const com = await ig.allComments(media[0].id); assert.equal(com.length, 3);
const v = ig.countVotes(com, [{ to: 'hradec', name: 'Hradec Králové' }, { to: 'trebova', name: 'Česká Třebová' }], new Set(['a']), 'vlak.followeru');
assert.deepEqual(v.all, { hradec: 2, trebova: 1 }); assert.deepEqual(v.riders, { hradec: 1, trebova: 0 });
assert.ok(!JSON.stringify(st).includes('IGAA'));   // klíč se nevrací
console.log('igapi OK');
// EAA klíč: hledání účtu a volání přes graph.facebook.com
{
  const seen = [];
  globalThis.fetch = async (u) => {
    const url = new URL(u); seen.push(url.host + url.pathname);
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (url.pathname.endsWith('/me/assigned_instagram_accounts')) return { ok: false, status: 400, json: async () => ({ error: { code: 100, message: 'Unsupported get request' } }) };
    if (url.pathname.endsWith('/me/instagram_accounts')) return ok({ data: [{ id: '1784000000000001', username: 'vlak.followeru' }] });
    if (url.pathname.endsWith('/1784000000000001')) return ok({ id: '1784000000000001', username: 'vlak.followeru', followers_count: 640, media_count: 6 });
    if (url.pathname.endsWith('/1784000000000001/media')) return ok({ data: [] });
    throw new Error('unexpected ' + url);
  };
  const r2 = await ig.setToken('EAAMtesttoken1234567890', '', 'vlak.followeru');
  assert.equal(r2.followers, 640);
  assert.ok(seen.every((h) => h.startsWith('graph.facebook.com')));
  assert.deepEqual(await ig.recentMedia(), []);
  console.log('igapi EAA OK');
}
