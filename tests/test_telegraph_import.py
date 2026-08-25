"""Verifies that the modern Telegraph dependency is importable."""

from __future__ import annotations

import unittest


class TelegraphImportTests(unittest.TestCase):
    def test_telegraph_poster_v2_imports(self) -> None:
        from html_telegraph_poster_v2 import TelegraphPoster

        self.assertTrue(callable(TelegraphPoster))


if __name__ == "__main__":
    unittest.main()
