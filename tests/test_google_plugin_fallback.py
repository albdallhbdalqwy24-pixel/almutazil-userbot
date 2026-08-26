"""Ensure the Google plugin can load without the legacy lxml<5 parser."""

from __future__ import annotations

import unittest
from pathlib import Path


class GooglePluginFallbackTests(unittest.TestCase):
    def test_legacy_search_parser_is_optional(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/plugins/جوجل.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("try:\n    from search_engine_parser", source)
        self.assertIn("except ModuleNotFoundError:", source)
        self.assertIn("if GoogleSearch is None:", source)


if __name__ == "__main__":
    unittest.main()
