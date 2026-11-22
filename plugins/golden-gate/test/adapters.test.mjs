import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { destinationSchema, prepare, save, run, updateDotenv, UncertainError } from '../src/adapters.mjs';

test('destination schemas reject injected flags and unknown secret fields', () => {
  assert.throws(() => destinationSchema.parse({ provider: 'github', repo: 'x/y', name: '--body', secret: 'synthetic' }));
  assert.throws(() => destinationSchema.parse({ provider: 'aws', profile: '--debug', secretArn: 'not-an-arn' }));
  assert.throws(() => destinationSchema.parse({ provider: 'azure', vault: '--debug', subscription: 'sub', name: 'key' }));
});
test('dotenv preserves unrelated entries and rejects ambiguous syntax', () => {
  const output = updateDotenv('# settings\nOTHER=value\nKEY=old\n', 'KEY', 'new#$"value\\path');
  assert.equal(output, '# settings\nOTHER=value\nKEY=\'new#$"value\\path\'\n');
  assert.throws(() => updateDotenv('KEY="old\nmultiline"\n', 'KEY', 'new'));
  assert.throws(() => updateDotenv('KEY=old\nKEY=duplicate\n', 'KEY', 'new'));
  assert.throws(() => updateDotenv('', 'KEY', 'multi\nline'));
  assert.throws(() => updateDotenv('', 'KEY', 'both\'"quotes'));
});
test('local save writes mode 0600, rejects symlinks, protects examples', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-test-')); t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const file = path.join(dir, '.env.local'), plan = await prepare({ provider: 'env', file, name: 'KEY' });
  await save(plan, 'synthetic-test-only');
  assert.equal(await fs.readFile(file, 'utf8'), "KEY='synthetic-test-only'\n");
  assert.equal((await fs.stat(file)).mode & 0o777, 0o600);
  await fs.symlink(file, path.join(dir, '.env.link'));
  await assert.rejects(prepare({ provider: 'env', file: path.join(dir, '.env.link'), name: 'KEY' }), /Symlink/);
  await assert.rejects(prepare({ provider: 'env', file: path.join(dir, '.env.example'), name: 'KEY' }), /example/);
});
test('Git dotenv guard refuses nonignored and tracked files', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-git-')); t.after(() => fs.rm(dir, { recursive: true, force: true }));
  await run('git', ['init', '-q', dir]);
  const destination = { provider: 'env', file: path.join(dir, '.env.local'), name: 'KEY' };
  await assert.rejects(prepare(destination), /Ignore/);
  await fs.writeFile(path.join(dir, '.gitignore'), '.env.local\n');
  const plan = await prepare(destination); await save(plan, 'synthetic');
  await run('git', ['add', '-f', '.env.local'], { cwd: dir });
  await assert.rejects(prepare(destination), /tracked/);
});
test('Git guard fails closed if Git is unavailable in a repository', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-closed-')); t.after(() => fs.rm(dir, { recursive: true, force: true }));
  await fs.mkdir(path.join(dir, '.git'));
  await assert.rejects(prepare({ provider: 'env', file: path.join(dir, '.env'), name: 'KEY' }, async () => { throw new Error(); }), /verify Git/);
});

test('local Worker routes are bound to the reviewed file and Git policy', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-worker-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const configFile = path.join(dir, 'wrangler.jsonc');
  await fs.writeFile(configFile, '{}');
  await run('git', ['init', '-q', dir]);
  const worker = { provider: 'cloudflare-local', configFile, name: 'SERVICE_KEY' };
  await assert.rejects(prepare(worker), /Ignore/);
  await fs.writeFile(path.join(dir, '.gitignore'), '.dev.vars*\n');
  const shared = await prepare(worker);
  assert.match(shared.label, /local, shared default/);
  const staging = { ...worker, environment: 'staging' };
  const pending = await prepare(staging);
  assert.match(pending.label, /local, environment staging.*\.dev\.vars\.staging/);
  await save(shared, 'synthetic-shared');
  await assert.rejects(save(pending, 'synthetic-stage'), /inherits/);
  const scopedFile = path.join(dir, '.dev.vars.staging');
  await assert.rejects(fs.stat(scopedFile), { code: 'ENOENT' });
  await fs.writeFile(scopedFile, 'OTHER=fixture\n');
  await save(await prepare(staging), 'synthetic-stage');
  assert.equal(await fs.readFile(scopedFile, 'utf8'), "OTHER=fixture\nSERVICE_KEY='synthetic-stage'\n");
  assert.equal(await fs.readFile(path.join(dir, '.dev.vars'), 'utf8'), "SERVICE_KEY='synthetic-shared'\n");
  await run('git', ['add', '-f', '.dev.vars.staging'], { cwd: dir });
  await assert.rejects(prepare(staging), /tracked/);
});

test('local Worker routing rejects shadowing dotenv, unsafe targets and cloud fields', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-worker-dotenv-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const configFile = path.join(dir, 'wrangler.toml');
  await fs.writeFile(configFile, '');
  const worker = { provider: 'cloudflare-local', configFile, name: 'SERVICE_KEY' };
  const plan = await prepare(worker);
  await fs.writeFile(path.join(dir, '.env.production'), 'OTHER=fixture\n');
  await prepare({ ...worker, environment: 'staging' });
  await assert.rejects(prepare({ ...worker, environment: 'production' }), /hide existing/);
  await fs.writeFile(path.join(dir, '.env.local'), 'OTHER=fixture\n');
  await assert.rejects(save(plan, 'synthetic'), /hide existing/);
  await assert.rejects(prepare(worker), /hide existing/);
  await fs.symlink('.env.local', path.join(dir, '.dev.vars'));
  await assert.rejects(prepare(worker), /Symlink/);
  await assert.rejects(prepare({ ...worker, environment: '../escape' }));
  await assert.rejects(prepare({ ...worker, configFile: 'wrangler.toml' }), /absolute/);
  await assert.rejects(prepare({ ...worker, configFile: path.join(dir, '.env.local') }), /Wrangler/);
  await assert.rejects(prepare({ ...worker, accountId: 'unwanted' }));
});
test('cloud adapters pass values only through stdin and suppress write output', async () => {
  const destinations = [
    { provider: 'github', repo: 'example/app', environment: 'staging', name: 'KEY' },
    { provider: 'aws', secretArn: 'arn:aws:secretsmanager:us-west-2:123456789012:secret:test-AbCdEf', profile: 'default' },
    { provider: 'azure', vault: 'test-vault', subscription: 'test-sub', name: 'service-key' },
  ];
  for (const destination of destinations) {
    const calls = [];
    const execute = async (command, args, options = {}) => {
      calls.push({ command, args, options });
      if (command === 'gh' && args[0] === 'api') return 'example-user';
      if (command === 'aws' && args[0] === 'sts') return JSON.stringify({ Account: '123456789012', Arn: 'arn:aws:iam::123456789012:user/test' });
      if (command === 'az' && args[0] === 'account') return JSON.stringify({ id: 'test-sub', tenant: 'test-tenant', user: 'test@example.invalid' });
      return '';
    };
    const plan = await prepare(destination, execute); await save(plan, 'synthetic-secret-only', execute);
    const write = calls.at(-1);
    assert.equal(write.options.input, 'synthetic-secret-only'); assert.ok(!write.args.join(' ').includes('synthetic-secret-only')); assert.equal(write.options.capture, undefined);
    if (destination.provider === 'aws') assert.ok(write.args.includes('file:///dev/stdin'));
    if (destination.provider === 'azure') assert.ok(write.args.includes('/dev/stdin'));
  }
});
test('identity changes block saving; write errors become uncertain', async () => {
  const destination = { provider: 'github', repo: 'example/app', name: 'KEY' };
  const plan = await prepare(destination, async () => 'first');
  await assert.rejects(save(plan, 'synthetic', async () => 'second'), /login changed/);
  await assert.rejects(save(plan, 'synthetic', async (_cmd, args) => { if (args[0] === 'api') return 'first'; throw new Error('synthetic-private-provider-output'); }), UncertainError);
});

test('invalid secret byte lengths and control characters never reach a provider', async () => {
  const plan = { destination: { provider: 'github', repo: 'example/app', name: 'KEY' }, identity: 'test' };
  for (const secret of ['', 'x'.repeat(65537), '🔐'.repeat(16385), 'synthetic\0value', 'synthetic\rvalue', null]) {
    await assert.rejects(save(plan, secret, async () => assert.fail('provider must not run')), /UTF-8 bytes/);
  }
});

test('a dotenv replaced by a symlink after review cannot redirect the write', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-recheck-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const file = path.join(dir, '.env.local'), other = path.join(dir, '.env.other');
  await fs.writeFile(file, 'KEY=before\n'); await fs.writeFile(other, 'KEY=untouched\n');
  const plan = await prepare({ provider: 'env', file, name: 'KEY' });
  await fs.unlink(file); await fs.symlink(other, file);
  await assert.rejects(save(plan, 'synthetic'), /Symlink/);
  assert.equal(await fs.readFile(other, 'utf8'), 'KEY=untouched\n');
});

test('hardlinked destinations and existing locks cannot replace a value', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-lock-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const file = path.join(dir, '.env.local'); await fs.writeFile(file, 'KEY=before\n');
  const plan = await prepare({ provider: 'env', file, name: 'KEY' });
  await fs.link(file, path.join(dir, '.env.link'));
  await assert.rejects(save(plan, 'synthetic'), /regular private file/);
  await fs.unlink(path.join(dir, '.env.link'));
  const lock = `${plan.destination.file}.golden-gate.lock`;
  await fs.writeFile(lock, 'existing-lock');
  await assert.rejects(save(plan, 'synthetic'), /busy/);
  assert.equal(await fs.readFile(file, 'utf8'), 'KEY=before\n');
  assert.equal(await fs.readFile(lock, 'utf8'), 'existing-lock');
});

test('parser failure preserves the original file and cleans its temporary lock', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-atomic-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const file = path.join(dir, '.env.local'), before = 'KEY=one\nKEY=two\n';
  await fs.writeFile(file, before);
  const plan = await prepare({ provider: 'env', file, name: 'KEY' });
  await assert.rejects(save(plan, 'synthetic'), /Duplicate/);
  assert.equal(await fs.readFile(file, 'utf8'), before);
  assert.deepEqual(await fs.readdir(dir), ['.env.local']);
});

test('provider subprocess failures and timeouts suppress stdout and stderr', async () => {
  await assert.rejects(run(process.execPath, ['-e', 'process.stdout.write("SYNTHETIC-PRIVATE"); process.stderr.write("SYNTHETIC-PRIVATE"); process.exit(1)']), err => {
    assert.ok(!err.message.includes('SYNTHETIC-PRIVATE')); return /Provider command failed/.test(err.message);
  });
  await assert.rejects(run(process.execPath, ['-e', 'setTimeout(() => {}, 10000)'], { timeout: 50 }), /timed out/);
});
