"""Regression checks for dynamically installed third-party module names."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


class DependencyResolutionTests(unittest.TestCase):
    def test_dynamic_import_names_map_to_pypi_packages(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "zlzl/helpers/utils/extdl.py"
        ).read_text(encoding="utf-8")
        module = ast.parse(source)
        mapping = next(
            ast.literal_eval(node.value)
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "PIP_COMPATIBILITY_MAP" for target in node.targets)
        )
        self.assertEqual(mapping["git"], "GitPython")
        self.assertEqual(mapping["search_engine_parser"], "search-engine-parser")
        self.assertEqual(mapping["imdb"], "IMDbPY")


if __name__ == "__main__":
    unittest.main()
