"""Focused tests for the local Termux setup wizard."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import termux_setup


class TermuxSetupTests(unittest.TestCase):
    def test_write_config_preserves_full_group_ids_and_secret_strings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "config.py"
            original_path = termux_setup.CONFIG_PATH
            termux_setup.CONFIG_PATH = config_path
            try:
                termux_setup.write_config(
                    {
                        "APP_ID": "123456",
                        "API_HASH": "example-api-hash",
                        "STRING_SESSION": "example-string-session",
                        "TG_BOT_TOKEN": "example-bot-token",
                        "PRIVATE_GROUP_BOT_API_ID": "-1004451374841",
                        "PM_LOGGER_GROUP_ID": "-1004449370115",
                        "OWNER_ID": "0",
                        "ALIVE_NAME": "اختبار",
                        "TZ": "Asia/Riyadh",
                    }
                )
                generated = config_path.read_text(encoding="utf-8")
                self.assertIn("APP_ID = 123456", generated)
                self.assertIn("API_HASH = 'example-api-hash'", generated)
                self.assertIn("DB_URI = 'sqlite:///almutazil.db'", generated)
                self.assertIn("PRIVATE_GROUP_BOT_API_ID = -1004451374841", generated)
                self.assertIn("PM_LOGGER_GROUP_ID = -1004449370115", generated)
                self.assertNotIn("-100100", generated)
                self.assertEqual(config_path.stat().st_mode & 0o777, 0o600)
            finally:
                termux_setup.CONFIG_PATH = original_path

    def test_phone_normalization_handles_arabic_digits(self) -> None:
        self.assertEqual(
            termux_setup.normalize_phone("＋٩٦٦ ٥٠-١٢٣-٤٥٦٧"),
            "+966501234567",
        )

    def test_main_page_mentions_local_session_creation(self) -> None:
        page = termux_setup.page().decode("utf-8")
        self.assertIn("127.0.0.1", page)
        self.assertIn("استخراج String Session", page)


if __name__ == "__main__":
    unittest.main()
