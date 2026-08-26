"""Regression checks for one-time logger group creation feedback."""

from __future__ import annotations

import unittest
from pathlib import Path


class LoggerGroupCreationLogsTests(unittest.TestCase):
    def test_startup_logs_created_group_identifiers(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/__main__.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("السجل={Config.PRIVATE_GROUP_BOT_API_ID}", source)
        self.assertIn("التخزين={Config.PM_LOGGER_GROUP_ID}", source)


if __name__ == "__main__":
    unittest.main()
