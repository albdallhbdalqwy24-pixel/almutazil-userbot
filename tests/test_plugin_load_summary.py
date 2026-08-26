"""Regression checks for transparent command/plugin loading feedback."""

from __future__ import annotations

import unittest
from pathlib import Path


class PluginLoadSummaryTests(unittest.TestCase):
    def test_loader_records_successes_and_failures(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/utils/startup.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("PLUGIN_LOAD_SUMMARY", source)
        self.assertIn("NON_INSTALLABLE_PLUGIN_MODULES", source)
        self.assertIn("ملخص تحميل", source)

    def test_theme_fallback_replies_instead_of_silently_failing(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/plugins/ثيمات_بديل.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"ث1": ("theme-photo-1.jpg"', source)
        self.assertIn('"ث2": ("theme-video-2.mp4"', source)
        self.assertIn("هذا الثيم لم تُضف له صورة أو فيديو بعد", source)

    def test_command_load_status_is_registered(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/plugins/الاوامر.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("حالة (?:الاوامر|الأوامر)", source)
        self.assertIn("PLUGIN_LOAD_SUMMARY", source)


if __name__ == "__main__":
    unittest.main()
