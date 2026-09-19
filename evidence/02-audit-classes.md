# Font Awesome 6.4.0 menu-class audit

## Sources and package identity

- Menu source: `baseline/index.html`, all 12 entries of `lunchMenu` in source order.
- Exact stylesheet loaded by the page: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
- Downloaded and extracted package: `@fortawesome/fontawesome-free@6.4.0`.
- Package archive: https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.4.0.tgz
- Metadata inspected: `package/metadata/icon-families.json`.
- CSS inspected: `package/css/all.css`.
- `package/package.json` confirms the package name and version. The extracted `package/css/all.min.css` is byte-for-byte identical to the downloaded CDN stylesheet (`cmp` succeeded).

## Method

1. Extract each dish name and icon class from the baseline's `lunchMenu` array. All entries use `fas`, the classic solid style.
2. Resolve the icon name against metadata keys and each record's `aliases.names`. An alias inherits the canonical record's license, styles, Unicode, and label.
3. Check free availability using `familyStylesByLicense.free`.
4. Check for an actual `svgs.classic.solid` entry, and separately confirm `{ "family": "classic", "style": "solid" }` in the free license list.
5. Find the exact `.fa-NAME::before` selector in `all.css` and extract its `content` code point. Verify it equals the metadata `unicode`; for aliases, also verify it equals the canonical class's CSS code point.
6. Copy the canonical metadata record's official `label` verbatim, preserving capitalization.

`No` and `N/A (absent)` refer specifically to this free 6.4.0 package. For the three unresolved names, neither a canonical key nor a name alias exists in its metadata, and no corresponding selector exists in its CSS. There is consequently no official label to report from these sources; no label is inferred from the requested class name. These results do not establish whether a name exists in another release or edition.

## Results

| Dish | Class in baseline | Free set (metadata) | `classic.solid` entry | Free `classic.solid` | `all.css` selector / glyph | Alias → canonical | Official `label` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pizza | `fas fa-pizza-slice` | Yes | Yes | Yes | Yes (`U+F818`) | No (canonical) | `Pizza Slice` |
| Sushi | `fas fa-fish` | Yes | Yes | Yes | Yes (`U+F578`) | No (canonical) | `Fish` |
| Burger | `fas fa-hamburger` | Yes | Yes | Yes | Yes (`U+F805`) | Yes → `burger` | `Burger` |
| Salad | `fas fa-leaf` | Yes | Yes | Yes | Yes (`U+F06C`) | No (canonical) | `Leaf` |
| Tacos | `fas fa-utensil-spoon` | Yes | Yes | Yes | Yes (`U+F2E5`) | Yes → `spoon` | `Spoon` |
| Ramen | `fas fa-bowl-hot` | No | No | No | No | N/A (absent) | N/A (absent) |
| Sandwich | `fas fa-bread-slice` | Yes | Yes | Yes | Yes (`U+F7EC`) | No (canonical) | `Bread Slice` |
| Pasta | `fas fa-pasta` | No | No | No | No | N/A (absent) | N/A (absent) |
| Curry | `fas fa-mortar-pestle` | Yes | Yes | Yes | Yes (`U+F5A7`) | No (canonical) | `Mortar Pestle` |
| Steak | `fas fa-drumstick-bite` | Yes | Yes | Yes | Yes (`U+F6D7`) | No (canonical) | `Drumstick Bite` |
| Soup | `fas fa-bowl` | No | No | No | No | N/A (absent) | N/A (absent) |
| BBQ | `fas fa-fire` | Yes | Yes | Yes | Yes (`U+F06D`) | No (canonical) | `Fire` |

## Findings

- **9 of 12** classes have both a free classic solid metadata entry and a matching CSS selector/code point.
- **3 of 12** are absent from both sources: Ramen (`fa-bowl-hot`), Pasta (`fa-pasta`), and Soup (`fa-bowl`).
- **2 aliases** are valid: `hamburger` → `burger`, and `utensil-spoon` → `spoon`. Neither alias is a missing-icon defect.
- All nine resolved CSS code points agree with metadata, and both aliases agree with their canonical CSS definitions.
- The library's own labels make the dish/depiction comparison explicit: Tacos / `Spoon`, Steak / `Drumstick Bite`, Sushi / `Fish`, Salad / `Leaf`, Sandwich / `Bread Slice`, Curry / `Mortar Pestle`, and BBQ / `Fire`. Pizza maps to `Pizza Slice`; Burger maps to `Burger`. These label strings establish what the library calls each glyph independently of rendering availability.

## Reproduce

From the repository root, download into a fresh temporary directory and run the committed read-only audit script:

```bash
audit_dir="$(mktemp -d)"
curl --fail --location --silent --show-error \
  "https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.4.0.tgz" \
  --output "$audit_dir/fontawesome-free-6.4.0.tgz"
tar -xzf "$audit_dir/fontawesome-free-6.4.0.tgz" -C "$audit_dir"
curl --fail --location --silent --show-error \
  "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" \
  --output "$audit_dir/cdn-all.min.css"
cmp "$audit_dir/package/css/all.min.css" "$audit_dir/cdn-all.min.css"
python3 scripts/audit_icon_classes.py "$audit_dir/package"
```

The script prints the table and checks package identity, the 12-item count, free classic solid availability versus CSS presence, and metadata/canonical CSS code-point agreement.

## SHA-256 provenance

```text
45de4f0b3b77768b5c7c095b1e4f0f1de2095935c5f0711e60831b834181fdbb  baseline/index.html
385681597a3301b5f56fc70136274f9fd081e0ac5b9f8222351ac7e89465dfa2  fontawesome-free-6.4.0.tgz
660ed1c51e0c49e570cb6fd2f1da3478527e85846d707b61ca4745578c2b44d0  package/metadata/icon-families.json
0822e64055e9b5e5fca4c230a1140b23dff7986fdc111a366251e73b97a1c5b6  package/css/all.css
1edb1725a9ea8ca4dcf2f5508cee183218aa1685e47c1b23056717f754f58ebf  package/css/all.min.css
1edb1725a9ea8ca4dcf2f5508cee183218aa1685e47c1b23056717f754f58ebf  cdn-all.min.css
```
