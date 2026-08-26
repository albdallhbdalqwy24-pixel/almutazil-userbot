"""Regression tests for helper bootstrap retry counters."""

from __future__ import annotations

import unittest
from pathlib import Path


class HelperInstallAttemptsTests(unittest.TestCase):
    def test_helper_bootstraps_use_private_retry_counter(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative_path in ("zlzl/helpers/__init__.py", "zlzl/helpers/utils/__init__.py"):
            source = (root / relative_path).read_text(encoding="utf-8")
            self.assertIn("_install_attempts = 0", source)
            self.assertIn("_install_attempts += 1", source)
            self.assertNotIn("\ncheck = 0", source)

    def test_helpers_bootstrap_does_not_import_private_utils_symbols(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "zlzl/helpers/__init__.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("from .utils import _zedtools", source)
        self.assertNotIn("from .utils import _zedutils", source)
        self.assertNotIn("from .utils import _format", source)


if __name__ == "__main__":
    unittest.main()
