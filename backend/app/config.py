import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    notion_api_token: str
    notion_database_id: str


def load_settings() -> Settings:
    """Load and validate server-side configuration for the Notion integration."""
    load_dotenv(Path(__file__).parent.parent / ".env.local")

    missing = [
        name
        for name in ("NOTION_API_TOKEN", "NOTION_DATABASE_ID")
        if not os.getenv(name, "").strip()
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): " + ", ".join(missing)
        )

    return Settings(
        notion_api_token=os.environ["NOTION_API_TOKEN"].strip(),
        notion_database_id=os.environ["NOTION_DATABASE_ID"].strip(),
    )
