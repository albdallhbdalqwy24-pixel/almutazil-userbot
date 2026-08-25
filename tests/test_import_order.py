"""Regression checks for the zlzl startup import order."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ImportOrderTests(unittest.TestCase):
    def test_chatbot_loads_only_after_zedub_is_created(self) -> None:
        helper_init = (ROOT / "zlzl/helpers/__init__.py").read_text(encoding="utf-8")
        package_init = (ROOT / "zlzl/__init__.py").read_text(encoding="utf-8")

        self.assertNotIn("from .chatbot import *", helper_init)
        self.assertLess(
            package_init.index("from .core.session import zedub"),
            package_init.index("from .helpers.chatbot import *"),
        )


if __name__ == "__main__":
    unittest.main()
