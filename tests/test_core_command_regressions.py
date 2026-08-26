"""Regression checks for the basic commands that should always respond."""

from __future__ import annotations

import unittest
from pathlib import Path


class CoreCommandRegressionTests(unittest.TestCase):
    def test_help_accepts_common_arabic_spellings(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/plugins/الاوامر.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("(?:مساعدة|مساعده)", source)
        self.assertIn("(?:اوامري|الاوامر|الأوامر)", source)

    def test_status_initializes_template_values_without_saved_date(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/plugins/الفحص.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('zzt = ""', source)
        self.assertIn("zedda=zedda", source)
        self.assertIn('zzd = f"{bt.year}/{bt.month}/{bt.day}"', source)


if __name__ == "__main__":
    unittest.main()
