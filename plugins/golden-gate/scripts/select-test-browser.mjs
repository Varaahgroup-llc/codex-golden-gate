import { chromium } from 'playwright';
import { appendFileSync } from 'node:fs';
if (!process.env.GITHUB_ENV) throw new Error('GITHUB_ENV is required in CI.');
appendFileSync(process.env.GITHUB_ENV, 'GOLDEN_GATE_TEST_BROWSER=' + chromium.executablePath() + '\n');
