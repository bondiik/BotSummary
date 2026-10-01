import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Переменная окружения {name} не задана")
    return value


API_ID: int = int(_require("API_ID"))
API_HASH: str = _require("API_HASH")
PHONE: str = _require("PHONE")
TG_PASSWORD: str | None = os.getenv("TG_PASSWORD") or None

NUMBER_RECENT_MESSAGES: int = int(_require("NUMBER_RECENT_MESSAGES"))

OPEN_ROUTER_KEY: str = _require("OPEN_ROUTER_KEY")
OPEN_ROUTER_MODEL: str = _require("OPEN_ROUTER_MODEL")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSION_PATH = DATA_DIR / "userbot"

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")