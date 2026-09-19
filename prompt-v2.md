# Corrected prompt: preserve the menu and validate its visual assets

## Part 1 — What the original prompt was

> ## Q: I need to code random lunch menu recsys then publish this into github page. Let's first write the description readme.

> *   **Visual Appeal:** Each suggestion is paired with a relevant icon or image for a better experience.

> *   Icons provided by [Font Awesome](https://fontawesome.com/).

## Part 2 — Why that prompt produced these defects

**Source and evidence boundary.** Part 1 quotes the human turn and the generated README embedded in upstream [`week1/prompt.md`](https://raw.githubusercontent.com/dryjins/RecSys-LLMs/main/week1/prompt.md). Those historical quotations are the requested source material, not findings from the committed audit bundle. The prompt-level omissions and causal interpretations below are therefore marked **unverified remarks relative to evidence 00–06**. In particular, the audits do not establish the model's internal reasoning or the order in which it consulted resources. The observed consequences are separately grounded in the cited evidence. Evidence [01](evidence/01-icon-hypotheses.md) records hypotheses; a hypothesis alone is not a reproduced failure.

| Defect | Prompt omission / causal interpretation | Consequence observed in the committed evidence |
| --- | --- | --- |
| **1. Asset library treated as an acknowledgement, not a constraint — root-cause diagnosis** | **Unverified causal remark:** Font Awesome appears as an acknowledgement in the quoted generated README, rather than an enforceable dependency and admissibility contract established before design. Availability and suitability are left implicit. | The original classes include unavailable definitions and available but unsuitable depictions: Ramen, Pasta, and Soup have no definitions; Tacos is officially `Spoon`, and Steak is `Drumstick Bite`. These are separate availability and meaning failures. [02](evidence/02-audit-classes.md), [06](evidence/06-asset-map.md). |
| **2. No version pinned by the prompt** | **Unverified prompt-level remark:** The original request and the quoted acknowledgement do not constrain an edition, version, or style. This is a specification omission, not a claim that the resulting HTML lacked a versioned URL. | The audited page actually loads Font Awesome Free **6.4.0**, yet `fa-bowl-hot`, `fa-pasta`, and `fa-bowl` are absent from that package's metadata and CSS. The evidence establishes incompatibility with the loaded package, **not version drift as a demonstrated cause**. [02](evidence/02-audit-classes.md). |
| **3. Menu fixed before icon-set feasibility is checked** | **Unverified generation-order inference:** Treating a predefined menu as ready for implementation before consulting the asset catalogue leaves its visual coverage unproved. The audit cannot establish whether or when the generating model actually consulted the library. The defect is skipping the asset check, not having a fixed menu. | Exhaustive dish-named searches cover only **2/12** dishes in Font Awesome Free and **5/12** in the tested Lucide package. The later human-reviewed assignment preserves all **12/12**, using **3/12** Font Awesome assets and **9/12** emoji. The named-coverage test and the human admissibility test are different: the latter explicitly accepts Fish for Sushi. [04](evidence/04-coverage.md), [06](evidence/06-asset-map.md). |
| **4. “A relevant icon” is an adjective, not an acceptance condition** | **Unverified causal remark:** The wording supplies no checkable definition of relevance, no category requirement, and no recorded human decision about whether a glyph distinguishes one menu entry from another. | The metadata classifies `leaf` outside `food-beverage`, `spoon` under household/maps, and `mortar-pestle` under medical-health/science. Bread Slice and Drumstick Bite pass the mechanical food checks but fail the recorded human reviews for Sandwich and Steak. Existence alone is insufficient. [06](evidence/06-asset-map.md). |
| **5. No numeric definition of done; blank slots fail silently** | **Unverified prompt-level remark:** A visual promise without exhaustive measurements supplies no acceptance gate for missing assets. | Deterministic Chromium enumeration renders **9/12** glyphs and **3/12** blanks. Ramen, Pasta, and Soup each have `content: "none"` and width **0**, although the stylesheet and solid font loaded and the recorded error list is empty. [03 measurements](evidence/03-icon-measurements.json), [03 screenshot](evidence/03-icon-sheet.png). |
| **6. Asynchronous reveal has no guard** | The source finding is recorded in [01, hypothesis 10](evidence/01-icon-hypotheses.md): each click creates another timer without cancelling earlier ones. **Unverified causal remark:** the original prompt failed to demand a concurrency policy for the reveal. | The runtime trace records **5** clicks within **204.1 ms**, **5** result transitions, and **4** stale results after the latest click. There are **6** visible content transitions including loading. These are frame-observed content changes, not compositor paint-event counts. Every result belongs to an actual click; no mismatched name/icon pair or wholly unrequested result was observed. [05](evidence/05-race.json). |
| **7. No canonical-name requirement** | **Unverified prompt-level remark:** A class that happens to render is accepted without checking whether it is the canonical name for the selected release. | `hamburger` is an alias of `burger`; `utensil-spoon` is an alias of `spoon`. Both aliases render, so they are latent naming defects rather than the cause of the blank slots. The final assignment canonicalizes Burger and replaces the inadmissible Tacos asset with emoji. [02](evidence/02-audit-classes.md), [06](evidence/06-asset-map.md). |

**Root cause — unverified causal diagnosis, supported by the observed failure pattern:** defect 1, the absence of an enforceable visual-asset contract before implementation. It allows dependency selection, semantic matching, fallback policy, and verification to remain assumptions. The evidence demonstrates that rendering availability and dish identification need different checks; neither a library acknowledgement nor a plausible class name supplies them. Defects 2–5 and 7 expose parts of that missing contract. Defect 6 additionally needs an explicit interaction contract; correcting asset names alone does not address the observed stale results. This diagnosis is an interpretation of [02](evidence/02-audit-classes.md), [03](evidence/03-icon-measurements.json), [05](evidence/05-race.json), and [06](evidence/06-asset-map.md), not a recorded account of the original model's thought process.

## Part 3 — The corrected prompt

### A — Apply the dependency constraint before any design work

Use **Font Awesome Free 6.4.0, classic solid style**, at this exact pinned CDN stylesheet URL:

```text
https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
```

Treat the library, edition, version, and style as hard constraints, not acknowledgements. Do not change them to make an unsupported icon name work. Before designing the UI or writing any code, complete and show the Visual Asset Mapping Table required below.

Use the shipped files as your factual authority:

- `vendor/fontawesome-free-6.4.0/metadata/icon-families.json`
- `vendor/fontawesome-free-6.4.0/metadata/categories.yml`

Use [00-provenance.md](evidence/00-provenance.md) for the registry-hash and archive-to-vendor checks, and [02-audit-classes.md](evidence/02-audit-classes.md) for the package/CDN correspondence and style checks. Do not infer semantic suitability from an integrity hash.

### B — Treat the complete menu as immutable input

Implement the lunch recommender for exactly these **12** dishes, in this order:

```text
Pizza, Sushi, Burger, Salad, Tacos, Ramen, Sandwich, Pasta, Curry, Steak, Soup, BBQ
```

The dishes **MAY NOT BE REMOVED, REPLACED OR REORDERED**. The menu is an input, not a variable to optimize for library coverage. Preserve its names and uniform random selection. Derive and check the ordered list against `baseline/index.html` and the final assignment in [06-asset-map.md](evidence/06-asset-map.md). Uniform selection is recorded in [01](evidence/01-icon-hypotheses.md); the complete catalogue is recorded in [03](evidence/03-icon-measurements.json).

Render the selected dish name together with its assigned visual asset. Do not substitute another dish because the original class is missing or inadmissible.

### C — Apply the admissibility rule and record human review

Apply the following rule exactly as operationalized in [06-asset-map.md](evidence/06-asset-map.md):

**(a) Existence and free solid style.** Resolve the baseline name against a canonical metadata key or an entry in another icon's `aliases.names`. Require both a `svgs.classic.solid` entry and the pair `{ "family": "classic", "style": "solid" }` under `familyStylesByLicense.free`. Resolving an alias for diagnosis does not authorize emitting that alias in the final code.

**(b) Food category.** Require the resolved canonical name to be listed in the `food-beverage` icon list in `metadata/categories.yml`. Report all of its category memberships. Do not infer the category from a plausible name or its appearance.

**(c) Distinguishing meaning.** The official `label` must denote the dish itself, or an ingredient that distinguishes that dish from the other eleven. Reject a glyph that could equally identify another dish on this same menu. Follow the recorded human interpretation: judge conventional composition and menu-level identification, not every hypothetical ingredient variant. Do not automate this semantic decision. For every icon passing (a) and (b), print the dish and official label as **REVIEW**, then record the explicit human **KEEP-FA** or **EMOJI** decision and its one-line justification.

Decide **(a) and (b) by reading the shipped metadata files**, not from memory. You may run the existing `scripts/build_asset_map.py --review-only` and `scripts/build_asset_map.py`; do not write new implementation code before presenting the mapping. Reuse the explicit decisions in [06-review-decisions.json](evidence/06-review-decisions.json), with their justifications visible. If a proposed change needs a new semantic decision, obtain human review before coding instead of silently inventing approval.

Preserve the approved Sushi decision: **Fish is accepted as a category-level match**, because Sushi is the conventionally seafood item in this menu under the recorded review. Also retain the recorded objection: sushi is defined by vinegared rice, and the glyph depicts a whole raw fish, not a prepared dish. Do not report this as exact dish-name coverage or as a universal semantic fact. Sandwich's Bread Slice is rejected because Burger is bread-based by definition; Steak's Drumstick Bite is rejected because it does not identify Steak. These are the decisions in [06](evidence/06-asset-map.md).

Use **canonical v6 icon names only** in the final assignment and code. Reject aliases such as `fa-hamburger` as final values even though they render; emit the approved canonical `fas fa-burger` instead. Record `fa-utensil-spoon` as the other baseline alias, but do not treat its canonicalization as permission to keep an asset that fails the category or semantic rule. [02](evidence/02-audit-classes.md), [06](evidence/06-asset-map.md).

### D — Show the Visual Asset Mapping Table before writing any code

Produce and show a table with **one row for each of the 12 dishes**, preserving their order. Include:

- Dish and baseline class.
- Baseline existence and canonical/alias resolution.
- Chosen asset value and type: `font-awesome` or `emoji`.
- For a Font Awesome asset: canonical metadata key, evidence of the free `classic.solid` entry, category memberships, exact official label, and the recorded human decision with justification.
- For an emoji: the failed admissibility condition or rejected REVIEW decision, and the Unicode fallback taken from the approved assignment.

Reproduce the final assignment in [06-asset-map.md](evidence/06-asset-map.md): **3/12 Font Awesome assignments and 9/12 emoji assignments, preserving 12/12 dishes**. These are assignment counts, not evidence that the corrected implementation has already passed rendering tests. Use the script-derived mapping and recorded decisions, not a newly guessed table.

**Any dish whose class fails the admissibility rule receives a Unicode emoji. Removing the dish is not an option.** Use the operating system's emoji font stack for emoji assets rather than treating their values as Font Awesome classes. Preserve the distinct approved fallbacks for Ramen and Soup. Do not replace them with `bowl-food` or `bowl-rice`: the official labels identify generic food or rice in a bowl and do not distinguish these dishes, as documented in [06](evidence/06-asset-map.md).

Proceed to code only after showing the complete mapping with no unresolved REVIEW decisions.

### E — Guard the reveal so one burst produces one result

Implement an explicit guard for the asynchronous reveal. Choose and state one of these required policies:

- **Cancel-and-replace:** cancel any pending reveal timer before starting a new one. Only the latest accepted click in the pending burst may reveal a result.
- **Disable-until-complete:** disable the control while a reveal is pending, accept no additional requests during that period, and re-enable it after the reveal completes.

Apply the same pending-reveal policy to any automatic page-load reveal. Keep the dish name and its assigned asset in the same result update.

For **N rapid click attempts arriving while the reveal is pending, produce exactly one visible recommendation**, not a sequence of stale recommendations. A loading indicator or its animation is not a recommendation. State whether the policy preserves the first accepted request or replaces it with the latest request. The acceptance test concerns the result shown for a burst, not the number of browser animation paints.

These are required remedies to implement and verify, **not fixes already demonstrated by the committed evidence**. [05-race.json](evidence/05-race.json) records the unguarded baseline; it does not establish that a corrected implementation passes.

### F — Meet the numeric definition of done

Do not declare completion until the corrected implementation satisfies **all 12 items rendering a visible asset, with zero blanks out of 12**.

Enumerate all menu entries deterministically in source order. Do not estimate coverage by clicking the random button. Load the pinned stylesheet, confirm the stylesheet and solid font loaded, and wait for `document.fonts.ready` before measuring, following the method in [03](evidence/03-icon-measurements.json).

Measure the actual asset element, not a fixed-width wrapper. Require:

- **Font Awesome asset:** `getComputedStyle(el,'::before').content !== 'none'` **and** `el.getBoundingClientRect().width > 0`.
- **Emoji asset:** non-empty text, tested as `el.textContent.trim() !== ''`, **and** `el.getBoundingClientRect().width > 0`.

Record each dish, asset type/value, measured content or text, width, and pass/fail. Save a screenshot of the complete catalogue and inspect it for visibility and the approved dish-to-asset correspondence. Report **12/12 passing and 0/12 blank only if those are the actual measurements**. The positive-width checks are the required mechanical tests; do not use them as a replacement for semantic review or screenshot inspection.

Also test the guarded application with **5 click attempts within 300 ms**, after the page-load recommendation settles. Record attempt timestamps, accepted requests, result updates, displayed names/assets, and whether each pair belongs to the same approved menu entry. Require **exactly one visible result for the burst, zero stale result reveals, and zero mismatched pairs**. Measure actual timing and results; do not relabel the old trace as a passing test. The baseline comparison and its distinction between timer completions, DOM changes, and frame-observed content changes are in [05](evidence/05-race.json).

These numeric targets are requirements for the new implementation, **not claims that evidence 03 or 05 already meets them**. The baseline measurements and the approved asset assignment are different artifacts.

### G — Report unmet requirements plainly

If you cannot satisfy any item, state plainly **which dish or requirement remains unsatisfied, the failed check, and the supporting evidence**. If required metadata or review decisions are unavailable, say so explicitly rather than guessing them. Do not remove, replace, or reorder menu entries, return known-incomplete code with a caveat, or claim completion while a check fails. Resolve the blocked requirement before presenting code as the completed solution.

Return the mapping first, followed by the implementation only after the mapping is resolved, and then the actual verification results. Keep assumptions and unverified remarks visibly separate from measured facts.

## Part 4 — Why this prompt cannot reproduce the same failure

**Verification boundary:** a compliant implementation cannot be accepted as complete with these same documented defects, because the clauses below make each one an explicit rejection condition. That is an acceptance argument, not proof that a model will obey the prompt or that a future implementation has already passed. **The corrected prompt's actual effectiveness remains unverified until it is used and its outputs are tested.**

| Part 2 defect | Specific Part 3 clause that removes the omission |
| --- | --- |
| **1 — Acknowledgement instead of constraint** | **A** establishes the exact library/edition/style before design; **C** makes admissibility explicit; **D** blocks code until the complete evidence-backed mapping is shown. |
| **2 — No prompt-level version pin** | **A** requires Free 6.4.0 and its exact CDN URL, with shipped metadata and the provenance evidence as the authority. A remembered name from another release is not sufficient. |
| **3 — Menu-before-assets feasibility gap** | **B** makes all 12 dishes immutable; **D** requires every asset to be mapped before code and uses emoji for gaps. The task can no longer be completed by assuming coverage or shrinking the menu. |
| **4 — Unverifiable “relevant” adjective** | **C(a–c)** separates existence/free style, official category, and explicit human interpretation of the official label. **D** preserves the reviewed decisions and rejects generic bowl substitutions. |
| **5 — Silent blanks and no definition of done** | **F** requires deterministic 12-item measurement, visible assets, and 0/12 blanks, plus a screenshot; **G** prohibits presenting failed checks as a completed solution with a caveat. |
| **6 — Unguarded reveal** | **E** requires cancellation or a disabled control; **F** requires the rapid-click test to show one result and no stale reveals, with timestamped evidence. |
| **7 — Alias accepted as canonical** | **C** separates alias diagnosis from final admissibility and permits only canonical v6 names in the emitted Font Awesome assignment. |

### Residual risks this prompt does not remove

- **CDN single point of failure — unverified failure scenario, not an observed outage.** The pinned CDN remains the external dependency for the retained Font Awesome assets. Pinning and metadata checks do not supply an independent delivery path. Stylesheet and font-loading failures are hypotheses in [01, items 4–5](evidence/01-icon-hypotheses.md); [03](evidence/03-icon-measurements.json) records successful loading in the tested run. This prompt's checks detect a failure in the test environment, but do not establish future CDN availability.
- **Operating-system emoji rendering.** [06](evidence/06-asset-map.md) explicitly assigns Unicode emoji through the viewer's operating system font stack. **Unverified across viewers:** the committed evidence does not establish identical appearance or glyph support on every operating system. Non-empty text and positive width alone are not proof of an appropriate-looking emoji on every viewer's device; that limitation is why the prompt also requires visual inspection rather than equating an assigned character with universal rendering success.
- **Human semantic judgment.** The Sushi category-level acceptance and its recorded objection remain part of [06](evidence/06-asset-map.md). The prompt preserves that explicit decision; it does not turn the label `Fish` into an exact Sushi depiction or prove that every viewer interprets it identically. Universal interpretation is **unverified**.
- **Integrity is not semantic or runtime correctness.** [00](evidence/00-provenance.md) verifies registry-hash agreement and vendored bytes, while explicitly limiting what that establishes. It does not prove icon suitability, safety, or a future implementation's behavior. The rendering and interaction requirements still need to be executed against that implementation.
