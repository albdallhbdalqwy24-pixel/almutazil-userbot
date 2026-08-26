"""Create a static inventory of registered ZTele command handlers."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (ROOT / "zlzl/plugins", ROOT / "zlzl/assistant")
OUTPUT = ROOT / "reports/command_inventory.json"
SUMMARY = ROOT / "reports/command_audit.md"


def expression_text(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return f"<dynamic:{ast.unparse(node)}>"


def decorator_pattern(decorator: ast.AST) -> str | None:
    if not isinstance(decorator, ast.Call):
        return None
    target = decorator.func
    if not (
        isinstance(target, ast.Attribute)
        and target.attr == "zed_cmd"
    ):
        return None
    for keyword in decorator.keywords:
        if keyword.arg == "pattern":
            return expression_text(keyword.value)
    if decorator.args:
        return expression_text(decorator.args[0])
    return "<missing-pattern>"


def collect_file(path: Path) -> list[dict[str, object]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as error:
        return [{"file": str(path.relative_to(ROOT)), "error": str(error)}]

    rows: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        patterns = [
            pattern
            for decorator in node.decorator_list
            if (pattern := decorator_pattern(decorator)) is not None
        ]
        for pattern in patterns:
            rows.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "line": node.lineno,
                    "handler": node.name,
                    "pattern": pattern,
                }
            )
    return rows


def main() -> None:
    rows: list[dict[str, object]] = []
    for source in SOURCES:
        for path in sorted(source.rglob("*.py")):
            rows.extend(collect_file(path))

    rows.sort(key=lambda row: (str(row.get("file", "")), int(row.get("line", 0))))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    handlers = [row for row in rows if "pattern" in row]
    errors = [row for row in rows if "error" in row]
    static_handlers = [
        row
        for row in handlers
        if not str(row["pattern"]).startswith("<")
    ]
    invalid_patterns: list[dict[str, object]] = []
    for row in static_handlers:
        try:
            re.compile(r"\." + str(row["pattern"]))
        except re.error as error:
            invalid_patterns.append({**row, "error": str(error)})

    by_folder: dict[str, int] = {}
    for row in handlers:
        folder = str(row["file"]).split("/")[1]
        by_folder[folder] = by_folder.get(folder, 0) + 1
    summary = [
        "# ZTele Command Audit",
        "",
        f"- Registered handlers: **{len(handlers)}**",
        f"- Static command patterns: **{len(static_handlers)}**",
        f"- Dynamic or event-only handlers: **{len(handlers) - len(static_handlers)}**",
        f"- Source parse errors: **{len(errors)}**",
        f"- Invalid static regex patterns: **{len(invalid_patterns)}**",
        "",
        "## Handlers by source folder",
        "",
        "| Folder | Handlers |",
        "|---|---:|",
        *[f"| {folder} | {count} |" for folder, count in sorted(by_folder.items())],
        "",
        "## Invalid static patterns",
        "",
        "None" if not invalid_patterns else "```json\n" + json.dumps(invalid_patterns, ensure_ascii=False, indent=2) + "\n```",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(
        f"handlers={len(handlers)} static={len(static_handlers)} "
        f"parse_errors={len(errors)} invalid_patterns={len(invalid_patterns)} "
        f"output={OUTPUT} summary={SUMMARY}"
    )


if __name__ == "__main__":
    main()
