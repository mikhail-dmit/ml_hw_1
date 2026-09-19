# Clean-room attempt 1 — specification dependency failure

## Source and status

**Result: failed to produce `app/index.html`.** This record documents the user's report of a fresh session given the earlier `prompt-v2.md` without the prior conversation or readable supporting audit files. The prompt version under test was introduced in commit `e6e91be` (`docs: define evidence-backed prompt for complete visual coverage`).

The user reported that a fresh session with no prior context refused to produce `app/index.html` because the prompt depended on files it could not read.

The user identified the missing inputs as:

- The baseline Font Awesome class for each dish.
- The recorded human decisions for admissibility rule (c).
- The approved final assignment that the prompt instructed the implementer to reproduce from an audit report.

This is a user-reported outcome, not a reconstructed model transcript. No raw clean-room transcript was supplied in this checkout. Independently, inspection of the local `app/` directory found only `.gitkeep`, with no `app/index.html`; that confirms the missing local artifact but does not by itself establish why the other session declined.

## What failed

The prompt depended on `baseline/index.html`, `evidence/06-review-decisions.json`, `evidence/06-asset-map.md`, and repository helper scripts for inputs it had not included. Its refusal-on-missing-input instruction did not cure that omission: the specification itself was incomplete for a clean-room implementer.

This is a **prompt defect**, not a failed visual/runtime measurement and not a limitation of the clean-room test. There is no fixed page to measure, so no after-fix asset coverage, blank count, or rapid-click result count is claimed here. A later inspection of the existing test scripts does not explain or excuse this generation failure.

## Response

The corrected Part 3 now carries:

- The exact twelve upstream dish names and baseline class strings, in source order, as the input to repair.
- The unchanged three-part admissibility rule.
- All five explicit human (c) decisions with their one-line justifications and the recorded Sushi objection.
- The prescribed emoji fallbacks.
- Instructions for independently obtaining the pinned official Font Awesome package and inspecting its vendored metadata.
- A requirement to derive the mechanical (a)/(b) outcomes and the final mapping before writing application code.

The finished asset-map table is **not** supplied as an answer to copy. Human semantic outcomes are inputs because rule (c) is non-automatable; mechanical eligibility remains the implementer's responsibility. The revised Part 3 requires neither the prior evidence files nor the original application file to complete the work.

## Verification boundary

The repair addresses the reported missing-input dependency. Static checks can establish that the inputs are present and the rule is unchanged; they do not establish successful generation or correct runtime behavior. A second clean-room run and fixed-app browser measurements remain outstanding.
