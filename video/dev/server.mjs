// Lokální napodobenina Vercelu: statické soubory + /api/*.js se souborovým úložištěm.
import http from 'node:http';
import { promises as fs } from 'node:fs';
import path from 'node:path';
const ROOT = process.argv[2];
const PORT = +process.argv[3] || 3456;
const types = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'text/javascript' };
http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  try {
    if (url.pathname.startsWith('/api/')) {
      const mod = await import(path.join(ROOT, url.pathname + '.js') + '?t=' + 0);
      return mod.default(req, res);
    }
    const p = url.pathname === '/' ? '/index.html' : url.pathname;
    const data = await fs.readFile(path.join(ROOT, p));
    res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
    res.end(data);
  } catch (e) { res.writeHead(404); res.end('not found'); }
}).listen(PORT, () => console.log('dev on', PORT));
