const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const evidence = path.join(root, 'evidence');
const stylesheetUrl = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const escapeHtml = value => value.replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

// This function also runs when the generated HTML is opened independently.
async function measureIcons() {
  // Trigger layout/font discovery before awaiting the FontFaceSet.
  document.body.getBoundingClientRect();
  await document.fonts.ready;

  const items = [...document.querySelectorAll('.cell')].map((cell, index) => {
    const el = cell.querySelector('.glyph');
    const content = getComputedStyle(el, '::before').content;
    const width = el.getBoundingClientRect().width;
    const blank = content === 'none' || width === 0;
    cell.classList.toggle('blank', blank);
    cell.querySelector('.status').textContent = blank ? 'BLANK' : 'GLYPH';
    const codePoints = content === 'none' ? 'none' : [...content.replace(/^"|"$/g, '')]
      .map(char => `U+${char.codePointAt(0).toString(16).toUpperCase()}`).join(' ');
    cell.querySelector('.measurement').textContent = `${codePoints} · width ${width}px`;
    return {
      index: index + 1,
      dish: cell.dataset.dish,
      iconClass: cell.dataset.iconClass,
      content,
      width,
      blank,
    };
  });

  const total = items.length;
  const blankCount = items.filter(item => item.blank).length;
  const renderedCount = total - blankCount;
  document.querySelector('#summary').textContent =
    `${renderedCount}/${total} render a glyph · ${blankCount}/${total} blank (${100 * blankCount / total}%)`;
  return {
    total,
    renderedCount,
    blankCount,
    blankRate: { numerator: blankCount, denominator: total },
    items,
    stylesheetLoaded: document.querySelector('link[rel="stylesheet"]').sheet !== null,
    fonts: [...document.fonts].map(font => ({
      family: font.family, weight: font.weight, status: font.status,
    })),
  };
}

async function main() {
  const baseline = await fs.readFile(path.join(root, 'baseline/index.html'));
  const source = baseline.toString('utf8');
  const loadedStylesheet = source.match(/<link\s+rel="stylesheet"\s+href="([^"]+)"/);
  assert.equal(loadedStylesheet?.[1], stylesheetUrl, 'Baseline stylesheet changed');
  const menu = source.match(/const lunchMenu = \[([\s\S]*?)\];/);
  assert(menu, 'Could not find lunchMenu');
  const items = [...menu[1].matchAll(/\{\s*name:\s*"([^"]+)",\s*icon:\s*"([^"]+)"\s*\}/g)]
    .map(([, dish, iconClass]) => ({ dish, iconClass }));
  assert.equal(items.length, 12, 'Expected all 12 menu items');
  assert.equal(new Set(items.map(item => item.dish)).size, 12, 'Duplicate menu entries');

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Font Awesome 6.4.0 — all 12 lunch icons</title>
  <link rel="stylesheet" href="${escapeHtml(stylesheetUrl)}">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; padding: 36px; background: #f4f6fa; color: #17243a; font-family: Arial, sans-serif; }
    main { max-width: 1128px; margin: auto; }
    h1 { margin: 0 0 12px; font-size: 30px; }
    p { line-height: 1.5; }
    .subtitle { margin: 0 0 14px; color: #526079; }
    #summary { padding: 14px 18px; border-radius: 10px; background: #17243a; color: white; font-size: 20px; font-weight: bold; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
    .cell { min-height: 240px; padding: 18px 10px; text-align: center; background: white; border: 2px solid #d7e0eb; border-radius: 12px; }
    .cell.blank { border-color: #b42318; background: #fff1ef; }
    .slot { height: 82px; display: grid; place-items: center; }
    .glyph { font-size: 64px; color: #ff6b6b; }
    h2 { margin: 10px 0 8px; font-size: 21px; }
    code { font-size: 13px; }
    .status { display: table; margin: 12px auto 8px; padding: 4px 9px; border-radius: 5px; font-size: 12px; font-weight: bold; background: #e6f4ed; color: #14673c; }
    .blank .status { background: #fee0dc; color: #b42318; }
    .measurement { margin: 0; font-size: 12px; color: #526079; }
    footer { margin-top: 20px; font-size: 13px; line-height: 1.6; color: #526079; }
  </style>
</head>
<body>
  <main>
    <h1>Lunch icon catalogue · Font Awesome 6.4.0</h1>
    <p class="subtitle">All 12 entries from baseline/index.html, in source order. Measured after document.fonts.ready.</p>
    <p id="summary">Waiting for fonts and measurements…</p>
    <div class="grid">
${items.map(({ dish, iconClass }) => `      <section class="cell" data-dish="${escapeHtml(dish)}" data-icon-class="${escapeHtml(iconClass)}">
        <div class="slot"><i class="glyph ${escapeHtml(iconClass)}" aria-hidden="true"></i></div>
        <h2>${escapeHtml(dish)}</h2>
        <code>${escapeHtml(iconClass)}</code>
        <span class="status">PENDING</span>
        <p class="measurement"></p>
      </section>`).join('\n')}
    </div>
    <footer>Red cells: ::before content === 'none' or icon width === 0.<br>
    Complete deterministic enumeration; uniform selection makes the blank fraction the exact per-recommendation blank rate.</footer>
  </main>
  <script>
    window.auditReady = (${measureIcons.toString()})();
  </script>
</body>
</html>
`;
  await fs.mkdir(evidence, { recursive: true });
  const htmlPath = path.join(evidence, '03-icon-sheet.html');
  await fs.writeFile(htmlPath, html);

  const browser = await chromium.launch({ headless: true });
  try {
    const viewport = { width: 1200, height: 1100 };
    const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('requestfailed', request => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
    const [stylesheetResponse] = await Promise.all([
      page.waitForResponse(response => response.url() === stylesheetUrl),
      page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' }),
    ]);
    assert(stylesheetResponse.ok(), `Stylesheet HTTP ${stylesheetResponse.status()}`);
    const measurements = await page.evaluate(() => window.auditReady);
    assert(measurements.stylesheetLoaded, 'Stylesheet did not load');
    assert(measurements.fonts.some(font =>
      font.family.replace(/["']/g, '') === 'Font Awesome 6 Free' &&
      font.weight === '900' && font.status === 'loaded'), 'Solid icon font did not load');
    assert.equal(measurements.total, items.length);
    assert.deepEqual(measurements.items.map(({ dish, iconClass }) => ({ dish, iconClass })), items);
    assert.deepEqual(errors, [], 'Browser/runtime or network failures');

    const report = {
      source: 'baseline/index.html',
      sourceSha256: sha256(baseline),
      stylesheetUrl,
      stylesheetSha256: sha256(await stylesheetResponse.body()),
      playwrightVersion: require('playwright/package.json').version,
      browser: { name: 'Chromium', version: browser.version(), headless: true, viewport, deviceScaleFactor: 1 },
      method: 'Enumerate all menu items once in source order; measure after document.fonts.ready.',
      blankCriterion: "content === 'none' || width === 0",
      ...measurements,
      errors,
    };
    await page.screenshot({ path: path.join(evidence, '03-icon-sheet.png'), fullPage: true });
    await fs.writeFile(path.join(evidence, '03-icon-measurements.json'), `${JSON.stringify(report, null, 2)}\n`);
    console.table(measurements.items);
    console.log(`${measurements.renderedCount}/${measurements.total} render a glyph.`);
    console.log(`Exact blank rate: ${measurements.blankCount}/${measurements.total} (${100 * measurements.blankCount / measurements.total}%).`);
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
