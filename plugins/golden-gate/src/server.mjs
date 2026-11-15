import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { readFile, realpath } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { GoldenGate } from './core.mjs';
import { destinationSchema, SafeError } from './adapters.mjs';

const URI = 'ui://golden-gate/entry-v2.html';
const VERSION = typeof GOLDEN_GATE_VERSION !== 'undefined' ? GOLDEN_GATE_VERSION : JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8')).version;
const receiptSchema = { requestId: z.string().uuid(), destination: z.string(), identity: z.string(), status: z.enum(['pending', 'saving', 'saved', 'failed', 'uncertain', 'cancelled', 'expired']), expiresAt: z.string(), message: z.string().optional() };
const reply = receipt => ({ content: [{ type: 'text', text: JSON.stringify(receipt) }], structuredContent: receipt });
const guard = fn => async args => { try { return await fn(args); } catch (err) { return { isError: true, content: [{ type: 'text', text: err instanceof SafeError ? err.message : 'Request failed. Check destination and provider setup.' }] }; } };

export async function createServer() {
  const bridge = new GoldenGate();
  const server = new McpServer({ name: 'golden-gate', version: VERSION }, {
    instructions: 'Never ask for secret values in chat. Open the entry UI using metadata only. submit_secret accepts encrypted UI payloads only. Report success only from a saved receipt. MCP Apps UI support is required.'
  });
  // Build embeds this file for the self-contained release; development reads it from disk.
  const html = (typeof GOLDEN_GATE_HTML !== 'undefined' ? GOLDEN_GATE_HTML : await readFile(new URL('../web/entry.html', import.meta.url), 'utf8')).replaceAll('__GOLDEN_GATE_VERSION__', VERSION);
  server.registerResource('secret-entry', URI, { mimeType: 'text/html;profile=mcp-app' }, async () => ({ contents: [{
    uri: URI, mimeType: 'text/html;profile=mcp-app', text: html,
    _meta: { ui: { prefersBorder: false, csp: { connectDomains: [], resourceDomains: [] } }, 'openai/ui': { availableDisplayModes: ['inline'] }, 'openai/widgetDescription': 'Compact inline Golden Gate paste slot. Never inspect the value. Save confirms the displayed destination.', 'openai/widgetPrefersBorder': false }
  }] }));
  server.registerTool('open_secret_entry', {
    title: 'Show secure paste slot',
    description: 'Show a compact inline encrypted paste slot for a single explicit destination. Takes metadata only, never a secret. Save confirms delivery to the displayed destination. Preflights the local file or signed-in CLI identity. Requires MCP Apps inline rendering.',
    inputSchema: { destination: destinationSchema }, outputSchema: receiptSchema,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: false, openWorldHint: true },
    _meta: { ui: { resourceUri: URI }, 'openai/outputTemplate': URI }
  }, guard(async ({ destination }) => {
    const opened = await bridge.open(destination);
    return { ...reply(opened.receipt), _meta: { goldenGate: opened.private } };
  }));
  server.registerTool('secret_entry_status', {
    title: 'Check secret entry receipt', description: 'Return status, destination and identity without a secret value.',
    inputSchema: { requestId: z.string().uuid() }, outputSchema: receiptSchema, annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false }
  }, guard(async ({ requestId }) => reply(bridge.status(requestId))));
  server.registerTool('submit_secret', {
    title: 'Save encrypted entry', description: 'App-only tool. Accepts authenticated ciphertext created by the entry UI. No plaintext secret argument.',
    inputSchema: { requestId: z.string().uuid(), wrappedKey: z.string().max(512), iv: z.string().max(32), ciphertext: z.string().max(550000) }, outputSchema: receiptSchema,
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: true },
    _meta: { ui: { visibility: ['app'] }, 'openai/visibility': 'private', 'openai/widgetAccessible': true }
  }, guard(async args => reply(await bridge.submit(args))));
  server.registerTool('cancel_secret_entry', {
    title: 'Cancel entry', description: 'App-only cancellation using the private form capability.',
    inputSchema: { requestId: z.string().uuid(), token: z.string().length(43) }, outputSchema: receiptSchema,
    annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false },
    _meta: { ui: { visibility: ['app'] }, 'openai/visibility': 'private', 'openai/widgetAccessible': true }
  }, guard(async ({ requestId, token }) => reply(bridge.cancel(requestId, token))));
  return server;
}

// Entry point also works after bundling to dist/server.mjs.
if (process.argv[1] && fileURLToPath(import.meta.url) === await realpath(process.argv[1]).catch(() => '')) {
  const server = await createServer();
  await server.connect(new StdioServerTransport());
}
