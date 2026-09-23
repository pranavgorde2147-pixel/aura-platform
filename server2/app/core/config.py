import os
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "Qwen3.5-4B"


class Config:
    """Configuration for AURA Server 2 - Personal Brain."""

    # Service settings
    SERVICE_NAME: str = "AURA Personal Brain"
    SERVICE_VERSION: str = "0.1.0"
    HOST: str = os.getenv("AURA_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("AURA_PORT", "8002"))

    # Model settings
    MODEL_NAME: str = "Qwen3.5-4B"
    MODEL_PATH: str = os.getenv("AURA_MODEL_PATH", str(DEFAULT_MODEL_PATH))
    MODEL_DEVICE: str = os.getenv("AURA_MODEL_DEVICE", "cpu")
    MODEL_LOAD_IN_8BIT: bool = os.getenv("AURA_MODEL_LOAD_IN_8BIT", "false").lower() == "true"
    MODEL_TORCH_DTYPE: str = os.getenv("AURA_MODEL_TORCH_DTYPE", "bfloat16")

    # Security settings
    SERVICE_TOKEN: Optional[str] = os.getenv("AURA_SERVICE_TOKEN")
    REQUIRE_AUTH: bool = os.getenv("AURA_REQUIRE_AUTH", "true").lower() == "true"

    # Server 1 integration
    SERVER1_URL: Optional[str] = os.getenv("AURA_SERVER1_URL")
    SERVER1_VERIFY_IDENTITY: bool = os.getenv("AURA_SERVER1_VERIFY_IDENTITY", "true").lower() == "true"

    # Vault provider (future)
    VAULT_ENABLED: bool = os.getenv("AURA_VAULT_ENABLED", "false").lower() == "true"
    VAULT_URL: Optional[str] = os.getenv("AURA_VAULT_URL")

    # Logging
    LOG_LEVEL: str = os.getenv("AURA_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("AURA_LOG_FORMAT", "json")

    # Inference settings
    MAX_NEW_TOKENS: int = int(os.getenv("AURA_MAX_NEW_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("AURA_TEMPERATURE", "0.7"))
    TOP_P: float = float(os.getenv("AURA_TOP_P", "0.9"))
    TOP_K: int = int(os.getenv("AURA_TOP_K", "50"))

    # Development/Testing
    DEBUG: bool = os.getenv("AURA_DEBUG", "false").lower() == "true"
    USE_MOCK_MODEL: bool = os.getenv("AURA_USE_MOCK_MODEL", "false").lower() == "true"

    @classmethod
    def verify(cls):
        """Verify critical configuration."""
        model_path = Path(cls.MODEL_PATH)
        if not model_path.exists():
            raise ValueError(f"Model path does not exist: {cls.MODEL_PATH}")

        if cls.REQUIRE_AUTH and not cls.SERVICE_TOKEN:
            raise ValueError("AURA_SERVICE_TOKEN required when AURA_REQUIRE_AUTH=true")

    @property
    def model_dir(self) -> Path:
        return Path(self.MODEL_PATH)


# For backward compatibility
Settings = Config
