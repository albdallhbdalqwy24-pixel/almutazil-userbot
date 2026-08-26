"""Render's Telegraph layer must not import or install the legacy poster."""

from __future__ import annotations

import unittest
from pathlib import Path


class TelegraphRenderCompatTests(unittest.TestCase):
    def test_functions_uses_local_compatibility_layer(self) -> None:
        root = Path(__file__).resolve().parents[1]
        functions_source = (root / "zlzl/helpers/functions/functions.py").read_text(
            encoding="utf-8"
        )
        compat_source = (root / "zlzl/helpers/functions/telegraph_compat.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from .telegraph_compat import TelegraphPoster", functions_source)
        self.assertNotIn("html-telegraph-poster-v2", functions_source)
        self.assertIn("from telegraph import Telegraph", compat_source)


if __name__ == "__main__":
    unittest.main()
