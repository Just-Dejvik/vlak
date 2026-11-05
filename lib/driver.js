// Strojvedoucí je uložený nickem ve stavu světa; při opravě nicku ho přesuneme.
import { mutateJSON, readJSON } from './store.js';
import { seedState } from './core.js';

/** Když se přejmenuje strojvedoucí, ať v lokomotivě zůstane. */
export async function renameDriver(from, to) {
  if (from === to) return;
  const st = await readJSON('state.json', { fresh: true });
  if (!st || !st.data.driver || st.data.driver.nick !== from) return;
  await mutateJSON('state.json', seedState, (cur) => {
    if (cur.driver && cur.driver.nick === from) cur.driver.nick = to;
    return { ok: true };
  });
}
