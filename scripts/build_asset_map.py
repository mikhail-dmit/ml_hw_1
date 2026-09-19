"""Screen all baseline icons from vendored metadata and apply explicit human reviews."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor/fontawesome-free-6.4.0"
FALLBACKS = {
    "Pizza": "🍕", "Sushi": "🍣", "Burger": "🍔", "Salad": "🥗",
    "Tacos": "🌮", "Ramen": "🍜", "Sandwich": "🥪", "Pasta": "🍝",
    "Curry": "🍛", "Steak": "🥩", "Soup": "🍲", "BBQ": "🍖",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_table(headers, rows):
    def line(cells):
        return "| " + " | ".join(str(cell).replace("|", "\\|").replace("\n", " ") for cell in cells) + " |"
    return "\n".join([line(headers), line(["---"] * len(headers)), *[line(row) for row in rows]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-only", action="store_true", help="Print mechanical results and REVIEW rows without generating files")
    parser.add_argument("--decisions", type=Path, default=ROOT / "evidence/06-review-decisions.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/06-asset-map.md")
    args = parser.parse_args()

    baseline = ROOT / "baseline/index.html"
    metadata_path = VENDOR / "metadata/icon-families.json"
    categories_path = VENDOR / "metadata/categories.yml"
    manifest = json.loads((VENDOR / "package.json").read_text())
    assert (manifest["name"], manifest["version"]) == ("@fortawesome/fontawesome-free", "6.4.0")
    metadata = json.loads(metadata_path.read_text())
    categories = yaml.safe_load(categories_path.read_text())
    assert "food-beverage" in categories
    aliases = {}
    for canonical, record in metadata.items():
        for alias in record.get("aliases", {}).get("names", []):
            assert alias not in metadata and alias not in aliases, alias
            aliases[alias] = canonical

    source = baseline.read_text()
    menu = re.search(r"const lunchMenu = \[(.*?)\];", source, re.S)[1]
    entries = re.findall(r'{ name: "([^"]+)", icon: "([^"]+)" }', menu)
    assert len(entries) == 12 and len({dish for dish, _ in entries}) == 12
    assert set(FALLBACKS) == {dish for dish, _ in entries}, "Fallbacks must cover the complete menu"
    rows = []
    review_log = []
    for dish, baseline_class in entries:
        style, icon_class = baseline_class.split()
        assert style == "fas" and icon_class.startswith("fa-")
        name = icon_class[3:]
        canonical = name if name in metadata else aliases.get(name)
        record = metadata.get(canonical, {})
        free_solid = (
            {"family": "classic", "style": "solid"} in record.get("familyStylesByLicense", {}).get("free", [])
            and "solid" in record.get("svgs", {}).get("classic", {})
        )
        memberships = sorted(category for category, info in categories.items() if canonical in info["icons"])
        food = "food-beverage" in memberships
        needs_review = bool(canonical and free_solid and food)
        alias_status = "Absent" if canonical is None else (
            f"Alias `{name}` → `{canonical}`" if canonical != name else f"Canonical `{canonical}`"
        )
        failures = []
        if not canonical:
            failures.append("(a) Name is neither a canonical icon nor a declared alias")
        elif not free_solid:
            failures.append("(a) No free classic.solid entry")
        if not food:
            failures.append("(b) Not listed in food-beverage")
        row = {
            "dish": dish, "baseline_class": baseline_class, "canonical": canonical,
            "exists": canonical is not None, "alias_status": alias_status,
            "categories": memberships, "label": record.get("label", "N/A (absent)"),
            "free_solid": free_solid, "needs_review": needs_review,
            "verdict": "REVIEW" if needs_review else "EMOJI", "failures": failures,
        }
        rows.append(row)
        if needs_review:
            review_log.append(f'REVIEW | {dish} | {baseline_class} | official label: {row["label"]} | (a) PASS | (b) PASS')

    def result_table():
        return markdown_table(
            ["Dish", "Baseline class", "Exists", "Canonical or alias", "Categories", "Official label", "Verdict"],
            [[row["dish"], f'`{row["baseline_class"]}`', "Yes" if row["exists"] else "No",
              row["alias_status"], ", ".join(row["categories"]) or "None",
              row["label"], row["verdict"]] for row in rows],
        )

    print("\n".join(review_log))
    if args.review_only:
        print(result_table())
        return

    decisions = json.loads(args.decisions.read_text())
    assert decisions["reviewer"].strip(), "An explicit reviewer is required"
    assert decisions["criterionInterpretation"].strip(), "Record the human interpretation of rule (c)"
    assert set(decisions["reviews"]) == {row["dish"] for row in rows if row["needs_review"]}, "Every REVIEW row must have exactly one decision"
    review_rows = []
    review_notes = []
    for row in rows:
        if not row["needs_review"]:
            continue
        decision = decisions["reviews"][row["dish"]]
        assert decision["baselineClass"] == row["baseline_class"]
        assert decision["officialLabel"] == row["label"], "Reviewed label must match vendored metadata"
        assert decision["verdict"] in {"KEEP-FA", "EMOJI"}
        assert decision["justification"].strip() and "\n" not in decision["justification"]
        row["verdict"] = decision["verdict"]
        review_rows.append([row["dish"], row["label"], row["verdict"], decision["justification"]])
        print(f'DECISION | {row["dish"]} | {row["verdict"]} | {decision["justification"]}')
        for key, title in (("reasoning", "Human reasoning"), ("userProvidedReference", "User-provided reference"), ("recordedObjection", "Recorded objection")):
            if key in decision:
                note = f'**{row["dish"]} — {title}:** {decision[key]}'
                review_notes.append(note)
                print(f'NOTE | {row["dish"]} | {title} | {decision[key]}')

    assignments = [
        [row["dish"], "font-awesome" if row["verdict"] == "KEEP-FA" else "emoji",
         f'fas fa-{row["canonical"]}' if row["verdict"] == "KEEP-FA" else FALLBACKS[row["dish"]]]
        for row in rows
    ]
    assert [dish for dish, _, _ in assignments] == [dish for dish, _ in entries], "No menu item may be removed or reordered"
    assert len(assignments) == 12 and all(value for _, _, value in assignments)
    fa_count = sum(kind == "font-awesome" for _, kind, _ in assignments)
    emoji_count = len(assignments) - fa_count
    alias_rows = [row for row in rows if row["exists"] and row["baseline_class"].split()[1][3:] != row["canonical"]]

    # Establish the mechanical eligibility and official labels of the rejected generic substitutes too.
    bowl_labels = []
    for name in ("bowl-food", "bowl-rice"):
        record = metadata[name]
        assert {"family": "classic", "style": "solid"} in record["familyStylesByLicense"]["free"]
        assert "solid" in record["svgs"]["classic"]
        assert name in categories["food-beverage"]["icons"]
        bowl_labels.append(f'`{name}` (official label: **{record["label"]}**)')

    report = [
        "# Asset assignment for all 12 dishes",
        "Generated by `scripts/build_asset_map.py` from the unchanged baseline, vendored Font Awesome 6.4.0 metadata, and explicit review decisions. The tables are computed; no menu entries are removed.",
        "## Inputs and rules",
        "- (a) Resolve a canonical metadata key or `aliases.names` entry; require both a `svgs.classic.solid` entry and the classic/solid pair under `familyStylesByLicense.free`.\n"
        "- (b) Require the resolved canonical name in the `food-beverage` icon list in `metadata/categories.yml`. All category memberships are reported.\n"
        "- (c) Every mechanically eligible icon is printed as REVIEW with its exact official label. Only an explicit human KEEP-FA decision can retain it; a rejected or mechanically ineligible icon receives an emoji.\n"
        "- A retained Font Awesome alias is emitted using its canonical v6 class. The input alias remains visible as a latent naming defect.\n"
        "- Emoji are explicit Unicode fallback choices, not Font Awesome metadata or guessed CSS names. They use the operating system's emoji font stack.",
        "## Computed class audit (resolved verdicts)", result_table(),
        "## Mechanical rejections",
        markdown_table(["Dish", "Reason"], [[row["dish"], "; ".join(row["failures"])] for row in rows if not row["needs_review"]]),
        "## REVIEW log and explicit decisions",
        f'Reviewer: **{decisions["reviewer"]}**. Decision input: `{args.decisions.name}`.',
        f'Human interpretation of (c): {decisions["criterionInterpretation"]}',
        "```text\n" + "\n".join(review_log) + "\n```",
        markdown_table(["Dish", "Official label", "Decision", "One-line justification"], review_rows),
        *review_notes,
        "## Alias findings",
        "\n".join(f'- {row["dish"]}: {row["alias_status"]}; final verdict: {row["verdict"]}.' for row in alias_rows),
        "## Final assignment",
        markdown_table(["Dish", "Asset type", "Value"], assignments),
        "## Coverage",
        f'**{len(assignments)}/12 dishes retain an assigned visual asset**, comprising **{fa_count}/12 Font Awesome** and **{emoji_count}/12 emoji** assignments. All 12 original dishes survive in their original order.',
        f'The {fa_count}/12 admissible Font Awesome assignments show that the original assumption of complete dedicated library coverage was false; Unicode fallbacks restore the full 12/12 assignment without shrinking the menu.',
        "## Why generic bowls were not substituted",
        f'{bowl_labels[0]} and {bowl_labels[1]} pass the existence/free-style and food-beverage tests, but their labels identify generic food or rice in a bowl rather than Ramen or Soup. A bowl of food could equally represent either dish, and a rice bowl could also suggest Curry or another rice-based meal; category membership therefore does not satisfy the distinguishing-dish requirement in (c). They were not substituted for failed baseline classes. Ramen and Soup instead receive separate Unicode fallbacks in the assignment above.',
        "## Reproduce",
        "```bash\npython3 -m pip install -r scripts/requirements.txt\npython3 scripts/build_asset_map.py --review-only\npython3 scripts/build_asset_map.py\n```",
        "## Source SHA-256",
        "```text\n" + "\n".join(f'{sha256(file)}  {file.relative_to(ROOT) if file.is_relative_to(ROOT) else file.name}' for file in (baseline, metadata_path, categories_path, args.decisions)) + "\n```",
    ]
    args.output.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    print(result_table())
    print(markdown_table(["Dish", "Asset type", "Value"], assignments))
    print(f"Coverage: {len(assignments)}/12; Font Awesome: {fa_count}/12; emoji: {emoji_count}/12")


if __name__ == "__main__":
    main()
