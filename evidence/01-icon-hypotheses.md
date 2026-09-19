# Icon hypotheses — before the formal audit

I inspected `baseline/index.html` and checked the exact Font Awesome stylesheet it loads. **No files were changed.**

Two different problems are already apparent:
- **Missing definitions:** `fa-bowl-hot`, `fa-pasta`, and `fa-bowl` are absent from that stylesheet.
- **Questionable dish–icon mappings:** for example, Tacos uses a spoon and Steak uses a drumstick. These can render successfully while still looking wrong.

Below are the distinct failure modes worth checking. **Terminal** commands run from the project folder. **Console** commands run in the browser’s DevTools with the page open.

## 1. The requested icon is unavailable in the loaded library

**On screen:** Certain dishes have a name but no icon, even though other recommendations work.

Possible underlying causes include a misspelled name, an icon from another version, or an icon excluded from the loaded edition. Absence from this stylesheet alone does not distinguish those causes.

**Cheapest definitive check against the actual stylesheet — Terminal:**

```bash
python3 - <<'PY'
from pathlib import Path
from urllib.request import urlopen
import re

html = Path("baseline/index.html").read_text()
url = re.search(r'<link rel="stylesheet" href="([^"]+)"', html)[1]
css = urlopen(url).read().decode()
for dish, classes in re.findall(r'{ name: "([^"]+)", icon: "([^"]+)" }', html):
    icon = classes.split()[-1]
    found = re.search(r'\.' + re.escape(icon) + r'::?before\b', css)
    print(f'{dish:10} {icon:22} {"PRESENT" if found else "ABSENT"}')
PY
```

**Already confirmed:** Ramen, Pasta, and Soup request absent definitions. Legacy-looking names such as `fa-hamburger` and `fa-utensil-spoon` **are present**.

## 2. The icon depicts the wrong food

**On screen:** A clear, recognizable symbol contradicts the dish name—for example, a drumstick beside “Steak.”

**Cheapest check of the assigned mappings — Terminal:**

```bash
python3 - <<'PY'
from pathlib import Path
import re
html = Path("baseline/index.html").read_text()
for name, icon in re.findall(r'{ name: "([^"]+)", icon: "([^"]+)" }', html):
    print(f"{name}: {icon}")
PY
```

This confirms that **Tacos → spoon** and **Steak → drumstick** are intentional data assignments, rather than a rendering mix-up. Whether a depiction is appropriate requires visual judgment.

## 3. The icon is related to the dish but too generic or ambiguous

**On screen:** “Sushi” gets a fish, “Salad” a leaf, “Sandwich” a bread slice, “Curry” a mortar and pestle, or “BBQ” a flame. The user sees an ingredient, tool, or cooking method rather than the actual dish.

**Cheapest check:** Run the mapping command in **#2**.

This is distinct from a contradictory icon: a fish is related to sushi, but may still fail to communicate “sushi.” A command can establish the mapping; it cannot establish whether users understand it.

## 4. The stylesheet does not load at all

**On screen:** Most or all icons disappear, including the heading’s utensils, the button’s random symbol, and the loading spinner.

**Cheapest browser check — Console:**

```javascript
[...document.querySelectorAll('link[rel="stylesheet"]')].map(l => ({
  url: l.href,
  loaded: l.sheet !== null
}))
```

`loaded: false` after the page finishes loading indicates that the stylesheet is unavailable to the page. Inspect the failed Network request for the specific cause: connectivity, blocking, CSP, or an HTTP error.

## 5. The stylesheet loads, but the icon font fails to load

**On screen:** Empty squares, missing-glyph boxes, or blank spaces appear where icons should be. Several otherwise valid icons are affected.

**Cheapest active font-load check — Console:**

```javascript
await document.fonts.load('900 64px "Font Awesome 6 Free"')
```

- A rejected promise indicates a font-loading failure.
- An empty array means no matching font face was found.
- Returned faces with `status: "loaded"` establish that the matching font loaded.

CSS availability and font availability are separate checks: the stylesheet points to additional font resources.

## 6. The browser applies the wrong glyph, font family, or weight

**On screen:** A valid icon class produces an unrelated symbol, a box, or the wrong visual style. This can result from CSS overrides, competing library versions, or a mismatched font asset.

**Cheapest check of the rendered icon — Console:**

```javascript
(() => {
  const i = document.querySelector('.food-icon i');
  const s = getComputedStyle(i, '::before');
  return {
    classes: i.className,
    glyph: s.content,
    font: s.fontFamily,
    weight: s.fontWeight,
    stylesheets: [...document.styleSheets].map(s => s.href)
  };
})()
```

For a valid recommendation, expect a defined glyph, **Font Awesome 6 Free**, and weight **900**. `none` or `normal` content points toward a missing/overridden icon definition. Unexpected stylesheet URLs or font values identify a different problem.

## 7. The icon exists but is visually hidden, clipped, tiny, or hard to see

**On screen:** The name is readable, but the icon is invisible, cropped, misplaced, oversized, or blends into the background.

**Cheapest style-and-layout check — Console:**

```javascript
(() => {
  const i = document.querySelector('.food-icon i');
  return [i, i.parentElement, document.querySelector('.lunch-display')].map(e => {
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    return {
      element: e.className,
      display: s.display, visibility: s.visibility, opacity: s.opacity,
      size: s.fontSize, color: s.color, background: s.backgroundColor,
      overflow: s.overflow,
      x: r.x, y: r.y, width: r.width, height: r.height
    };
  });
})()
```

Run this while the problem is visible, at the affected window size or zoom. Zero dimensions, hidden visibility, zero opacity, or clipping provide concrete evidence; perceived contrast still needs visual inspection.

## 8. A placeholder or spinner is mistaken for the recommendation—or never goes away

**On screen:** A question mark remains beside “What’s for lunch?”, or a spinner remains beside “Thinking...”.

**Cheapest check — Console:**

```javascript
setTimeout(() => console.log({
  dish: document.querySelector('.food-name').textContent,
  icon: document.querySelector('.food-icon i').className
}), 1500)
```

Normally, this page replaces the loading state after **500 ms**. A persistent question mark suggests initialization did not complete; a persistent spinner suggests the callback did not complete. Check Console errors to identify why.

## 9. The icon and name belong to different recommendations

**On screen:** “Pizza” appears beside another dish’s icon, even though the configured Pizza mapping is correct.

**Cheapest check during the suspected mismatch — Console:**

```javascript
({
  dish: document.querySelector('.food-name').textContent,
  icon: document.querySelector('.food-icon i').className
})
```

Compare this pair with **#2**.

**Source finding:** The current callback assigns both from the same `selectedLunch` object, synchronously. A pairing mismatch is therefore not explained by the normal update path; it would need evidence from the running page.

## 10. Rapid clicks cause intermediate results or apparent flickering

**On screen:** A recommendation appears too soon after the latest click, then changes again without another click. The icon/name pair can remain correct while the timing feels wrong.

The source creates a new timer on every click and does not cancel earlier timers.

**Cheapest reproduction with an update trace — Console:**

```javascript
(() => {
  const box = document.querySelector('.lunch-display');
  const button = document.querySelector('#generateBtn');
  const start = performance.now();
  const observer = new MutationObserver(() => console.log(
    Math.round(performance.now() - start),
    document.querySelector('.food-name').textContent,
    document.querySelector('.food-icon i').className
  ));
  observer.observe(box, {childList: true, subtree: true});
  button.click();
  setTimeout(() => button.click(), 200);
  setTimeout(() => observer.disconnect(), 1500);
})()
```

Expect separate completions around **500 ms** and **700 ms**. This changes only the current page’s recommendation state.

## 11. The icon appears “stuck” because a random choice repeats

**On screen:** Clicking Generate returns the same icon and dish, making the user suspect that nothing updated.

**Cheapest check of the selection rule — Terminal:**

```bash
python3 - <<'PY'
from pathlib import Path
s = Path("baseline/index.html").read_text()
a = s.index("const randomIndex")
b = s.index("// Briefly show loading state", a)
print(s[a:b].strip())
PY
```

The selection has no repeat-prevention rule. With 12 equally likely options, an immediate repeat has probability **1/12**. A repeat alone does not prove an icon bug.

## 12. More than one recommendation icon is rendered

**On screen:** Two symbols appear above one dish, or an old icon remains alongside the new one.

**Cheapest check — Console:**

```javascript
[...document.querySelectorAll('.food-icon')].map(e => ({
  html: e.innerHTML,
  children: e.children.length,
  before: getComputedStyle(e.firstElementChild, '::before').content,
  after: getComputedStyle(e.firstElementChild, '::after').content
}))
```

Expect one container with one `<i>` and one generated glyph. Extra elements or an additional `::after` glyph would explain duplication.

**Source finding:** The current implementation replaces `innerHTML`, rather than appending icons, so ordinary recommendations should not accumulate extra elements.
