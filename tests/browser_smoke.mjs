// Optional rendered-browser audit. Install test-only dependencies under ignored .cache/browser.
// npm install --prefix .cache/browser --no-save --package-lock=false @sparticuz/chromium playwright-core
import chromium, { inflate, setupLambdaEnvironment } from '../.cache/browser/node_modules/@sparticuz/chromium/build/index.js';
import { chromium as playwright } from '../.cache/browser/node_modules/playwright-core/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const base = process.env.PREVIEW_URL || 'http://127.0.0.1:8000';
// The sandbox lacks NSS/NSPR; use the test package's bundled runtime libraries.
await inflate(new URL('../.cache/browser/node_modules/@sparticuz/chromium/bin/al2023.tar.br', import.meta.url).pathname);
setupLambdaEnvironment('/tmp/al2023/lib');
const browser = await playwright.launch({ executablePath: await chromium.executablePath(), args: chromium.args, headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const routes = ['index.html','executive-summary.html','research.html','evidence.html',
  ...[24,25,27,28,30,31,32,33,36].map(n => `sites/GEMSDOE${n}.html`)];
const results = [];
try {
  for (const route of routes) {
    const response = await page.goto(`${base}/${route}`, { waitUntil: 'domcontentloaded' });
    assert.equal(response.status(), 200);
    await page.locator('h1').waitFor();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    assert.equal(overflow, false, `${route}: page-wide overflow`);
    const brokenImages = await page.locator('img').evaluateAll(images => images.some(image => !image.complete || !image.naturalWidth));
    assert.equal(brokenImages, false);
    results.push({ route, status: response.status(), page_wide_overflow: overflow, title: await page.title() });
  }
  await page.goto(`${base}/index.html`);
  // 2026-10-31: the executive table now carries 9 historical rows + 2 generated rows
  // (this session's H-REGAVOID file, verdict NOT OK, and the standing H-TVGB candidate, OK).
  assert.equal(await page.locator('tbody tr').count(), 11);
  // 2026-10-31: a negative verdict renders disabled download buttons (hero + release card)
  // instead of active CTAs for the NOT OK file; the standing candidate keeps its active link.
  assert.equal(await page.locator('button:disabled').count(), 2);
  assert.equal(await page.locator('a.button[href*="regavoid"][download]').count(), 0);
  await page.screenshot({ path: '.cache/desktop-preview.png', fullPage: true });
  await page.setViewportSize({ width: 375, height: 812 });
  for (const route of ['index.html','executive-summary.html','sites/GEMSDOE32.html','evidence.html']) {
    await page.goto(`${base}/${route}`, { waitUntil: 'domcontentloaded' });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `mobile overflow: ${route}`);
  }
  await page.goto(`${base}/index.html`);
  await page.screenshot({ path: '.cache/mobile-preview.png', fullPage: true });
  assert.deepEqual(errors, []);
  fs.writeFileSync('evidence/browser_checks.json', JSON.stringify({
    checked_utc: new Date().toISOString(), browser: await browser.version(),
    desktop_viewport: [1440,1000], mobile_viewport: [375,812],
    pages: results, mobile_pages_checked: 4, page_errors: errors,
    disabled_submission_button: true, total_executive_rows: 11, historical_rows: 9,
    screenshot_paths: ['.cache/desktop-preview.png','.cache/mobile-preview.png'],
    scope: 'Rendered UI/navigation and page-wide overflow. Not competition acceptance, scientific validation or score confirmation.'
  }, null, 2) + '\n');
  console.log('PASS: 13 rendered desktop pages; 4 mobile layouts; no page errors; no horizontal page overflow; blocked download explicit; executive table 11 rows (9 historical + 2 generated).');
} finally { await browser.close(); }
