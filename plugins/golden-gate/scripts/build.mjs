import { build } from 'esbuild';
import { readFile, mkdir, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = new URL('../', import.meta.url);
await mkdir(new URL('dist/', root), { recursive: true });
const result = await build({
  entryPoints: [fileURLToPath(new URL('src/server.mjs', root))],
  outfile: fileURLToPath(new URL('dist/server.mjs', root)),
  platform: 'node', target: 'node22', format: 'esm', bundle: true,
  banner: { js: "import { createRequire as __createRequire } from 'node:module'; const require = __createRequire(import.meta.url);" },
  define: {
    GOLDEN_GATE_HTML: JSON.stringify(await readFile(new URL('web/entry.html', root), 'utf8')),
    GOLDEN_GATE_VERSION: JSON.stringify(JSON.parse(await readFile(new URL('package.json', root), 'utf8')).version),
  },
  legalComments: 'eof', sourcemap: false, metafile: true,
});
const packages = new Set();
for (const input of Object.keys(result.metafile.inputs)) {
  const marker = input.lastIndexOf('node_modules/'); if (marker < 0) continue;
  const tail = input.slice(marker + 13).split('/');
  const name = tail[0].startsWith('@') ? tail.slice(0, 2).join('/') : tail[0];
  packages.add(path.resolve(input.slice(0, marker + 13), name));
}
const notices = ['Third-party code bundled in server.mjs. Original licenses follow.\n'];
for (const dir of [...packages].sort()) {
  const pkg = JSON.parse(await readFile(path.join(dir, 'package.json'), 'utf8'));
  notices.push(`\n===== ${pkg.name}@${pkg.version} (${pkg.license || 'see package license'}) =====\n`);
  for (const file of (await readdir(dir)).filter(name => /^(?:licen[sc]e|notice|copying)(?:\.|$)/i.test(name))) {
    try { notices.push(await readFile(path.join(dir, file), 'utf8')); } catch { /* License directories are not text files. */ }
  }
}
await writeFile(new URL('dist/THIRD_PARTY_LICENSES.txt', root), notices.join('\n'));
console.log('Built self-contained dist/server.mjs');
