import { generateKeyPairSync, randomBytes, randomUUID, privateDecrypt, constants, createDecipheriv, timingSafeEqual } from 'node:crypto';
import { prepare, save, SafeError, UncertainError } from './adapters.mjs';

const decode = (value, max) => {
  if (typeof value !== 'string' || value.length > max || !/^[A-Za-z0-9_-]+$/.test(value)) throw new SafeError('Invalid encrypted submission.');
  return Buffer.from(value, 'base64url');
};
export class SecretBridge {
  constructor({ prepareFn = prepare, saveFn = save, now = Date.now } = {}) {
    this.prepareFn = prepareFn; this.saveFn = saveFn; this.now = now; this.requests = new Map();
  }
  async open(destination) {
    // Remove terminal/expired sessions, including their private keys and capabilities.
    for (const [id, r] of this.requests) if (r.expiresAt < this.now() - 300000) this.requests.delete(id);
    if (this.requests.size >= 50) throw new SafeError('Too many recent forms; wait for existing forms to expire.');
    const plan = await this.prepareFn(destination);
    const { publicKey, privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
    const requestId = randomUUID(), token = randomBytes(32).toString('base64url'), expiresAt = this.now() + 300000;
    const request = { plan, privateKey, token, expiresAt, status: 'pending' };
    request.timer = setTimeout(() => { if (request.status === 'pending') this.finish(request, 'expired'); }, 300000);
    request.timer.unref();
    this.requests.set(requestId, request);
    return { receipt: this.status(requestId), private: { requestId, token, expiresAt, label: plan.label, identity: plan.identity, publicKey: publicKey.export({ format: 'jwk' }) } };
  }
  status(id) {
    const r = this.requests.get(id);
    if (!r) throw new SafeError('Unknown entry request.');
    if (r.status === 'pending' && r.expiresAt <= this.now()) this.finish(r, 'expired');
    return { requestId: id, destination: r.plan.label, identity: r.plan.identity, status: r.status, expiresAt: new Date(r.expiresAt).toISOString(), ...(r.message ? { message: r.message } : {}) };
  }
  finish(r, status, message) { clearTimeout(r.timer); r.status = status; r.message = message; r.privateKey = undefined; r.token = undefined; }
  authorize(id, token) {
    const r = this.requests.get(id);
    this.status(id);
    if (r.status !== 'pending') throw new SafeError('This entry form is no longer active.');
    if (typeof token !== 'string' || token.length !== r.token.length || !timingSafeEqual(Buffer.from(token), Buffer.from(r.token))) throw new SafeError('Invalid form capability.');
    return r;
  }
  cancel(id, token) { const r = this.authorize(id, token); this.finish(r, 'cancelled'); return this.status(id); }
  async submit({ requestId, wrappedKey, iv, ciphertext }) {
    const r = this.requests.get(requestId);
    this.status(requestId);
    if (r.status !== 'pending') throw new SafeError('This entry form is no longer active.');
    let key, plaintext, payload;
    try {
      key = privateDecrypt({ key: r.privateKey, padding: constants.RSA_PKCS1_OAEP_PADDING, oaepHash: 'sha256' }, decode(wrappedKey, 512));
      const nonce = decode(iv, 32), data = decode(ciphertext, 550000);
      if (key.length !== 32 || nonce.length !== 12 || data.length < 16) throw new Error();
      const decipher = createDecipheriv('aes-256-gcm', key, nonce);
      decipher.setAAD(Buffer.from(requestId)); decipher.setAuthTag(data.subarray(-16));
      plaintext = Buffer.concat([decipher.update(data.subarray(0, -16)), decipher.final()]);
      payload = JSON.parse(plaintext.toString('utf8'));
      this.authorize(requestId, payload.token);
      if (payload.confirmed !== true || typeof payload.secret !== 'string' || Object.keys(payload).sort().join(',') !== 'confirmed,secret,token') throw new Error();
    } catch { throw new SafeError('Encrypted form validation failed.'); }
    finally { key?.fill(0); plaintext?.fill(0); }
    // Claim synchronously before any await; prevent concurrent and replayed writes.
    r.status = 'saving'; r.privateKey = undefined; r.token = undefined;
    try { await this.saveFn(r.plan, payload.secret); this.finish(r, 'saved'); }
    catch (err) { this.finish(r, err instanceof UncertainError ? 'uncertain' : 'failed', err instanceof SafeError ? err.message : 'Saving failed. No provider output is exposed.'); }
    finally { payload.secret = ''; payload.token = ''; }
    return this.status(requestId);
  }
}
