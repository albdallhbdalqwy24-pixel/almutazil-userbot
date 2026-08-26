"""Ensure the static command audit finds no malformed registered patterns."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommandAuditTests(unittest.TestCase):
    def test_registered_command_patterns_compile(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/audit_command_inventory.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("parse_errors=0", completed.stdout)
        self.assertIn("invalid_patterns=0", completed.stdout)
        summary = (ROOT / "reports/command_audit.md").read_text(encoding="utf-8")
        self.assertIn("Registered handlers:", summary)


if __name__ == "__main__":
    unittest.main()
