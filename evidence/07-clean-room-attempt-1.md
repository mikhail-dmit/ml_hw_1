# Clean-room attempt 1

Source: Separate OpenCode session with no prior context.
Date recorded: 2026-09-19.

Exact instruction:

```text
Read prompt-v2.md in this repository and treat it as the complete specification.
Do not look at baseline/index.html, at any file under evidence/, or at git
history — the point of this session is to test whether the specification alone is
sufficient. Produce app/index.html exactly as the specification requires,
including the Visual Asset Mapping Table it asks you to output before any code.
```

**`prompt-v2.md` is not sufficient as a standalone specification under your access restrictions.** I read it without opening `baseline/index.html`, any file under `evidence/`, or git history. I have not written implementation code.

### Visual Asset Mapping Table — blocked


The specification requires a fully resolved, evidence-backed mapping before any code, but some mandatory inputs exist only in the files you prohibited:


| Required information | Specification reference | Blocker |
|---|---|---|
| Baseline class for every dish | B, D; lines 54, 78–79 | The prompt names all 12 dishes but does not provide their complete baseline class mapping. |
| Explicit human decisions and their justifications for every eligible icon | C; lines 66–70 | The prompt includes selected decisions, but requires the full decisions from `evidence/06-review-decisions.json`. |
| Exact approved final assignment | D; lines 82–84 | The authoritative assignment is referenced in `evidence/06-asset-map.md`, rather than reproduced in the prompt. |
| Provenance and package/CDN checks | A; line 44 | The required records are under `evidence/`. |


I also inspected the permitted `scripts/build_asset_map.py` to determine whether it could resolve these dependencies. It contains explicit emoji fallbacks, but **both execution modes read `baseline/index.html`**, and the full mode additionally reads the prohibited review decisions. I did not run it.


The vendored metadata can establish icon existence, style, categories, and labels. It cannot establish the omitted baseline associations or recorded human approvals.


### Implementation and verification status


- **`app/index.html`:** not created or modified.
- **Mapping:** unresolved; presenting a completed table would require inventing or assuming mandatory inputs.
- **Rendering and rapid-click tests:** not run; no passing results claimed.


This follows section G, which explicitly prohibits guessing unavailable review decisions or presenting an incomplete implementation as complete.


To make this specification independently executable, inline the complete baseline class mapping, the approved final assignments, and every required human decision with its justification. Also replace the mandatory checks against prohibited files with self-contained requirements. With those additions, the mapping can be shown before code and the implementation verified within your boundary.
