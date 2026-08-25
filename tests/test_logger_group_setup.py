"""Checks for the explicit local logger-group creation option."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LoggerGroupSetupTests(unittest.TestCase):
    def test_setup_page_offers_opt_in_group_creation(self) -> None:
        source = (ROOT / "termux_setup.py").read_text(encoding="utf-8")
        self.assertIn('name="AUTO_CREATE_LOG_GROUPS"', source)
        self.assertIn("AUTO_CREATE_LOG_GROUPS = {auto_create_groups}", source)

    def test_runtime_creates_groups_only_when_explicitly_requested(self) -> None:
        source = (ROOT / "zlzl/__main__.py").read_text(encoding="utf-8")
        self.assertIn("async def ensure_requested_logger_groups", source)
        self.assertIn('getattr(Config, "AUTO_CREATE_LOG_GROUPS", False)', source)
        self.assertIn('addgvar("PRIVATE_GROUP_BOT_API_ID", str(group_id))', source)
        self.assertIn('addgvar("PM_LOGGER_GROUP_ID", str(group_id))', source)


if __name__ == "__main__":
    unittest.main()
