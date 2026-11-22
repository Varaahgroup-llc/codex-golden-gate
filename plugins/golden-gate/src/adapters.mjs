import { spawn } from 'node:child_process';
import * as fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';

const name = z.string().regex(/^[A-Za-z_][A-Za-z0-9_]{0,127}$/);
const safe = z.string().min(1).max(256).regex(/^[A-Za-z0-9][A-Za-z0-9_.@/ -]*$/);
export const destinationSchema = z.discriminatedUnion('provider', [
  z.object({ provider: z.literal('env'), file: z.string().max(4096), name }).strict(),
  z.object({
    provider: z.literal('cloudflare-local'),
    configFile: z.string().max(4096),
    environment: z.string().regex(/^[A-Za-z0-9_-]{1,128}$/).optional(),
    name,
  }).strict(),
  z.object({ provider: z.literal('github'), repo: z.string().regex(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/), name, environment: safe.optional() }).strict(),
  z.object({ provider: z.literal('aws'), secretArn: z.string().regex(/^arn:aws(?:-us-gov|-cn)?:secretsmanager:[a-z0-9-]+:\d{12}:secret:[A-Za-z0-9/_+=.@-]+$/), profile: safe }).strict(),
  z.object({ provider: z.literal('azure'), vault: z.string().regex(/^[A-Za-z][A-Za-z0-9-]{1,22}[A-Za-z0-9]$/), subscription: safe, name: z.string().regex(/^[A-Za-z0-9-]{1,127}$/) }).strict(),
]);

export class SafeError extends Error {}
export class UncertainError extends SafeError {}

// No shell, no secret argv, no provider output in error messages or receipts.
export function run(command, args, { input, capture = false, cwd, timeout = 45000 } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, shell: false, windowsHide: true,
      env: { ...process.env, GH_PROMPT_DISABLED: '1', AWS_PAGER: '', AWS_CLI_AUTO_PROMPT: 'off', AZURE_CORE_COLLECT_TELEMETRY: '0' },
      stdio: ['pipe', capture ? 'pipe' : 'ignore', 'ignore'] });
    let output = '', settled = false;
    const finish = (err, value) => { if (settled) return; settled = true; clearTimeout(timer); err ? reject(err) : resolve(value); };
    const timer = setTimeout(() => { child.kill('SIGKILL'); finish(new SafeError('Provider command timed out.')); }, timeout);
    child.stdout?.on('data', chunk => { output += chunk; if (output.length > 16384) { child.kill('SIGKILL'); finish(new SafeError('Unexpected provider response.')); } });
    child.stdin.on('error', () => {});
    child.on('error', () => finish(new SafeError('Required provider CLI is unavailable.')));
    child.on('close', code => finish(code === 0 ? null : new SafeError('Provider command failed. Check CLI login and destination permissions.'), output.trim()));
    child.stdin.end(input);
  });
}

async function safeFile(file) {
  if (!path.isAbsolute(file) || /[\r\n\0]/.test(file)) throw new SafeError('Use an absolute dotenv path.');
  const base = path.basename(file);
  if (!/^(?:\.env(?:\.[A-Za-z0-9_-]+)*|\.dev\.vars(?:\.[A-Za-z0-9_-]+)*)$/.test(base) || /\.(?:example|sample|template|dist)(?:\.|$)/i.test(base)) throw new SafeError('Choose a private .env or .dev.vars file, not an example file.');
  let current = path.parse(file).root;
  for (const part of file.slice(current.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    try { if ((await fs.lstat(current)).isSymbolicLink()) throw new SafeError('Symlink destinations are unsupported.'); }
    catch (err) { if (err.code !== 'ENOENT') throw err; }
  }
  const parent = await fs.stat(path.dirname(file));
  if (!parent.isDirectory()) throw new SafeError('Destination parent must exist.');
  try { const st = await fs.lstat(file); if (!st.isFile() || st.nlink !== 1 || st.size > 1048576) throw new SafeError('Destination must be a small, regular private file.'); }
  catch (err) { if (err.code !== 'ENOENT') throw err; }
}

async function gitGuard(file, execute) {
  const cwd = path.dirname(file);
  let ancestor = cwd, hasGit = false;
  for (;;) {
    try { await fs.lstat(path.join(ancestor, '.git')); hasGit = true; break; } catch (err) { if (err.code !== 'ENOENT') throw err; }
    const parent = path.dirname(ancestor); if (parent === ancestor) break; ancestor = parent;
  }
  let inRepo = false;
  try { inRepo = (await execute('git', ['rev-parse', '--is-inside-work-tree'], { cwd, capture: true })) === 'true'; }
  catch { if (hasGit) throw new SafeError('Could not verify Git tracking and ignore rules.'); }
  if (hasGit && !inRepo) throw new SafeError('Could not verify Git tracking and ignore rules.');
  if (!inRepo) return;
  const rel = path.basename(file);
  const tracked = await execute('git', ['ls-files', '--', rel], { cwd, capture: true });
  if (tracked) throw new SafeError('Refusing a tracked dotenv file. Choose an ignored, untracked destination.');
  try { await execute('git', ['check-ignore', '--no-index', '-q', '--', rel], { cwd }); }
  catch { throw new SafeError('Ignore this dotenv file in Git before saving a secret.'); }
}

// Conservative parser: never corrupt an existing multiline or exotic dotenv file.
export function updateDotenv(text, key, secret) {
  if (text.includes('\0')) throw new SafeError('Unsupported dotenv syntax.');
  const lines = text.split(/\r?\n/), matches = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*(?:#.*)?$/.test(line)) continue;
    const match = line.match(/^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/);
    if (!match) throw new SafeError('Existing dotenv syntax is unsupported; use a separate private file.');
    const value = match[2];
    if (value.startsWith('"') && !/^"(?:[^"\\]|\\.)*"\s*(?:#.*)?$/.test(value)) throw new SafeError('Existing multiline dotenv values are unsupported.');
    if (value.startsWith("'") && !/^'[^']*'\s*(?:#.*)?$/.test(value)) throw new SafeError('Existing multiline dotenv values are unsupported.');
    if (value.startsWith('`')) throw new SafeError('Existing backtick dotenv values are unsupported.');
    if (match[1] === key) matches.push(i);
  }
  if (matches.length > 1) throw new SafeError('Duplicate destination keys require manual cleanup.');
  // dotenv parsers do not agree on backslash/quote unescaping. Use only lossless
  // single-line forms and refuse ambiguous values instead of corrupting them.
  let encoded;
  if (/[\r\n]/.test(secret)) throw new SafeError('This dotenv adapter accepts single-line values only.');
  if (!secret.includes("'")) encoded = "'" + secret + "'";
  else if (!/["\\]/.test(secret)) encoded = '"' + secret + '"';
  else throw new SafeError('This value cannot be represented losslessly by the supported dotenv format. Use a secret manager.');
  const entry = `${key}=${encoded}`;
  if (matches.length) lines[matches[0]] = entry;
  else { if (lines.at(-1) === '') lines.pop(); lines.push(entry); }
  return lines.join('\n').replace(/\n*$/, '\n');
}

// Inspect filenames only. A named Wrangler environment can fall back to a
// shared file, but an environment-specific request must never write there.
async function workerDevFile(destination) {
  const { configFile, environment } = destination;
  if (!path.isAbsolute(configFile) || /[\r\n\0]/.test(configFile) ||
      !['wrangler.toml', 'wrangler.json', 'wrangler.jsonc'].includes(path.basename(configFile))) {
    throw new SafeError('Choose the absolute Wrangler configuration file used by this local Worker.');
  }
  if (!(await fs.lstat(configFile)).isFile()) throw new SafeError('Choose a regular Wrangler configuration file.');
  const directory = await fs.realpath(path.dirname(configFile));
  const names = await fs.readdir(directory);
  const target = environment ? `.dev.vars.${environment}` : '.dev.vars';
  if (!names.includes(target)) {
    if (environment && names.includes('.dev.vars')) {
      throw new SafeError('This environment inherits .dev.vars. Choose the shared file explicitly or prepare a complete environment-specific file.');
    }
    // A new shared .dev.vars can mask dotenv files across environments.
    // A new scoped file affects only that environment's dotenv precedence.
    const shadowsDotenv = environment
      ? ['.env', '.env.local', `.env.${environment}`, `.env.${environment}.local`].some(file => names.includes(file))
      : names.some(file => /^\.env(?:\.|$)/.test(file) && !/\.(?:example|sample|template|dist)(?:\.|$)/i.test(file));
    if (shadowsDotenv) {
      throw new SafeError('Creating this .dev.vars file could hide existing dotenv settings. Review the local configuration and choose an explicit destination.');
    }
  }
  return path.join(directory, target);
}

export async function prepare(raw, execute = run) {
  const destination = destinationSchema.parse(raw);
  if (process.platform === 'win32') throw new SafeError('This release supports macOS and Linux desktop only.');
  let identity, label;
  if (destination.provider === 'cloudflare-local') {
    const file = await workerDevFile(destination);
    const local = await prepare({ provider: 'env', file, name: destination.name }, execute);
    const scope = destination.environment ? `environment ${destination.environment}` : 'shared default';
    return Object.freeze({ ...local, worker: Object.freeze(destination), label: `Cloudflare Worker (local, ${scope}) / ${local.label}` });
  }
  if (destination.provider === 'env') {
    if (!path.isAbsolute(destination.file) || /[\r\n\0]/.test(destination.file)) throw new SafeError('Use an absolute dotenv path.');
    // Resolve OS aliases such as macOS /var and /tmp before presenting the plan.
    // The final file itself still must not be a symlink; the canonical path is
    // immutable for the lifetime of the form and is rechecked before saving.
    destination.file = path.join(await fs.realpath(path.dirname(destination.file)), path.basename(destination.file));
    await safeFile(destination.file); await gitGuard(destination.file, execute);
    identity = `Local OS user ${process.getuid?.() ?? 'current'}`;
    label = `${destination.file} → ${destination.name}`;
  } else if (destination.provider === 'github') {
    identity = await execute('gh', ['api', '--hostname', 'github.com', 'user', '--jq', '.login'], { capture: true });
    if (!/^[A-Za-z0-9-]+$/.test(identity)) throw new SafeError('Could not identify the GitHub account.');
    label = `github.com/${destination.repo} / ${destination.environment ? `environment ${destination.environment}` : 'repository Actions'} / ${destination.name}`;
  } else if (destination.provider === 'aws') {
    const region = destination.secretArn.split(':')[3];
    const data = JSON.parse(await execute('aws', ['sts', 'get-caller-identity', '--profile', destination.profile, '--region', region, '--output', 'json'], { capture: true }));
    if (typeof data.Arn !== 'string' || !/^\d{12}$/.test(data.Account)) throw new SafeError('Could not identify the AWS account.');
    identity = `${data.Arn} (profile ${destination.profile})`;
    label = destination.secretArn;
  } else {
    const data = JSON.parse(await execute('az', ['account', 'show', '--subscription', destination.subscription, '--query', '{id:id,tenant:tenantId,user:user.name}', '--output', 'json'], { capture: true }));
    if (![data.id, data.tenant, data.user].every(v => typeof v === 'string' && v.length)) throw new SafeError('Could not identify the Azure account.');
    identity = `${data.user} / tenant ${data.tenant} / subscription ${data.id}`;
    destination.subscription = data.id;
    label = `Azure Key Vault ${destination.vault} / ${destination.name} / subscription ${data.id}`;
  }
  if (identity.length > 1024) throw new SafeError('Unexpected identity response.');
  return Object.freeze({ destination: Object.freeze(destination), identity, label });
}

export async function save(plan, secret, execute = run) {
  if (typeof secret !== 'string' || !Buffer.byteLength(secret) || Buffer.byteLength(secret) > 65536 || /[\0\r]/.test(secret)) throw new SafeError('Enter 1–65,536 UTF-8 bytes without NUL or carriage returns.');
  const d = plan.destination;
  if (d.provider === 'env') {
    if (plan.worker && await workerDevFile(plan.worker) !== d.file) {
      throw new SafeError('Local Worker destination changed. Open a new form to review it.');
    }
    await safeFile(d.file); await gitGuard(d.file, execute);
    const lock = `${d.file}.golden-gate.lock`;
    let handle;
    try { handle = await fs.open(lock, 'wx', 0o600); }
    catch { throw new SafeError('Destination is busy. If a prior process crashed, review and remove its .golden-gate.lock file.'); }
    const temp = path.join(path.dirname(d.file), `.golden-gate-${randomUUID()}`);
    try {
      let text = '', before;
      try { const source = await fs.open(d.file, constants.O_RDONLY | constants.O_NOFOLLOW); try { before = await source.stat(); text = await source.readFile('utf8'); } finally { await source.close(); } }
      catch (err) { if (err.code !== 'ENOENT') throw err; }
      const output = updateDotenv(text, d.name, secret);
      const writer = await fs.open(temp, 'wx', 0o600);
      try { await writer.writeFile(output, 'utf8'); await writer.sync(); } finally { await writer.close(); }
      await safeFile(d.file);
      let after; try { after = await fs.stat(d.file); } catch (err) { if (err.code !== 'ENOENT') throw err; }
      if (Boolean(before) !== Boolean(after) || (before && (before.ino !== after.ino || before.mtimeMs !== after.mtimeMs || before.size !== after.size))) throw new SafeError('Destination changed during saving. No value was replaced.');
      await fs.rename(temp, d.file);
    } finally { await fs.unlink(temp).catch(() => {}); await handle.close(); await fs.unlink(lock).catch(() => {}); }
    return;
  }
  // Recheck identity before the write so a changed CLI login cannot silently redirect it.
  const current = await prepare(d, execute);
  if (current.identity !== plan.identity) throw new SafeError('Provider login changed. Open a new form to review the identity.');
  let command, args;
  if (d.provider === 'github') {
    command = 'gh'; args = ['secret', 'set', d.name, '--repo', `https://github.com/${d.repo}`, '--app', 'actions'];
    if (d.environment) args.push('--env', d.environment);
  } else if (d.provider === 'aws') {
    command = 'aws'; args = ['secretsmanager', 'put-secret-value', '--secret-id', d.secretArn, '--profile', d.profile, '--region', d.secretArn.split(':')[3], '--secret-string', 'file:///dev/stdin', '--client-request-token', randomUUID(), '--output', 'json'];
  } else {
    command = 'az'; args = ['keyvault', 'secret', 'set', '--vault-name', d.vault, '--subscription', d.subscription, '--name', d.name, '--file', '/dev/stdin', '--encoding', 'utf-8', '--output', 'none', '--only-show-errors'];
  }
  try { await execute(command, args, { input: secret }); }
  catch { throw new UncertainError('Provider write was not acknowledged. It may have succeeded. Check metadata before another attempt.'); }
}
