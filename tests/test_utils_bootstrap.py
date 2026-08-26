"""Regression tests for the helpers.utils bootstrap import order."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


class UtilsBootstrapTests(unittest.TestCase):
    def test_zedutils_is_exported_before_optional_helper_imports(self) -> None:
        source_path = Path(__file__).resolve().parents[1] / "zlzl/helpers/utils/__init__.py"
        module = ast.parse(source_path.read_text(encoding="utf-8"))

        zedutils_line = next(
            node.lineno
            for node in module.body
            if isinstance(node, ast.ImportFrom)
            and node.module is None
            and any(alias.name == "utils" and alias.asname == "_zedutils" for alias in node.names)
        )
        loop_line = next(node.lineno for node in module.body if isinstance(node, ast.While))

        self.assertLess(zedutils_line, loop_line)


if __name__ == "__main__":
    unittest.main()
