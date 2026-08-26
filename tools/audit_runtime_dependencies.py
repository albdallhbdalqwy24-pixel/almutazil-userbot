"""List third-party imports used by command modules but missing at runtime."""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (ROOT / "zlzl/plugins", ROOT / "zlzl/assistant")
OUTPUT = ROOT / "reports/missing_runtime_dependencies.json"
SUMMARY = ROOT / "reports/runtime_dependency_audit.md"
STDLIB = set(getattr(sys, "stdlib_module_names", ()))
LOCAL_ROOTS = {"zlzl", "plugins", "assistant"}
RENDER_PROVIDES = {
    "barcode": "python-barcode",
    "cloudscraper": "cloudscraper",
    "geopy": "geopy",
    "gtts": "gTTS",
    "hachoir": "hachoir",
    "justwatch": "justwatch",
    "lottie": "lottie",
    "prettytable": "prettytable",
    "pySmartDL": "pySmartDL",
    "pyfiglet": "pyfiglet",
    "pymediainfo": "pymediainfo",
    "qrcode": "qrcode[pil]",
    "selenium": "selenium",
    "spamwatch": "spamwatch",
    "speedtest": "speedtest-cli",
    "telegraph": "telegraph",
    "wget": "wget",
    "youtube_search": "youtube-search",
}


def imports_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def is_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def main() -> None:
    usage: dict[str, list[str]] = defaultdict(list)
    for source in SOURCES:
        for path in sorted(source.rglob("*.py")):
            for module in imports_in(path):
                if module in STDLIB or module in LOCAL_ROOTS or module == "__future__":
                    continue
                usage[module].append(str(path.relative_to(ROOT)))

    requirements = (ROOT / "requirements-render.txt").read_text(encoding="utf-8")
    provisioned = {
        module: RENDER_PROVIDES[module]
        for module in sorted(usage)
        if module in RENDER_PROVIDES and RENDER_PROVIDES[module] in requirements
    }
    missing = {
        module: sorted(paths)
        for module, paths in sorted(usage.items())
        if not is_available(module) and module not in provisioned
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(missing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# ZTele Runtime Dependency Audit",
        "",
        f"- Third-party import roots: **{len(usage)}**",
        f"- Dependencies provided by Render requirements: **{len(provisioned)}**",
        f"- Dependencies not packaged for Render: **{len(missing)}**",
        "",
        "## Not packaged for Render",
        "",
        "None" if not missing else "```json\n" + json.dumps(missing, ensure_ascii=False, indent=2) + "\n```",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(
        f"third_party_modules={len(usage)} provisioned_modules={len(provisioned)} "
        f"missing_modules={len(missing)} output={OUTPUT} summary={SUMMARY}"
    )
    for module in missing:
        print(module)


if __name__ == "__main__":
    main()
