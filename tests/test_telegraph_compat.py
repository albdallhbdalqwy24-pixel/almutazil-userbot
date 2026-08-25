"""Regression checks for the modern Telegraph dependency used on Termux."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TelegraphCompatibilityTests(unittest.TestCase):
    def test_uses_python_3_14_compatible_telegraph_package(self) -> None:
        functions_source = (
            ROOT / "zlzl/helpers/functions/functions.py"
        ).read_text(encoding="utf-8")
        setup_source = (ROOT / "termux_setup.py").read_text(encoding="utf-8")

        self.assertIn("from html_telegraph_poster_v2 import TelegraphPoster", functions_source)
        self.assertIn('"html-telegraph-poster-v2"', setup_source)


if __name__ == "__main__":
    unittest.main()
