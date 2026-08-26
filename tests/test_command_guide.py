"""Verify the generated Arabic command guide covers the inventory."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommandGuideTests(unittest.TestCase):
    def test_guide_is_generated_from_the_full_inventory(self) -> None:
        subprocess.run(
            [sys.executable, "tools/generate_command_guide.py"],
            cwd=ROOT,
            check=True,
        )
        guide = (ROOT / "docs/دليل_الأوامر_الحالية.md").read_text(encoding="utf-8")
        self.assertIn("جميع المعالجات المسجلة (548)", guide)
        self.assertIn("`.حالة الاوامر`", guide)
        self.assertIn("إضافة: الاوامر", guide)
        self.assertIn("مراقب تلقائي للأحداث", guide)
        self.assertIn("`.ث1` للصورة و`.ث2` للفيديو", guide)


if __name__ == "__main__":
    unittest.main()
