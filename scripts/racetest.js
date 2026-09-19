const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');

function installProbe(menu) {
  const originalRandom = Math.random;
  const originalTimeout = window.setTimeout;
  let recording = false;
  let origin = 0;
  let activeClick = null;
  let lastResultRequestId = null;
  let frameId;
  let previousFrameKey;
  let framesSampled = 0;
  let observer;
  const clicks = [];
  const completions = [];
  const domStates = [];
  const frameStates = [];
  const now = () => Number((performance.now() - origin).toFixed(3));

  function snapshot() {
    const box = document.querySelector('.lunch-display');
    const dish = document.querySelector('.food-name').textContent;
    const iconClass = document.querySelector('.food-icon i')?.className ?? null;
    const entry = menu.find(item => item.name === dish);
    const loading = dish === 'Thinking...' && iconClass === 'fas fa-spinner fa-spin';
    const style = getComputedStyle(box);
    const opacity = Number(style.opacity);
    return {
      atMs: now(), dish, iconClass,
      phase: loading ? 'loading' : 'result',
      sameMenuEntry: loading ? null : Boolean(entry && entry.icon === iconClass),
      sourceRequestId: loading ? null : lastResultRequestId,
      latestRequestId: clicks.length || null,
      stale: !loading && lastResultRequestId !== null && lastResultRequestId < clicks.length,
      opacity,
      visible: style.display !== 'none' && style.visibility === 'visible' && opacity > 0,
    };
  }

  window.addEventListener('click', event => {
    if (!recording || !event.target.closest('#generateBtn')) return;
    const requestId = clicks.length + 1;
    activeClick = requestId;
    clicks.push({ requestId, atMs: now(), trusted: event.isTrusted, randomDraws: [] });
  }, true);
  window.addEventListener('click', () => { activeClick = null; });

  // Observe the native random draw without substituting or seeding its value.
  Math.random = function () {
    const value = originalRandom();
    if (recording && activeClick !== null) {
      const request = clicks[activeClick - 1];
      request.randomDraws.push(value);
      request.selectedIndex = Math.floor(value * menu.length);
      request.selectedEntry = menu[request.selectedIndex];
    }
    return value;
  };

  // Preserve the callback, delay, arguments, and native scheduling order.
  window.setTimeout = function (callback, delay, ...args) {
    if (!recording || activeClick === null || delay !== 500 || typeof callback !== 'function') {
      return originalTimeout.call(window, callback, delay, ...args);
    }
    const request = clicks[activeClick - 1];
    request.timerScheduledAtMs = now();
    request.timerDelayMs = delay;
    return originalTimeout.call(window, function (...callbackArgs) {
      const firedAtMs = now();
      callback.apply(this, callbackArgs);
      lastResultRequestId = request.requestId;
      completions.push({ requestId: request.requestId, firedAtMs, state: snapshot() });
    }, delay, ...args);
  };

  function sampleFrame() {
    if (!recording) return;
    framesSampled += 1;
    const state = snapshot();
    // Ignore opacity-only animation steps; retain changes to the visible content or visibility.
    const key = JSON.stringify([state.dish, state.iconClass, state.visible]);
    if (key !== previousFrameKey) {
      frameStates.push({ frame: framesSampled, ...state });
      previousFrameKey = key;
    }
    frameId = requestAnimationFrame(sampleFrame);
  }

  window.__raceProbe = {
    completions,
    arm() {
      origin = performance.now();
      recording = true;
      const beforeBurst = snapshot();
      domStates.push({ cause: 'before-burst', ...beforeBurst });
      frameStates.push({ frame: 0, ...beforeBurst });
      previousFrameKey = JSON.stringify([beforeBurst.dish, beforeBurst.iconClass, beforeBurst.visible]);
      observer = new MutationObserver(records => {
        domStates.push({ cause: 'mutation-batch', mutationCount: records.length, ...snapshot() });
      });
      observer.observe(document.querySelector('.lunch-display'), {
        childList: true, subtree: true, characterData: true, attributes: true,
      });
      frameId = requestAnimationFrame(sampleFrame);
    },
    stop() {
      const finalState = snapshot();
      recording = false;
      observer.disconnect();
      cancelAnimationFrame(frameId);
      Math.random = originalRandom;
      window.setTimeout = originalTimeout;
      return { clicks, completions, domStates, frameStates, framesSampled, finalState };
    },
  };
}

async function main() {
  const baselinePath = path.join(root, 'baseline/index.html');
  const baseline = await fs.readFile(baselinePath);
  const menuSource = baseline.toString('utf8').match(/const lunchMenu = \[([\s\S]*?)\];/);
  assert(menuSource, 'Missing lunchMenu');
  const menu = [...menuSource[1].matchAll(/\{\s*name:\s*"([^"]+)",\s*icon:\s*"([^"]+)"\s*\}/g)]
    .map(([, name, icon]) => ({ name, icon }));
  assert.equal(menu.length, 12);

  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('requestfailed', request => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
    await page.addInitScript(installProbe, menu);
    await page.goto(pathToFileURL(baselinePath).href, { waitUntil: 'load' });
    // Exclude the automatic page-load request and let its animation finish.
    await page.waitForFunction(() =>
      !["What's for lunch?", 'Thinking...'].includes(document.querySelector('.food-name').textContent));
    await page.waitForFunction(() => document.querySelector('.lunch-display').getAnimations()
      .every(animation => animation.playState === 'finished'));
    const fontState = await page.evaluate(async () => {
      await document.fonts.ready;
      return {
        stylesheetLoaded: document.querySelector('link[rel="stylesheet"]').sheet !== null,
        solidFontLoaded: [...document.fonts].some(font =>
          font.family.replace(/["']/g, '') === 'Font Awesome 6 Free' &&
          font.weight === '900' && font.status === 'loaded'),
      };
    });
    assert(fontState.stylesheetLoaded && fontState.solidFontLoaded, 'Font assets did not load');
    const button = await page.locator('#generateBtn').boundingBox();
    assert(button);
    const x = button.x + button.width / 2;
    const y = button.y + button.height / 2;
    await page.mouse.move(x, y);
    await page.evaluate(() => window.__raceProbe.arm());
    for (let index = 0; index < 5; index += 1) {
      await page.mouse.click(x, y);
      if (index < 4) await page.waitForTimeout(45);
    }
    await page.waitForFunction(() => window.__raceProbe.completions.length === 5);
    await page.waitForTimeout(600);
    const trace = await page.evaluate(() => window.__raceProbe.stop());
    assert.equal(trace.clicks.length, 5);
    const clickSpanMs = Number((trace.clicks[4].atMs - trace.clicks[0].atMs).toFixed(3));
    assert(clickSpanMs < 300, `Burst exceeded 300 ms: ${clickSpanMs}`);
    assert(trace.clicks.every(click => click.trusted && click.randomDraws.length === 1));
    assert.equal(trace.completions.length, 5);
    assert.deepEqual(errors, []);

    // Visible content changes, excluding the pre-burst state and invisible animation frames.
    const visibleStates = trace.frameStates.filter(state => state.visible);
    const visibleTransitions = visibleStates.filter((state, index) => index > 0 &&
      (state.dish !== visibleStates[index - 1].dish || state.iconClass !== visibleStates[index - 1].iconClass));
    const visibleResults = visibleTransitions.filter(state => state.phase === 'result');
    const mismatches = trace.domStates.filter(state => state.sameMenuEntry === false);
    const unrequestedCompletions = trace.completions.filter(completion => {
      const request = trace.clicks[completion.requestId - 1];
      return completion.state.dish !== request.selectedEntry.name ||
        completion.state.iconClass !== request.selectedEntry.icon;
    });
    assert.equal(mismatches.length, 0, 'Observed a mismatched dish/icon pair');
    assert.equal(unrequestedCompletions.length, 0, 'Result differs from its originating request');
    assert.equal(trace.finalState.sourceRequestId, 5);

    const report = {
      source: 'baseline/index.html',
      sourceSha256: createHash('sha256').update(baseline).digest('hex'),
      playwrightVersion: require('playwright/package.json').version,
      browser: { name: 'Chromium', version: browser.version(), headless: true },
      method: {
        input: 'Five trusted Playwright mouse clicks, with 45 ms waits between clicks; actual span asserted below 300 ms.',
        startup: 'Automatic page-load result and fade-in finish before the probe is armed.',
        clock: 'performance.now(), milliseconds since probe arm, rounded to 0.001 ms.',
        instrumentation: 'Native Math.random values are observed, not changed. Native 500 ms callbacks retain their original delay, arguments, and scheduling order.',
        dom: 'MutationObserver records every delivered mutation batch after synchronous app updates.',
        frames: 'requestAnimationFrame samples dish, icon, and visibility every frame; frameStates stores changes. These are pre-render samples, not a compositor paint-event count.',
        repaints: 'Visible dish/icon content transitions; continuous spinner/fade animation paints are excluded. Repeated identical results may not add a content transition.',
        sameMenuEntry: 'true/false for a result; null for the intentional Thinking.../spinner loading state.',
      },
      menu,
      fontState,
      summary: {
        clickCount: trace.clicks.length,
        clickSpanMs,
        timerCompletions: trace.completions.length,
        visibleContentTransitions: visibleTransitions.length,
        visibleLoadingTransitions: visibleTransitions.filter(state => state.phase === 'loading').length,
        visibleResultTransitions: visibleResults.length,
        staleTimerCompletions: trace.completions.filter(completion => completion.state.stale).length,
        staleVisibleResultTransitions: visibleResults.filter(state => state.stale).length,
        mismatchedMenuPairs: mismatches.length,
        resultsWithoutAnOriginatingClick: unrequestedCompletions.length,
        finalResultRequestId: trace.finalState.sourceRequestId,
        interpretation: 'Earlier requested results can appear after newer clicks have superseded them. Every result still belongs to an actual click; its icon and name update together. With equal 500 ms delays, the latest click supplies the final result.',
      },
      visibleTransitions,
      ...trace,
      errors,
    };
    await fs.writeFile(path.join(root, 'evidence/05-race.json'), `${JSON.stringify(report, null, 2)}\n`);
    console.table(trace.clicks.map(({ requestId, atMs, selectedEntry }) => ({ requestId, atMs, selectedDish: selectedEntry.name })));
    console.table(visibleTransitions.map(({ atMs, dish, iconClass, sameMenuEntry, sourceRequestId, stale }) =>
      ({ atMs, dish, iconClass, sameMenuEntry, sourceRequestId, stale })));
    console.log(JSON.stringify(report.summary, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
