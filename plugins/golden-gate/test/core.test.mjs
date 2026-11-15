import test from 'node:test';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { GoldenGate } from '../src/core.mjs';
import { UncertainError } from '../src/adapters.mjs';

const destination = { provider: 'github', repo: 'example/app', name: 'SERVICE_KEY' };
const plan = { destination, label: 'example/app / SERVICE_KEY', identity: 'example-user' };
export async function envelope(session, secret, extra = {}) {
  const subtle = webcrypto.subtle;
  const publicKey = await subtle.importKey('jwk', session.publicKey, { name: 'RSA-OAEP', hash: 'SHA-256' }, false, ['encrypt']);
  const key = await subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt']);
  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const payload = Buffer.from(JSON.stringify({ token: session.token, confirmed: true, secret, ...extra }));
  return { requestId: session.requestId,
    wrappedKey: Buffer.from(await subtle.encrypt({ name: 'RSA-OAEP' }, publicKey, await subtle.exportKey('raw', key))).toString('base64url'),
    iv: Buffer.from(iv).toString('base64url'),
    ciphertext: Buffer.from(await subtle.encrypt({ name: 'AES-GCM', iv, additionalData: Buffer.from(session.requestId) }, key, payload)).toString('base64url') };
}

test('Web Crypto submission saves once and returns only a receipt', async () => {
  const calls = [];
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async (...args) => calls.push(args) });
  const opened = await bridge.open(destination), secret = 'synthetic-test-only-🔐\nsecond line';
  const encrypted = await envelope(opened.private, secret);
  assert.ok(!JSON.stringify(encrypted).includes(secret));
  const receipt = await bridge.submit(encrypted);
  assert.equal(receipt.status, 'saved'); assert.equal(calls.length, 1); assert.equal(calls[0][1], secret);
  assert.ok(!JSON.stringify(receipt).includes(secret)); assert.ok(!JSON.stringify(receipt).includes(opened.private.token));
  assert.equal(bridge.requests.get(receipt.requestId).privateKey, undefined);
  await assert.rejects(bridge.submit(encrypted), /no longer active/);
});
test('ciphertext tampering and missing consent cannot write', async () => {
  let writes = 0;
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => writes++ });
  const opened = await bridge.open(destination), encrypted = await envelope(opened.private, 'synthetic');
  const bytes = Buffer.from(encrypted.ciphertext, 'base64url'); bytes[0] ^= 1;
  await assert.rejects(bridge.submit({ ...encrypted, ciphertext: bytes.toString('base64url') }), /validation failed/);
  await assert.rejects(bridge.submit(await envelope(opened.private, 'synthetic', { confirmed: false })), /validation failed/);
  await assert.rejects(bridge.submit(await envelope(opened.private, 'synthetic', { token: 'x'.repeat(43) })), /validation failed/);
  assert.equal(writes, 0);
});
test('ciphertext is bound to the destination request', async () => {
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => assert.fail('unexpected save') });
  const a = await bridge.open(destination), b = await bridge.open(destination);
  const encrypted = await envelope(a.private, 'synthetic');
  await assert.rejects(bridge.submit({ ...encrypted, requestId: b.receipt.requestId }), /validation failed/);
});
test('cancelled and expired forms cannot write', async () => {
  let now = 1000;
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => assert.fail('unexpected save'), now: () => now });
  const opened = await bridge.open(destination), encrypted = await envelope(opened.private, 'synthetic');
  assert.throws(() => bridge.cancel(opened.receipt.requestId, 'bad'), /capability/);
  assert.equal(bridge.cancel(opened.receipt.requestId, opened.private.token).status, 'cancelled');
  await assert.rejects(bridge.submit(encrypted), /no longer active/);
  const next = await bridge.open(destination), nextEncrypted = await envelope(next.private, 'synthetic'); now += 300001;
  assert.equal(bridge.status(next.receipt.requestId).status, 'expired');
  await assert.rejects(bridge.submit(nextEncrypted), /no longer active/);
});
test('concurrent submissions cannot duplicate a write', async () => {
  let release, writes = 0;
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => { writes++; await new Promise(r => release = r); } });
  const opened = await bridge.open(destination), encrypted = await envelope(opened.private, 'synthetic');
  const first = bridge.submit(encrypted);
  await assert.rejects(bridge.submit(encrypted), /no longer active/); release(); await first; assert.equal(writes, 1);
});
test('cloud uncertainty and unexpected provider exceptions cannot leak values', async () => {
  for (const [error, status] of [[new UncertainError('Check destination metadata.'), 'uncertain'], [new Error('synthetic-secret-that-must-not-leak'), 'failed']]) {
    const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => { throw error; } });
    const opened = await bridge.open(destination);
    const result = await bridge.submit(await envelope(opened.private, 'synthetic-secret-that-must-not-leak'));
    assert.equal(result.status, status); assert.ok(!JSON.stringify(result).includes('synthetic-secret-that-must-not-leak'));
  }
});

test('expiry is enforced at the exact deadline and destroys the capability', async () => {
  let now = 1000, writes = 0;
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => writes++, now: () => now });
  const opened = await bridge.open(destination);
  const encrypted = await envelope(opened.private, 'synthetic');
  now = opened.private.expiresAt;
  await assert.rejects(bridge.submit(encrypted), /no longer active/);
  const state = bridge.requests.get(opened.receipt.requestId);
  assert.equal(bridge.status(opened.receipt.requestId).status, 'expired');
  assert.equal(state.privateKey, undefined); assert.equal(state.token, undefined);
  assert.equal(writes, 0);
});

test('malformed envelopes and extra decrypted fields fail closed without a write', async () => {
  let writes = 0;
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => writes++ });
  const opened = await bridge.open(destination);
  const encrypted = await envelope(opened.private, 'synthetic');
  for (const replacement of [{ wrappedKey: '!' }, { iv: 'AA' }, { ciphertext: 'AA' }, { ciphertext: 'A'.repeat(550001) }]) {
    await assert.rejects(bridge.submit({ ...encrypted, ...replacement }), /validation failed/);
  }
  for (const payload of [{ destination: { provider: 'github', repo: 'other/repo', name: 'KEY' } }, { secret: 42 }, { confirmed: 'true' }]) {
    await assert.rejects(bridge.submit(await envelope(opened.private, 'synthetic', payload)), /validation failed/);
  }
  assert.equal(writes, 0);
  assert.equal(bridge.cancel(opened.receipt.requestId, opened.private.token).status, 'cancelled');
});

test('in-flight status is nonmutating and cancellation cannot race a claimed write', async () => {
  let release, writes = 0;
  const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => { writes++; await new Promise(r => release = r); } });
  const opened = await bridge.open(destination);
  const saving = bridge.submit(await envelope(opened.private, 'synthetic'));
  assert.equal(bridge.status(opened.receipt.requestId).status, 'saving');
  assert.throws(() => bridge.cancel(opened.receipt.requestId, opened.private.token), /no longer active/);
  release();
  const receipt = await saving;
  assert.deepEqual(bridge.status(receipt.requestId), receipt);
  assert.deepEqual(bridge.status(receipt.requestId), receipt);
  assert.equal(writes, 1);
});

test('failed or uncertain writes are terminal and cannot be retried automatically', async () => {
  for (const error of [new Error('SYNTHETIC-PRIVATE'), new UncertainError('Check metadata before retrying.')]) {
    let writes = 0;
    const bridge = new GoldenGate({ prepareFn: async () => plan, saveFn: async () => { writes++; throw error; } });
    const opened = await bridge.open(destination), encrypted = await envelope(opened.private, 'synthetic');
    const receipt = await bridge.submit(encrypted);
    assert.ok(['failed', 'uncertain'].includes(receipt.status));
    await assert.rejects(bridge.submit(encrypted), /no longer active/);
    assert.equal(writes, 1);
    assert.equal(bridge.requests.get(receipt.requestId).token, undefined);
    assert.equal(bridge.requests.get(receipt.requestId).privateKey, undefined);
    assert.ok(!JSON.stringify(receipt).includes('SYNTHETIC-PRIVATE'));
  }
});
