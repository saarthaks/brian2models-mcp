"""Fetch Brian2 examples from the docs and write them to ~/.brian2_models/models.json.

Also scans ~/.brian2_models/custom/ for user-added .py files.
Idempotent — reruns overwrite existing entries by id.
"""

import json
import re
from pathlib import Path

import requests

from .library import CUSTOM_DIR, LIBRARY_DIR, MODELS_FILE


def extract_docstring(source: str) -> str:
    """Extract the module-level docstring from a Python source file."""
    match = re.match(
        r'^(?:\s*#[^\n]*\n)*\s*(?:\'\'\'|"""|r""")(.*?)(?:\'\'\'|""")',
        source,
        re.DOTALL,
    )
    if match:
        return match.group(1).strip()
    return ""


SKIP_EXTENSIONS = {".npy", ".txt", ".md", ".mplstyle"}


def parse_example_links(html: str) -> list[str]:
    """Parse example names from the Brian2 examples index page.

    Links follow the pattern:
      CUBA.html                           -> CUBA
      advanced.COBAHH_approximated.html   -> advanced/COBAHH_approximated
      frompapers.Brette_2004.html         -> frompapers/Brette_2004

    Dots separate category from name; on GitHub these become directory separators.
    Filters out non-Python resources (.npy, .txt, .md, etc.).
    """
    # Match internal relative links ending in .html (exclude anchors, external, navigation)
    pattern = r'href="([A-Za-z][^"]*?\.html)"'
    matches = re.findall(pattern, html)

    names = []
    for href in matches:
        # Skip navigation/index links
        if href in ("index.html", "genindex.html"):
            continue
        if href.startswith("../") or href.startswith("http"):
            continue

        # Remove .html suffix
        name = href.removesuffix(".html")

        # Convert dots to slashes (category.example -> category/example)
        # But we need to figure out where the "path" part ends
        # The convention: the first dot separates category from the rest
        # e.g. "frompapers.Brette_2012.Fig1" -> "frompapers/Brette_2012/Fig1"
        path = name.replace(".", "/")

        # Skip non-Python resources (e.g. .npy, .txt, .md, .mplstyle files)
        skip = False
        for ext in SKIP_EXTENSIONS:
            if name.endswith(ext):
                skip = True
                break
        if skip:
            continue

        names.append(path)

    return list(dict.fromkeys(names))  # dedupe preserving order


def generate_tags(name: str) -> list[str]:
    """Generate basic tags from the example name and path."""
    tags = []
    if "/" in name:
        tags.append(name.split("/")[0])
    tags.append(name.rsplit("/", 1)[-1])
    return tags


EXAMPLES_INDEX = "https://brian2.readthedocs.io/en/stable/examples/index.html"
RAW_BASE = "https://raw.githubusercontent.com/brian-team/brian2/master/examples"


def fetch_examples() -> list[dict]:
    """Fetch all Brian2 examples from the docs and GitHub."""
    print("Fetching examples index...")
    resp = requests.get(EXAMPLES_INDEX, timeout=30)
    resp.raise_for_status()

    names = parse_example_links(resp.text)
    print(f"Found {len(names)} example links")

    models = []
    failed = []

    for name in names:
        url = f"{RAW_BASE}/{name}.py"
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            source = r.text
        except requests.RequestException as e:
            print(f"  FAILED: {name} — {e}")
            failed.append(name)
            continue

        docstring = extract_docstring(source)
        model_id = name.replace("/", "_")

        # For the docs URL, convert slashes back to dots
        docs_name = name.replace("/", ".")
        models.append({
            "id": model_id,
            "name": name.rsplit("/", 1)[-1],
            "docstring": docstring,
            "source": source,
            "origin_url": f"https://brian2.readthedocs.io/en/stable/examples/{docs_name}.html",
            "tags": generate_tags(name),
        })
        print(f"  OK: {name}")

    if failed:
        print(f"\n{len(failed)} examples failed to fetch")

    return models


def load_custom_models() -> list[dict]:
    """Scan ~/.brian2_models/custom/ for .py files and build model records."""
    if not CUSTOM_DIR.exists():
        return []

    models = []
    for py_file in sorted(CUSTOM_DIR.glob("*.py")):
        source = py_file.read_text(encoding="utf-8")
        docstring = extract_docstring(source)

        models.append({
            "id": py_file.stem,
            "name": py_file.stem,
            "docstring": docstring,
            "source": source,
            "origin_url": "custom",
            "tags": ["custom"],
        })
        print(f"  Custom: {py_file.stem}")

    return models


def seed():
    """Main seeding function."""
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)

    models = fetch_examples()
    custom = load_custom_models()

    # Merge: custom models take precedence by id
    models_by_id = {m["id"]: m for m in models}
    for cm in custom:
        models_by_id[cm["id"]] = cm

    all_models = list(models_by_id.values())

    MODELS_FILE.write_text(
        json.dumps(all_models, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nDone: {len(models)} models seeded, {len(custom)} custom models found.")
    print(f"Library written to {MODELS_FILE}")
