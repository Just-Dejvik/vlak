// Uhelný event: cestující švihem házejí uhlí do kotle. Společný cíl posune vlak o bonusové km,
// nejlepší topiči dostanou zlatou lopatu.
// Nastavení eventů je v dokumentu coal.json (mění jen správa a jednou dosažení cíle).
// Počítadla jsou zvlášť v Redisu (atomické INCRBY / ZINCRBY), aby tisíce hodů nezatěžovaly dokumenty.
import { kvCmd, kvPipe, mutateJSON, readJSON, STORE_KIND } from './store.js';
import { HttpError } from './core.js';

export const COAL_FILE = 'coal.json';
export const emptyCoal = () => ({ events: [], goldShovels: [] });
export const RATE = 3.5;      // hodů za sekundu, víc ruka nedá
export const BURST = 15;      // první dávka
export const CAP = 30;        // nejvíc za jeden požadavek

export async function readCoal(fresh = false) {
  const d = await readJSON(COAL_FILE, { fresh });
  const data = d ? d.data : emptyCoal();
  if (!Array.isArray(data.events)) data.events = [];
  if (!Array.isArray(data.goldShovels)) data.goldShovels = [];
  return data;
}
export const currentEvent = (doc) => (doc.events.length ? doc.events[doc.events.length - 1] : null);
export const isActive = (ev, now = Date.now()) => !!ev && now >= ev.start && now < ev.end;
export const bonusKm = (doc) => doc.events.reduce((s, e) => s + (e.done ? Number(e.bonus) || 0 : 0), 0);
export function publicEvent(ev) {
  if (!ev) return null;
  const { id, start, end, goal, bonus, done, doneAt, awarded } = ev;
  return { id, start, end, goal, bonus, done: !!done, doneAt: doneAt || null, awarded: awarded || null };
}

const K = (id) => ({ total: `vf:coal:${id}:total`, lb: `vf:coal:${id}:lb`, last: (nick) => `vf:coal:${id}:last:${nick}` });
const LUA = `local last=tonumber(redis.call('GET',KEYS[1]) or '0')
local now=tonumber(ARGV[1]) local n=tonumber(ARGV[2])
local allow
if last==0 then allow=tonumber(ARGV[5]) else allow=math.floor((now-last)*tonumber(ARGV[4])/1000)+1 end
if allow>tonumber(ARGV[6]) then allow=tonumber(ARGV[6]) end
if allow>n then allow=n end
if allow<0 then allow=0 end
local total local mine
if allow>0 then
  redis.call('SET',KEYS[1],now,'EX',900)
  total=redis.call('INCRBY',KEYS[2],allow)
  mine=redis.call('ZINCRBY',KEYS[3],allow,ARGV[3])
else
  total=tonumber(redis.call('GET',KEYS[2]) or '0')
  mine=redis.call('ZSCORE',KEYS[3],ARGV[3]) or '0'
end
return {allow,total,tostring(mine)}`;

// Bez Redisu (lokální vývoj, natáčení): stejná pravidla v paměti procesu.
const mem = { total: new Map(), lb: new Map(), last: new Map() };
function memThrow(id, nick, n, now) {
  const lk = id + '|' + nick;
  const last = mem.last.get(lk) || 0;
  let allow = last ? Math.floor((now - last) * RATE / 1000) + 1 : BURST;
  allow = Math.max(0, Math.min(allow, CAP, n));
  if (!mem.lb.has(id)) mem.lb.set(id, new Map());
  const lb = mem.lb.get(id);
  if (allow > 0) {
    mem.last.set(lk, now);
    mem.total.set(id, (mem.total.get(id) || 0) + allow);
    lb.set(nick, (lb.get(nick) || 0) + allow);
  }
  return { added: allow, total: mem.total.get(id) || 0, mine: lb.get(nick) || 0 };
}

/** Připíše hody (s ochranou proti klikacím robotům: nejvýš RATE za sekundu). */
export async function throwCoal(id, nick, n, now = Date.now()) {
  if (STORE_KIND !== 'redis') return memThrow(id, nick, n, now);
  const k = K(id);
  const [allow, total, mine] = await kvCmd(['EVAL', LUA, '3', k.last(nick), k.total, k.lb, String(now), String(n), nick, String(RATE), String(BURST), String(CAP)]);
  return { added: Number(allow) || 0, total: Number(total) || 0, mine: Math.round(Number(mine) || 0) };
}

/** Celkem hodů, počet topičů a nejlepší topiči. */
export async function coalStats(id, top = 10) {
  if (STORE_KIND !== 'redis') {
    const lb = mem.lb.get(id) || new Map();
    const list = [...lb.entries()].sort((a, b) => b[1] - a[1]).slice(0, top);
    return { total: mem.total.get(id) || 0, players: lb.size, top: list };
  }
  const k = K(id);
  const [total, range, players] = await kvPipe([['GET', k.total], ['ZREVRANGE', k.lb, '0', String(top - 1), 'WITHSCORES'], ['ZCARD', k.lb]]);
  const list = [];
  for (let i = 0; i + 1 < (range || []).length; i += 2) list.push([range[i], Math.round(Number(range[i + 1]) || 0)]);
  return { total: Number(total) || 0, players: Number(players) || 0, top: list };
}

/** Kolik hodil jeden cestující. */
export async function coalMine(id, nick) {
  nick = String(nick || '').toLowerCase().slice(0, 30);
  if (STORE_KIND !== 'redis') return (mem.lb.get(id) || new Map()).get(nick) || 0;
  return Math.round(Number(await kvCmd(['ZSCORE', K(id).lb, nick])) || 0);
}

/** Cíl splněn: zapíše se jednou, bonusové km se pak počítají ze všech splněných eventů. */
export async function markDone(id, now = Date.now()) {
  return mutateJSON(COAL_FILE, emptyCoal, (doc) => {
    const ev = doc.events.find((e) => e.id === id);
    if (!ev || ev.done) return { skipWrite: true, result: { ok: true } };
    ev.done = true; ev.doneAt = now;
    return { ok: true };
  });
}

export function cleanEventInput(b) {
  const hours = Number(b.hours), goal = Math.round(Number(b.goal)), bonus = Math.round(Number(b.bonus));
  if (!(hours >= 0.05 && hours <= 48)) throw new HttpError(400, 'Délka eventu musí být mezi 3 minutami a 48 hodinami.');
  if (!(goal >= 10 && goal <= 50_000_000)) throw new HttpError(400, 'Cíl musí být aspoň 10 lopat.');
  if (!(bonus >= 0 && bonus <= 2000)) throw new HttpError(400, 'Bonus musí být 0 až 2000 km.');
  return { hours, goal, bonus };
}
