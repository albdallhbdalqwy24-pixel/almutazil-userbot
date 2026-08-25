"""Regression checks for Python 3.14 Termux compatibility mappings."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

EXTDL_PATH = Path(__file__).resolve().parents[1] / "zlzl/helpers/utils/extdl.py"
SPEC = importlib.util.spec_from_file_location("termux_extdl", EXTDL_PATH)
extdl = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(extdl)


class TermuxCompatibilityTests(unittest.TestCase):
    def test_removed_cgi_module_uses_compatibility_package(self) -> None:
        self.assertEqual(extdl.resolve_pip_package("cgi"), "legacy-cgi")

    def test_unrelated_module_name_is_unchanged(self) -> None:
        self.assertEqual(extdl.resolve_pip_package("requests"), "requests")

    def test_setup_installs_lxml_clean_split_package(self) -> None:
        setup_source = (Path(__file__).resolve().parents[1] / "termux_setup.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"lxml_html_clean"', setup_source)


if __name__ == "__main__":
    unittest.main()
