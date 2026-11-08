// Stav vlaku těsně před výpadkem úložiště Vercel Blob (8. 11. 2026, 15:14), ze kterého nový
// Upstash Redis začne, dokud v něm nic není. Jízdenky se obnoví z mobilů cestujících
// (akce restore) a po odemčení Blobu se dosypou zbytek.
import SEED from './seed.js';

export function recoveredState() {
  const s = JSON.parse(JSON.stringify(SEED));
  Object.assign(s, {
    instagram: 'vlak.followeru',
    followers: 80,
    kmPerPassenger: 1,
    route: ['praha', 'kolin'],
    vote: { at: 'kolin', deadline: '', options: [{ to: 'pardubice', votes: 11 }, { to: 'hbrod', votes: 2 }] },
    chronicle: [{
      date: '2026-11-02', node: 'praha', task: '', title: 'Nástupiště 1',
      text: 'Na prvním nástupišti stojí lokomotiva a jeden jediný vagón. Výpravčí drží píšťalku a čeká, kam ho pošlete.',
      voteResult: 'Kolín 50 % · Plzeň 17 % · Ústí nad Labem 8 % · Tábor 25 %',
    }],
    specials: [],
    driver: { nick: 'novottna_s', at: 1793901619631 },
    lastCheck: { at: 1793916904838, expired: 0, followers: 80, left: 0, pending: 39, returned: 0, verified: 0 },
  });
  return s;
}

// 160 cestujících = 160 km: vlak po výpadku necouvá.
export const recoveredDb = () => ({ tickets: {}, rate: {}, peak: 160, recovering: true, reservedUpTo: 160 });
