"""Verify dependencies previously installed during userbot startup are present."""

from __future__ import annotations

import importlib
import unittest


class RenderRuntimeDependenciesTests(unittest.TestCase):
    def test_startup_dependencies_import_without_internal_pip(self) -> None:
        modules = (
            "git",
            "imdb",
            "wand",
            "colour",
            "emoji",
            "googletrans",
            "jikanpy",
            "lyricsgenius",
            "markdown",
            "motor",
            "moviepy",
            "search_engine_parser",
            "ujson",
            "urlextract",
        )
        for module_name in modules:
            with self.subTest(module=module_name):
                self.assertIsNotNone(importlib.import_module(module_name))


if __name__ == "__main__":
    unittest.main()
