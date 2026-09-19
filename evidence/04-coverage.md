# Exhaustive dish-name coverage: Font Awesome Free and Lucide Static

## Claim and result

> The free icon set contains a dedicated glyph for each of these dishes, so fixing this is just a matter of picking the correct existing icon name.

**The claim is false for both tested packages.** Using the requested **dish-named glyph** criterion, Font Awesome Free 6.4.0 covers **2/12** dishes and Lucide Static 1.47.0 covers **5/12**. Every name and every official metadata record in each package was searched, including aliases; this is not a search limited to the existing menu classes or a sample of icons.

Here, a **dedicated, dish-named glyph** means that the icon's canonical name, available alias, or official label names the dish, allowing singular/plural forms, hamburger/cheeseburger for Burger, and barbecue/barbeque for BBQ. Compound names such as `pizza-slice` count. A related search tag alone does not establish a dish-named icon: `sandwich` on Cheese or `hamburger` on a navigation Menu is not the icon's identity.

The metadata-only findings are retained separately. In particular, Lucide's `beef` explicitly has the official tag `steak`: the lack of a `steak`-named icon must **not** be read as proof that Lucide has no usable steak depiction. The conclusion tested here is complete dish-named coverage, not an exhaustive visual classification of every drawing.

## Packages and exhaustive inventory

| Library | Exact package | Canonical icon definitions | Names including aliases | SVG files |
| --- | --- | ---: | ---: | ---: |
| Font Awesome Free | `@fortawesome/fontawesome-free@6.4.0` | 1,856 | 2,452 | 2,020 across solid, regular, and brands |
| Lucide Static | `lucide-static@1.47.0` | 1,848 | 2,112 | 2,112 including aliases |

- Font Awesome's **1,856** canonical records in `package/metadata/icon-families.json` all have nonempty `familyStylesByLicense.free`. Their names exactly match the distinct SVG stems in `package/svgs/*/*.svg`. All **2,452** canonical/alias names exactly match the icon pseudo-element selectors in `package/css/all.css`. The inventory includes all free styles, not only classic solid.
- Lucide was acquired with **`npm pack lucide-static@1.47.0`**, then extracted. Its **1,848** canonical keys agree exactly between `package/tags.json` and `package/icon-nodes.json`. All canonical icons have SVGs. The **264** additional SVG names were also searched; every one has exactly the same SVG elements/attributes as at least one canonical icon after excluding the root `class` attribute.
- Lucide's package provides official **tags**, not a Font Awesome-style `label` field. No labels were invented from filenames. Canonical keys are covered by the name search; the metadata column reports matches in metadata values.

Sources:

- https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.4.0.tgz
- https://registry.npmjs.org/lucide-static/-/lucide-static-1.47.0.tgz
- Menu: all 12 dishes in `baseline/index.html`, in source order.

## Exact search method

The executable method is committed as `scripts/audit_dish_coverage.py`. Full field-level hits and computed counts are saved in `evidence/04-coverage-search.json`.

1. Read the 12 dish names directly from the baseline's `lunchMenu` array; assert there are exactly 12 distinct entries.
2. Check package names and pinned versions. Build and cross-check the complete inventories as described above.
3. **Broad discovery pass:** case-fold every available icon name/alias and every string value in every Font Awesome metadata record. Recursively scan the complete records, including labels, alias names, search terms, ligatures, and the other string fields. For Lucide, scan every SVG filename stem and every official tag value for every canonical icon. Record every matching icon, metadata field path, and value.
4. Use case-insensitive **substring** search in this discovery pass, with the queries below. This intentionally preserves possible false positives such as `pastafarianism` for Pasta rather than silently omitting them.
5. **Dish-named classification:** tokenize names, aliases, and official labels with `[a-z]+` after case-folding. Count a dish if any token exactly matches its explicit accepted-token list below. Search tags do not count as names or labels. The count is dishes covered, not number of matching icons, aliases, or style variants.
6. Also compute a separate **any whole-token name-or-metadata hit** count, using the same tokens on all discovery hits. This exposes metadata-only associations without treating them as dedicated names.

| Dish | Broad substring queries | Accepted tokens for dish-named classification |
| --- | --- | --- |
| Pizza | `pizza` | `pizza`, `pizzas` |
| Sushi | `sushi` | `sushi` |
| Burger | `burger` | `burger`, `burgers`, `hamburger`, `hamburgers`, `cheeseburger`, `cheeseburgers` |
| Salad | `salad` | `salad`, `salads` |
| Tacos | `taco` | `taco`, `tacos` |
| Ramen | `ramen` | `ramen` |
| Sandwich | `sandwich` | `sandwich`, `sandwiches` |
| Pasta | `pasta` | `pasta`, `pastas` |
| Curry | `curry`, `curries` | `curry`, `curries` |
| Steak | `steak` | `steak`, `steaks` |
| Soup | `soup` | `soup`, `soups` |
| BBQ | `bbq`, `barbecue`, `barbeque` | `bbq`, `barbecue`, `barbecues`, `barbeque`, `barbeques` |

No implicit substitutions such as fish → sushi, leaf → salad, spoon → tacos, generic bowl → ramen, fire → BBQ, or bread → sandwich are counted. This method tests the stated naming claim; it does not prove that no alternative-language name or visually related symbol exists.

## Per-dish, per-library results

The metadata column retains the official matching strings verbatim. For Font Awesome, these include `label`, `aliases.names`, and `search.terms`; their exact field paths are in the JSON evidence. Lucide matches in that column are official `tags` values. `None` means no substring match in that source, not missing metadata.

| Dish | Library | Name/alias substring hits | Official label/metadata substring hits | Dish-named glyph? |
| --- | --- | --- | --- | --- |
| Pizza | Font Awesome 6.4.0 | `pizza-slice` | `pizza-slice`: `Pizza Slice` | Yes |
| Pizza | Lucide Static 1.47.0 | `pizza` | None | Yes |
| Sushi | Font Awesome 6.4.0 | None | None | No |
| Sushi | Lucide Static 1.47.0 | None | None | No |
| Burger | Font Awesome 6.4.0 | `burger`, `hamburger` | `bars`: `hamburger`; `burger`: `Burger`, `burger`, `burger king`, `cheeseburger`, `hamburger` | Yes |
| Burger | Lucide Static 1.47.0 | `hamburger` | `hamburger`: `burger`, `cheeseburger`; `menu`: `hamburger`; `square-menu`: `hamburger` | Yes |
| Salad | Font Awesome 6.4.0 | None | None | No |
| Salad | Lucide Static 1.47.0 | `salad` | `leafy-green`: `salad` | Yes |
| Tacos | Font Awesome 6.4.0 | None | None | No |
| Tacos | Lucide Static 1.47.0 | None | None | No |
| Ramen | Font Awesome 6.4.0 | None | None | No |
| Ramen | Lucide Static 1.47.0 | None | None | No |
| Sandwich | Font Awesome 6.4.0 | None | `bread-slice`: `sandwich`; `burger`: `sandwich`; `cheese`: `sandwich`; `hotdog`: `sandwich` | No |
| Sandwich | Lucide Static 1.47.0 | `sandwich` | None | Yes |
| Pasta | Font Awesome 6.4.0 | `pastafarianism` | `spaghetti-monster-flying`: `pastafarianism` | No |
| Pasta | Lucide Static 1.47.0 | None | None | No |
| Curry | Font Awesome 6.4.0 | None | None | No |
| Curry | Lucide Static 1.47.0 | None | None | No |
| Steak | Font Awesome 6.4.0 | None | None | No |
| Steak | Lucide Static 1.47.0 | None | `beef`: `steak`; `beef-off`: `steak` | No |
| Soup | Font Awesome 6.4.0 | None | None | No |
| Soup | Lucide Static 1.47.0 | `soup` | None | Yes |
| BBQ | Font Awesome 6.4.0 | None | None | No |
| BBQ | Lucide Static 1.47.0 | None | `beef`: `bbq`; `beef-off`: `bbq`; `hamburger`: `barbecue`, `barbeque`, `bbq` | No |

## Totals and interpretation

| Measure | Font Awesome Free 6.4.0 | Lucide Static 1.47.0 |
| --- | --- | --- |
| Dedicated dish-named coverage | **2/12**: Pizza, Burger | **5/12**: Pizza, Burger, Salad, Sandwich, Soup |
| Any whole-token name/metadata association (not dedicated coverage) | **3/12**: Pizza, Burger, Sandwich | **7/12**: Pizza, Burger, Salad, Sandwich, Steak, Soup, BBQ |

**No dish-named glyph in either:** Sushi, Tacos, Ramen, Pasta, Curry, Steak, BBQ (**7 dishes**).

**No whole-token name or official metadata match in either:** Sushi, Tacos, Ramen, Pasta, Curry (**5 dishes**).

Important distinctions:

- `pastafarianism` is an alias of `spaghetti-monster-flying`, officially labeled **`Spaghetti Monster Flying`**. Its `pasta` substring is a false positive for a Pasta dish icon and fails the explicit whole-token criterion.
- Font Awesome's Sandwich search matches bread, burger, cheese, and hotdog metadata, but none is named or labeled Sandwich.
- Burger searches also find navigation icons tagged `hamburger`. Those metadata matches are not food glyphs. Both libraries independently have an actual food-named burger icon, so Burger is covered.
- Lucide `beef` and `beef-off` have an official `steak` tag; they are metadata-supported candidates, not steak-named icons. They also carry `bbq`, and Lucide's `hamburger` has barbecue-related tags. These associations are fully reported rather than treated as zero results or silently promoted to dedicated names.
- Even the looser **any matching name/metadata** interpretation leaves five dishes uncovered in both libraries. Choosing different existing names from either tested package therefore does not establish complete dedicated coverage for this catalogue.

## Reproduce

Run from the repository root (Python 3, npm, curl, and tar required):

```bash
audit_dir="$(mktemp -d)"
mkdir "$audit_dir/fontawesome" "$audit_dir/lucide"
curl --fail --location --silent --show-error \
  "https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.4.0.tgz" \
  --output "$audit_dir/fontawesome/fontawesome-free-6.4.0.tgz"
tar -xzf "$audit_dir/fontawesome/fontawesome-free-6.4.0.tgz" -C "$audit_dir/fontawesome"
npm pack lucide-static@1.47.0 --pack-destination "$audit_dir/lucide" --silent
tar -xzf "$audit_dir/lucide/lucide-static-1.47.0.tgz" -C "$audit_dir/lucide"
python3 scripts/audit_dish_coverage.py \
  "$audit_dir/fontawesome/package" "$audit_dir/lucide/package" \
  --json-output "$audit_dir/04-coverage-search.json"
cmp evidence/04-coverage-search.json "$audit_dir/04-coverage-search.json"
```

The script asserts the package identities, full inventory consistency, alias-geometry coverage, and menu cardinality. It prints all 24 result rows plus computed totals. The optional JSON output records every raw hit, query, accepted token, source checksum, and count without machine-specific paths or timestamps.

## SHA-256 provenance

```text
45de4f0b3b77768b5c7c095b1e4f0f1de2095935c5f0711e60831b834181fdbb  baseline/index.html
385681597a3301b5f56fc70136274f9fd081e0ac5b9f8222351ac7e89465dfa2  fontawesome-free-6.4.0.tgz
b47744c9f7b385c25fb27d212cf9830947030a57a635f8b11a5473a72ec57cfd  lucide-static-1.47.0.tgz
660ed1c51e0c49e570cb6fd2f1da3478527e85846d707b61ca4745578c2b44d0  fontawesome/package/metadata/icon-families.json
0822e64055e9b5e5fca4c230a1140b23dff7986fdc111a366251e73b97a1c5b6  fontawesome/package/css/all.css
2c5b54d36c25c1fec2a51d724ff7e775e8d279d719160193509085f5c9057d2f  lucide/package/tags.json
da6e80345f5af5143c81f78ca55c390908188f31f4451488a69969d69a20d95f  lucide/package/icon-nodes.json
```
