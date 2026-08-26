"""Regression checks for startup globals used while loading plugins."""

from __future__ import annotations

import unittest
from pathlib import Path


class StartupDefaultTests(unittest.TestCase):
    def test_vps_noload_has_a_safe_default(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/utils/startup.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("VPS_NOLOAD = []", source)
        self.assertIn('VPS_NOLOAD = ["vps"]', source)


if __name__ == "__main__":
    unittest.main()
