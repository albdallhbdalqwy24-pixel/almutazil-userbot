"""Regression checks for resilient command loading on Termux."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommandLoaderPolicyTests(unittest.TestCase):
    def test_failed_plugin_is_not_deleted(self) -> None:
        startup_source = (ROOT / "zlzl/utils/startup.py").read_text(encoding="utf-8")
        self.assertNotIn('os.remove(Path(f"{plugin_path}/{shortname}.py"))', startup_source)

    def test_basic_help_handlers_are_active(self) -> None:
        commands_source = (ROOT / "zlzl/plugins/الاوامر.py").read_text(encoding="utf-8")
        self.assertIn("(?:مساعدة|مساعده)", commands_source)
        self.assertIn("(?:اوامري|الاوامر|الأوامر)", commands_source)


if __name__ == "__main__":
    unittest.main()
