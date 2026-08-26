"""Regression checks for the private-message storage monitor."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StorageMonitorGuardTests(unittest.TestCase):
    def test_missing_sender_is_skipped_before_bot_property_access(self) -> None:
        source = (ROOT / "zlzl/plugins/التخزين.py").read_text(encoding="utf-8")
        self.assertIn("if sender is None or sender.bot:", source)
        self.assertLess(
            source.index("if sender is None or sender.bot:"),
            source.index("if not sender.bot:"),
        )


if __name__ == "__main__":
    unittest.main()
