import { cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = process.cwd();
const output = resolve(root, 'dist');
const requiredFiles = [
  'index.html',
  'app/static/css/style.css',
  'app/static/js/site.js',
  'app/static/favicon.svg'
];

for (const relativePath of requiredFiles) {
  await stat(resolve(root, relativePath));
}

const html = await readFile(resolve(root, 'index.html'), 'utf8');
const requiredSections = ['home', 'about', 'skills', 'projects', 'contact'];
for (const section of requiredSections) {
  if (!html.includes(`id="${section}"`)) {
    throw new Error(`Required portfolio section is missing: ${section}`);
  }
}
if (html.includes('csrf_token') || html.includes('url_for(') || html.includes('{{')) {
  throw new Error('Server-side template or authentication markup remains in index.html.');
}

await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
await writeFile(resolve(output, 'index.html'), html);
await cp(resolve(root, 'app/static'), resolve(output, 'app/static'), { recursive: true });

console.log(`Static portfolio built in ${output}`);
