"""Regression tests for the Render setup page without real Telegram values."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ["SETUP_PASSWORD"] = "test-password"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from render_setup_web import app, build_environment


class RenderSetupTests(unittest.TestCase):
    def test_health_endpoint_does_not_expose_configuration(self) -> None:
        response = app.test_client().get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"API_HASH", response.data)

    def test_environment_keeps_secrets_in_memory(self) -> None:
        environment = build_environment(
            {
                "APP_ID": "12345",
                "API_HASH": "hash-value",
                "STRING_SESSION": "session-value",
                "TG_BOT_TOKEN": "token-value",
                "OWNER_ID": "67890",
                "PRIVATE_GROUP_BOT_API_ID": "0",
                "PM_LOGGER_GROUP_ID": "0",
            }
        )
        self.assertEqual(environment["ZELZAL_A"], "0")
        self.assertEqual(environment["AUTO_CREATE_LOG_GROUPS"], "false")
        self.assertEqual(environment["DATABASE_URL"], "sqlite:///render_runtime.db")


if __name__ == "__main__":
    unittest.main()
