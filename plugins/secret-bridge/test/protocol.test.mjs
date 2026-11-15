import test from 'node:test';
import assert from 'node:assert/strict';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { createPublicKey, publicEncrypt, constants, randomBytes, createCipheriv } from 'node:crypto';

for (const entry of ['src/server.mjs', 'dist/server.mjs', 'isolated-release']) {
  test(`${entry}: actual MCP stdio discovery, resource and private capability`, async t => {
    const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'secret-bridge-protocol-'));
    let executable = fileURLToPath(new URL(`../${entry}`, import.meta.url));
    if (entry === 'isolated-release') {
      executable = path.join(dir, 'server.mjs');
      await fs.copyFile(new URL('../dist/server.mjs', import.meta.url), executable);
    }
    const transport = new StdioClientTransport({ command: process.execPath, args: [executable], cwd: dir, stderr: 'pipe' });
    let stderr = ''; transport.stderr?.on('data', data => stderr += data);
    const client = new Client({ name: 'secret-bridge-tests', version: '1.0.0' });
    t.after(async () => { await client.close(); await fs.rm(dir, { recursive: true, force: true }); });
    await client.connect(transport);
    const { tools } = await client.listTools();
    for (const tool of tools) {
      for (const flag of ['readOnlyHint', 'destructiveHint', 'openWorldHint']) {
        assert.equal(typeof tool.annotations?.[flag], 'boolean', `${tool.name} must declare ${flag}`);
      }
    }
    const submit = tools.find(tool => tool.name === 'submit_secret');
    assert.deepEqual(submit._meta.ui.visibility, ['app']); assert.ok(!('secret' in submit.inputSchema.properties));
    assert.ok(tools.every(tool => tool.outputSchema));
    const resource = await client.readResource({ uri: 'ui://secret-bridge/entry-v1.html' });
    assert.equal(resource.contents[0].mimeType, 'text/html;profile=mcp-app');
    assert.deepEqual(resource.contents[0]._meta.ui.csp.connectDomains, []);
    const opened = await client.callTool({ name: 'open_secret_entry', arguments: { destination: { provider: 'env', file: path.join(dir, '.env.local'), name: 'KEY' } } });
    assert.equal(opened.structuredContent.status, 'pending');
    assert.ok(opened._meta.secretBridge.publicKey);
    assert.ok(!JSON.stringify(opened.structuredContent).includes(opened._meta.secretBridge.token));
    assert.ok(!JSON.stringify(opened.content).includes(opened._meta.secretBridge.token));
    const status = await client.callTool({ name: 'secret_entry_status', arguments: { requestId: opened.structuredContent.requestId } });
    assert.equal(status.structuredContent.status, 'pending'); assert.equal(status._meta, undefined);
    const cancelled = await client.callTool({ name: 'cancel_secret_entry', arguments: { requestId: opened.structuredContent.requestId, token: opened._meta.secretBridge.token } });
    assert.equal(cancelled.structuredContent.status, 'cancelled');
    const next = await client.callTool({ name: 'open_secret_entry', arguments: { destination: { provider: 'env', file: path.join(dir, '.env.local'), name: 'KEY' } } });
    const session = next._meta.secretBridge, key = randomBytes(32), iv = randomBytes(12);
    const cipher = createCipheriv('aes-256-gcm', key, iv); cipher.setAAD(Buffer.from(session.requestId));
    const data = Buffer.concat([cipher.update(JSON.stringify({ token: session.token, confirmed: true, secret: 'synthetic-protocol-only' })), cipher.final(), cipher.getAuthTag()]);
    const encrypted = { requestId: session.requestId, iv: iv.toString('base64url'), ciphertext: data.toString('base64url'), wrappedKey: publicEncrypt({ key: createPublicKey({ key: session.publicKey, format: 'jwk' }), padding: constants.RSA_PKCS1_OAEP_PADDING, oaepHash: 'sha256' }, key).toString('base64url') };
    const saved = await client.callTool({ name: 'submit_secret', arguments: encrypted });
    assert.equal(saved.structuredContent.status, 'saved');
    assert.ok(!JSON.stringify(saved).includes('synthetic-protocol-only'));
    assert.equal(await fs.readFile(path.join(dir, '.env.local'), 'utf8'), "KEY='synthetic-protocol-only'\n");
    const replay = await client.callTool({ name: 'submit_secret', arguments: encrypted });
    assert.equal(replay.isError, true);
    assert.equal(stderr, '');
  });
}
