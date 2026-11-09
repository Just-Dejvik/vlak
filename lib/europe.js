// Evropská železniční síť pro dlouhou cestu (cíl: objet Zemi). Vzdálenosti jsou orientační:
// vzdušná čára × 1,25 (vlak nejezdí rovně). Doplňuje se k výchozí české mapě.
const N = {
  lipsko: ['Lipsko', 12.38, 51.34], berlin: ['Berlín', 13.37, 52.52], hamburk: ['Hamburk', 10.0, 53.55],
  hannover: ['Hannover', 9.74, 52.37], koln_r: ['Kolín nad Rýnem', 6.96, 50.94], frankfurt: ['Frankfurt', 8.66, 50.11],
  mnichov: ['Mnichov', 11.56, 48.14], stuttgart: ['Stuttgart', 9.18, 48.78], salcburk: ['Salcburk', 13.04, 47.81],
  innsbruck: ['Innsbruck', 11.4, 47.26], graz: ['Štýrský Hradec', 15.44, 47.07], curych: ['Curych', 8.54, 47.38],
  zeneva: ['Ženeva', 6.14, 46.21], pariz: ['Paříž', 2.35, 48.86], strasburk: ['Štrasburk', 7.75, 48.58],
  lyon: ['Lyon', 4.84, 45.76], marseille: ['Marseille', 5.37, 43.3], lille: ['Lille', 3.06, 50.63],
  brusel: ['Brusel', 4.35, 50.85], amsterdam: ['Amsterdam', 4.9, 52.37], londyn: ['Londýn', -0.12, 51.51],
  milan: ['Milán', 9.19, 45.46], benatky: ['Benátky', 12.32, 45.44], florencie: ['Florencie', 11.25, 43.77],
  rim: ['Řím', 12.5, 41.9], neapol: ['Neapol', 14.27, 40.85], barcelona: ['Barcelona', 2.17, 41.39],
  madrid: ['Madrid', -3.7, 40.42], krakov: ['Krakov', 19.94, 50.06], varsava: ['Varšava', 21.01, 52.23],
  vratislav: ['Vratislav', 17.04, 51.11], gdansk: ['Gdaňsk', 18.65, 54.35], poznan: ['Poznaň', 16.93, 52.41],
  zilina: ['Žilina', 18.74, 49.22], kosice: ['Košice', 21.26, 48.72], budapest: ['Budapešť', 19.04, 47.5],
  lublan: ['Lublaň', 14.51, 46.06], zahreb: ['Záhřeb', 15.98, 45.81], belehrad: ['Bělehrad', 20.46, 44.82],
  bukurest: ['Bukurešť', 26.1, 44.43], sofie: ['Sofie', 23.32, 42.7], solun: ['Soluň', 22.94, 40.64],
  atheny: ['Atény', 23.73, 37.98], istanbul: ['Istanbul', 28.98, 41.01], kodan: ['Kodaň', 12.57, 55.68],
  stockholm: ['Stockholm', 18.07, 59.33], oslo: ['Oslo', 10.75, 59.91], vilnius: ['Vilnius', 25.28, 54.69],
  riga: ['Riga', 24.11, 56.95], tallinn: ['Tallinn', 24.75, 59.44], lvov: ['Lvov', 24.03, 49.84], kyjev: ['Kyjev', 30.52, 50.45],
};
const E = `drazdany-lipsko drazdany-berlin lipsko-berlin lipsko-norimberk berlin-hamburk berlin-hannover hamburk-hannover
hannover-koln_r hannover-frankfurt koln_r-frankfurt frankfurt-norimberk frankfurt-stuttgart norimberk-mnichov rezno-mnichov
mnichov-stuttgart mnichov-salcburk mnichov-innsbruck linec-salcburk linec-viden salcburk-innsbruck viden-graz viden-budapest
bratislava-budapest viden-bratislava graz-lublan lublan-zahreb zahreb-budapest zahreb-belehrad budapest-belehrad belehrad-sofie
sofie-istanbul sofie-bukurest budapest-bukurest bukurest-istanbul sofie-solun solun-atheny innsbruck-benatky benatky-milan
lublan-benatky milan-florencie benatky-florencie florencie-rim rim-neapol milan-curych milan-zeneva curych-innsbruck
curych-stuttgart curych-strasburk strasburk-stuttgart strasburk-pariz pariz-lille lille-londyn lille-brusel brusel-amsterdam
brusel-koln_r amsterdam-koln_r amsterdam-hamburk pariz-lyon lyon-zeneva lyon-marseille marseille-barcelona barcelona-madrid
zeneva-curych hamburk-kodan kodan-stockholm kodan-oslo stockholm-oslo liberec-vratislav vratislav-katovice katovice-krakov
krakov-varsava katovice-varsava vratislav-poznan poznan-berlin poznan-varsava varsava-gdansk varsava-vilnius vilnius-riga
riga-tallinn krakov-lvov lvov-kyjev varsava-kyjev ostrava-zilina zilina-kosice bratislava-zilina kosice-budapest`;

const FOREIGN_EXITS = ['drazdany', 'viden', 'bratislava', 'linec', 'norimberk', 'rezno', 'katovice'];
const rad = (d) => (d * Math.PI) / 180;
function km(a, b) {
  const R = 6371, dLat = rad(b.lat - a.lat), dLon = rad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return Math.round(2 * R * Math.asin(Math.sqrt(h)) * 1.25);
}

/** Doplní do stavu evropská města a tratě (nic nemaže, jen přidává; české hraniční „výjezdy“ změní na stanice). */
export function ensureMap(state) {
  if (!state || !state.nodes || !Array.isArray(state.edges)) return state;
  for (const [id, [name, lon, lat]] of Object.entries(N)) if (!state.nodes[id]) state.nodes[id] = { name, lon, lat, lab: 'r' };
  for (const id of FOREIGN_EXITS) if (state.nodes[id] && state.nodes[id].exit) state.nodes[id] = { ...state.nodes[id], exit: false };
  const have = new Set(state.edges.map(([a, b]) => [a, b].sort().join('|')));
  for (const pair of E.split(/\s+/).filter(Boolean)) {
    const [a, b] = pair.split('-');
    if (!state.nodes[a] || !state.nodes[b]) continue;
    const k = [a, b].sort().join('|');
    if (have.has(k)) continue;
    state.edges.push([a, b, km(state.nodes[a], state.nodes[b])]);
    have.add(k);
  }
  state.mapVersion = 'europe-1';
  return state;
}
