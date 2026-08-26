"""Verify uploaded theme assets remain paired with their Telegram commands."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ThemeAssetTests(unittest.TestCase):
    def test_photo_and_video_assets_exist(self) -> None:
        assets = ROOT / "zlzl/theme_assets"
        self.assertTrue((assets / "theme-photo-1.jpg").is_file())
        self.assertTrue((assets / "theme-video-2.mp4").is_file())

    def test_local_theme_commands_are_mapped(self) -> None:
        source = (ROOT / "zlzl/plugins/ثيمات_بديل.py").read_text(encoding="utf-8")
        self.assertIn('"ث1": ("theme-photo-1.jpg"', source)
        self.assertIn('"ث2": ("theme-video-2.mp4"', source)
        self.assertIn("event.client.send_file", source)


if __name__ == "__main__":
    unittest.main()
