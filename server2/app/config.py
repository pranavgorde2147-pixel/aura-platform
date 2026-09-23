import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = Path("/models/Qwen3.5-4B")


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value if value is not None else None


class Settings:
    HOST = _get_env("HOST", "0.0.0.0")
    PORT = int(_get_env("PORT", "8001"))
    INTERNAL_API_TOKEN = _get_env("INTERNAL_API_TOKEN", "")
    MODEL_PATH = _get_env("MODEL_PATH", str(DEFAULT_MODEL_PATH))
    MODEL_NAME = _get_env("MODEL_NAME", "Qwen3.5-4B")


settings = Settings()
