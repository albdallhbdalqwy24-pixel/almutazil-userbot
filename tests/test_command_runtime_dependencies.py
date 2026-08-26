"""Regression checks for dependencies needed by registered command modules."""

from __future__ import annotations

import unittest
from pathlib import Path
import subprocess
import sys


class CommandRuntimeDependencyTests(unittest.TestCase):
    def test_render_requirements_cover_known_command_imports(self) -> None:
        requirements = (Path(__file__).resolve().parents[1] / "requirements-render.txt").read_text(
            encoding="utf-8"
        )
        for requirement in (
            "python-barcode",
            "cloudscraper",
            "geopy",
            "gTTS",
            "hachoir",
            "justwatch",
            "lottie",
            "prettytable",
            "pySmartDL",
            "pyfiglet",
            "pymediainfo",
            "qrcode[pil]",
            "selenium",
            "spamwatch",
            "speedtest-cli",
            "wget",
            "youtube-search",
        ):
            self.assertIn(requirement, requirements)

    def test_client_does_not_leave_command_errors_silent(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/core/client.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("تعذر تنفيذ هذا الأمر حالياً", source)

    def test_dependency_audit_has_only_the_handled_legacy_theme_package_missing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, "tools/audit_runtime_dependencies.py"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("missing_modules=1", completed.stdout)
        missing = (root / "reports/missing_runtime_dependencies.json").read_text(
            encoding="utf-8"
        )
        self.assertIn('"zedthon"', missing)


if __name__ == "__main__":
    unittest.main()
