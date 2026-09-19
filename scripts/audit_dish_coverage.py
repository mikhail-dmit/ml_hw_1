"""Exhaustively search two extracted icon packages; print dish-named coverage."""

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def strings(value, prefix=""):
    """Visit every string value in official metadata, retaining its field path."""
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, f"{prefix}.{key}".strip("."))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f"{prefix}.{index}".strip("."))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fontawesome", type=Path)
    parser.add_argument("lucide", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    fa, lu = args.fontawesome, args.lucide
    assert load_json(fa / "package.json")["version"] == "6.4.0"
    assert load_json(fa / "package.json")["name"] == "@fortawesome/fontawesome-free"
    assert load_json(lu / "package.json")["version"] == "1.47.0"
    assert load_json(lu / "package.json")["name"] == "lucide-static"

    metadata = load_json(fa / "metadata/icon-families.json")
    assert all(record["familyStylesByLicense"]["free"] for record in metadata.values())
    fa_names = {
        name: canonical
        for canonical, record in metadata.items()
        for name in [canonical, *record.get("aliases", {}).get("names", [])]
    }
    css_names = set(re.findall(r"\.fa-([\w-]+)::?before\b", (fa / "css/all.css").read_text()))
    assert set(fa_names) == css_names, "Font Awesome CSS/metadata name lists disagree"
    fa_svgs = list((fa / "svgs").glob("*/*.svg"))
    assert {file.stem for file in fa_svgs} == set(metadata)

    tags = load_json(lu / "tags.json")
    nodes = load_json(lu / "icon-nodes.json")
    assert set(tags) == set(nodes), "Lucide canonical geometry/metadata lists disagree"
    lu_svgs = {file.stem: file for file in (lu / "icons").glob("*.svg")}
    assert set(tags) <= set(lu_svgs)

    # Check every additional SVG name has a canonical counterpart with the same geometry.
    def shape(file):
        return tuple(
            (el.tag, tuple(sorted((key, value) for key, value in el.attrib.items() if key != "class")))
            for el in ET.fromstring(file.read_text()).iter()
        )

    canonical_shapes = {shape(lu_svgs[name]) for name in tags}
    assert all(shape(lu_svgs[name]) in canonical_shapes for name in set(lu_svgs) - set(tags))

    baseline = Path(__file__).resolve().parents[1] / "baseline/index.html"
    menu = re.search(r"const lunchMenu = \[(.*?)\];", baseline.read_text(), re.S)[1]
    dishes = re.findall(r'name: "([^"]+)"', menu)
    assert len(dishes) == 12 and len(set(dishes)) == 12

    # The broad pass preserves substring hits; the named pass uses explicit whole tokens.
    queries = {dish: [dish.casefold()] for dish in dishes}
    queries["Tacos"] = ["taco"]
    queries["BBQ"] = ["bbq", "barbecue", "barbeque"]
    tokens = {
        "Pizza": {"pizza", "pizzas"}, "Sushi": {"sushi"},
        "Burger": {"burger", "burgers", "hamburger", "hamburgers", "cheeseburger", "cheeseburgers"},
        "Salad": {"salad", "salads"}, "Tacos": {"taco", "tacos"},
        "Ramen": {"ramen"}, "Sandwich": {"sandwich", "sandwiches"},
        "Pasta": {"pasta", "pastas"}, "Curry": {"curry", "curries"},
        "Steak": {"steak", "steaks"}, "Soup": {"soup", "soups"},
        "BBQ": {"bbq", "barbecue", "barbecues", "barbeque", "barbeques"},
    }
    # Include the irregular plural in the broad pass too.
    queries["Curry"].append("curries")
    libraries = {
        "Font Awesome 6.4.0": {
            "names": sorted(fa_names),
            "fields": {name: list(strings(record)) for name, record in metadata.items()},
            "labels": {name: record["label"] for name, record in metadata.items()},
            "canonicalIconCount": len(metadata), "nameCountIncludingAliases": len(fa_names),
            "svgFileCountIncludingStyles": len(fa_svgs),
        },
        "Lucide Static 1.47.0": {
            "names": sorted(lu_svgs),
            "fields": {name: list(strings({"tags": values})) for name, values in tags.items()},
            "labels": {},
            "canonicalIconCount": len(tags), "nameCountIncludingAliases": len(lu_svgs),
            "svgFileCountIncludingAliases": len(lu_svgs),
        },
    }

    rows = []
    for dish in dishes:
        def broad(text):
            return any(query in text.casefold() for query in queries[dish])

        def named(text):
            return bool(set(re.findall(r"[a-z]+", text.casefold())) & tokens[dish])

        for library, data in libraries.items():
            name_hits = [name for name in data["names"] if broad(name)]
            metadata_hits = [
                {"icon": name, "field": field, "value": value}
                for name, fields in data["fields"].items()
                for field, value in fields if broad(value)
            ]
            named_names = [name for name in data["names"] if named(name)]
            named_labels = {name: label for name, label in data["labels"].items() if named(label)}
            rows.append({
                "dish": dish, "library": library,
                "queries": queries[dish], "namedTokens": sorted(tokens[dish]),
                "nameSubstringHits": name_hits, "metadataSubstringHits": metadata_hits,
                "dishNamedIcons": named_names, "dishNamedLabels": named_labels,
                "hasDishNamedGlyph": bool(named_names or named_labels),
                "hasWholeTokenNameOrMetadataHit": bool(named_names or any(named(hit["value"]) for hit in metadata_hits)),
            })

    report = {
        "libraries": {
            name: {key: value for key, value in data.items() if key not in {"names", "fields", "labels"}}
            for name, data in libraries.items()
        },
        "totalsDishNamed": {name: sum(row["hasDishNamedGlyph"] for row in rows if row["library"] == name) for name in libraries},
        "totalsAnyWholeTokenHit": {name: sum(row["hasWholeTokenNameOrMetadataHit"] for row in rows if row["library"] == name) for name in libraries},
        "noneNamedInEither": [dish for dish in dishes if not any(row["hasDishNamedGlyph"] for row in rows if row["dish"] == dish)],
        "noWholeTokenHitInEither": [dish for dish in dishes if not any(row["hasWholeTokenNameOrMetadataHit"] for row in rows if row["dish"] == dish)],
        "sha256": {
            "baseline/index.html": digest(baseline),
            "fontawesome/package/metadata/icon-families.json": digest(fa / "metadata/icon-families.json"),
            "fontawesome/package/css/all.css": digest(fa / "css/all.css"),
            "lucide/package/tags.json": digest(lu / "tags.json"),
            "lucide/package/icon-nodes.json": digest(lu / "icon-nodes.json"),
        },
        "rows": rows,
    }
    if args.json_output:
        args.json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("| Dish | Library | Name/alias substring hits | Official label/metadata substring hits | Dish-named glyph? |")
    print("| --- | --- | --- | --- | --- |")
    for row in rows:
        metadata_matches = {}
        for hit in row["metadataSubstringHits"]:
            metadata_matches.setdefault(hit["icon"], set()).add(hit["value"])
        names = ", ".join(f"`{name}`" for name in row["nameSubstringHits"]) or "None"
        values = "; ".join(f"`{name}`: " + ", ".join(f"`{value}`" for value in sorted(values)) for name, values in metadata_matches.items()) or "None"
        print(f'| {row["dish"]} | {row["library"]} | {names} | {values} | {"Yes" if row["hasDishNamedGlyph"] else "No"} |')
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
