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
