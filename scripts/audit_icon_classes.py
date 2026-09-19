"""Print the baseline menu's icon audit against an extracted Font Awesome package."""

import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Extracted package/ directory")
    args = parser.parse_args()

    baseline = Path(__file__).resolve().parents[1] / "baseline" / "index.html"
    html = baseline.read_text(encoding="utf-8")
    version = re.search(r"/font-awesome/([^/]+)/css/all\.min\.css", html)[1]
    manifest = json.loads((args.package / "package.json").read_text())
    assert manifest["name"] == "@fortawesome/fontawesome-free", manifest["name"]
    assert manifest["version"] == version, (manifest["version"], version)

    metadata = json.loads((args.package / "metadata/icon-families.json").read_text())
    css = (args.package / "css/all.css").read_text()
    # Index actual pseudo-element selectors and their content, including grouped aliases.
    glyphs = {}
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        content = re.search(r'content:\s*"\\([0-9a-fA-F]+)"', body)
        if content:
            for name in re.findall(r"\.fa-([\w-]+)::?before\b", selectors):
                glyphs[name] = content[1].lower()

    names = {}
    for canonical, record in metadata.items():
        for name in [canonical, *record.get("aliases", {}).get("names", [])]:
            assert name not in names or names[name] == canonical, name
            names[name] = canonical

    menu = re.search(r"const lunchMenu = \[(.*?)\];", html, re.S)[1]
    items = re.findall(r'{ name: "([^"]+)", icon: "([^"]+)" }', menu)
    assert len(items) == 12, f"Expected 12 menu items, got {len(items)}"
    rows = []
    for dish, classes in items:
        style, icon_class = classes.split()
        assert style == "fas" and icon_class.startswith("fa-"), classes
        name = icon_class[3:]
        canonical = names.get(name)
        record = metadata.get(canonical, {})
        free_styles = record.get("familyStylesByLicense", {}).get("free", [])
        solid = "solid" in record.get("svgs", {}).get("classic", {})
        free_solid = {"family": "classic", "style": "solid"} in free_styles
        css_present = name in glyphs

        # A class is usable here only if both metadata and CSS support classic solid.
        assert css_present == (solid and free_solid), f"Metadata/CSS disagree: {name}"
        if css_present:
            assert glyphs[name] == record["unicode"].lower(), name
            assert glyphs[name] == glyphs[canonical], f"Alias glyph differs: {name}"

        alias = "N/A (absent)" if canonical is None else (
            f"Yes → `{canonical}`" if name != canonical else "No (canonical)"
        )
        rows.append([
            dish,
            f"`{classes}`",
            "Yes" if free_styles else "No",
            "Yes" if solid else "No",
            "Yes" if free_solid else "No",
            f"Yes (`U+{glyphs[name].upper()}`)" if css_present else "No",
            alias,
            f'`{record["label"]}`' if record else "N/A (absent)",
        ])

    print("| Dish | Class in baseline | Free set (metadata) | `classic.solid` entry | Free `classic.solid` | `all.css` selector / glyph | Alias → canonical | Official `label` |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
