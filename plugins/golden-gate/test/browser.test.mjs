import test from 'node:test';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { GoldenGate } from '../src/core.mjs';

test('real browser iframe encrypts through bridge, saves and clears the form', async t => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'golden-gate-browser-'));
  const file = path.join(dir, '.env.local'), bridge = new GoldenGate();
  const opened = await bridge.open({ provider: 'env', file, name: 'TEST_KEY' });
  const toolResult = { structuredContent: opened.receipt, _meta: { goldenGate: opened.private } };
  const version = JSON.parse(await fs.readFile(new URL('../package.json', import.meta.url), 'utf8')).version;
  const html = (await fs.readFile(new URL('../web/entry.html', import.meta.url), 'utf8')).replaceAll('__GOLDEN_GATE_VERSION__', version);
  const transcript = [], receipts = [];
  const host = () => `<!doctype html><html><head><meta charset="utf-8"><title>Golden Gate test host</title></head><body style="background:#edf1f4;margin:40px"><iframe title="Secret entry" src="/entry" style="width:640px;height:760px;border:0"></iframe><script>
  window.bridgeMessages=[];const frame=document.querySelector('iframe');window.addEventListener('message',async event=>{if(event.source!==frame.contentWindow)return;const m=event.data;window.bridgeMessages.push(m);if(m.method==='ui/initialize'){event.source.postMessage({jsonrpc:'2.0',id:m.id,result:{protocolVersion:'2026-01-26',hostInfo:{name:'test-host',version:'1'},hostCapabilities:{}}},'*');}else if(m.method==='ui/notifications/initialized'){event.source.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:${JSON.stringify(toolResult).replaceAll('<', '\\u003c')}},'*');}else if(m.method==='tools/call'){const result=await fetch('/rpc',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(m.params)}).then(r=>r.json());event.source.postMessage({jsonrpc:'2.0',id:m.id,result},'*');}});</script></body></html>`;
  const server = createServer(async (req, res) => {
    if (req.url === '/entry') return res.writeHead(200, { 'content-type': 'text/html' }).end(html);
    if (req.url === '/rpc' && req.method === 'POST') {
      let body = ''; for await (const chunk of req) body += chunk;
      transcript.push(body); const call = JSON.parse(body);
      const receipt = call.name === 'submit_secret' ? await bridge.submit(call.arguments) : bridge.cancel(call.arguments.requestId, call.arguments.token);
      receipts.push(receipt);
      return res.writeHead(200, { 'content-type': 'application/json' }).end(JSON.stringify({ structuredContent: receipt }));
    }
    res.writeHead(200, { 'content-type': 'text/html' }).end(host());
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  t.after(async () => { await browser?.close(); await new Promise(resolve => server.close(resolve)); await fs.rm(dir, { recursive: true, force: true }); });
  browser = await chromium.launch({ executablePath: process.env.GOLDEN_GATE_TEST_BROWSER || (process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : undefined), headless: true });
  const page = await browser.newPage({ viewport: { width: 800, height: 900 } });
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  const network = [], consoleOutput = [], bridgeMessages = [];
  const origin = `http://127.0.0.1:${server.address().port}`;
  page.on('request', request => network.push({ url: request.url(), body: request.postData() }));
  page.on('console', message => consoleOutput.push(message.text()));
  // Fail on attempted external egress without sending even synthetic values to it.
  await page.route('**/*', route => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
  const snapshotChannels = async () => {
    bridgeMessages.push(...await page.evaluate(() => window.bridgeMessages));
    return frame.locator('body').evaluate(() => JSON.stringify({ local: { ...localStorage }, session: { ...sessionStorage } }));
  };
  await page.goto(origin);
  const frame = page.frameLocator('iframe');
  await frame.locator('#secret').waitFor({ state: 'visible' });
  assert.equal(await frame.locator('#modal').isVisible(), false);
  // Preview shows an empty test form, never a secret value.
  await page.screenshot({ path: process.env.GOLDEN_GATE_SCREENSHOT || new URL('../../../preview.png', import.meta.url).pathname });
  await frame.locator('#secret').fill('synthetic-browser-test-only');
  await frame.locator('#confirm').check();
  await frame.locator('#save').click();
  await frame.locator('#status').filter({ hasText: 'Saved.' }).waitFor();
  assert.equal(await fs.readFile(file, 'utf8'), "TEST_KEY='synthetic-browser-test-only'\n");
  assert.ok(transcript.length === 1); assert.ok(!transcript[0].includes('synthetic-browser-test-only'));
  assert.equal(await frame.locator('#secret').inputValue(), '');
  assert.equal(await frame.locator('#save').isDisabled(), true);
  assert.deepEqual(errors, []);
  const savedStorage = await snapshotChannels();
  // Fresh host/form exercises cancellation without writing a second value.
  const second = await bridge.open({ provider: 'env', file, name: 'UNUSED' });
  toolResult.structuredContent = second.receipt; toolResult._meta.goldenGate = second.private;
  await page.reload();
  await frame.locator('#destination').filter({ hasText: 'UNUSED' }).waitFor();
  await frame.locator('#secret').fill('synthetic-cancelled');
  await frame.locator('#cancel').click();
  await frame.locator('#status').filter({ hasText: 'cancelled' }).waitFor();
  assert.equal(bridge.status(second.receipt.requestId).status, 'cancelled');
  assert.equal(await frame.locator('#secret').inputValue(), '');
  assert.ok(!(await fs.readFile(file, 'utf8')).includes('UNUSED'));
  assert.equal(bridge.status(opened.receipt.requestId).status, 'saved');
  const cancelledStorage = await snapshotChannels();
  // Observe all outgoing messages, including any future ui/message or model-context
  // notification, rather than checking only tools/call's encrypted RPC body.
  const observedCalls = bridgeMessages.filter(message => message.method === 'tools/call');
  assert.deepEqual(observedCalls.map(message => message.params.name), ['submit_secret', 'cancel_secret_entry']);
  assert.equal(network.filter(request => request.url === `${origin}/rpc`).length, 2);
  assert.ok(network.every(request => new URL(request.url).origin === origin));
  const channels = JSON.stringify({ bridgeMessages, network, consoleOutput, receipts, savedStorage, cancelledStorage });
  for (const syntheticValue of ['synthetic-browser-test-only', 'synthetic-cancelled']) {
    assert.ok(!channels.includes(syntheticValue), 'Synthetic plaintext must not appear in observed bridge/network/console/receipt/storage channels');
  }
  assert.deepEqual(errors, []);
});
