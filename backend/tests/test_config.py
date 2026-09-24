import unittest
from unittest.mock import patch

from app.config import Settings, load_settings


class ConfigTests(unittest.TestCase):
    def test_load_settings_returns_notion_credentials(self):
        with patch.dict(
            "os.environ",
            {
                "NOTION_API_TOKEN": "secret-token",
                "NOTION_DATABASE_ID": "database-id",
            },
        ):
            settings = load_settings()

        self.assertEqual(
            settings,
            Settings(notion_api_token="secret-token", notion_database_id="database-id"),
        )

    def test_load_settings_rejects_missing_or_empty_credentials(self):
        for missing_variable in ("NOTION_API_TOKEN", "NOTION_DATABASE_ID"):
            with self.subTest(missing_variable=missing_variable):
                with patch.dict(
                    "os.environ",
                    {
                        "NOTION_API_TOKEN": "secret-token",
                        "NOTION_DATABASE_ID": "database-id",
                        missing_variable: " ",
                    },
                ):
                    with self.assertRaisesRegex(RuntimeError, missing_variable):
                        load_settings()


if __name__ == "__main__":
    unittest.main()
