"""Configuration loader for Smart Music Tagger."""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage application configuration from .env file."""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration loader.

        Args:
            env_file: Path to .env file (default: .env)
        """
        self.env_file = env_file
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from .env file."""
        if not os.path.exists(self.env_file):
            raise FileNotFoundError(
                f"Configuration file '{self.env_file}' not found.\n"
                "Please create .env file by copying .env.example:\n"
                "  cp .env.example .env\n"
                "Then fill in your actual values."
            )

        load_dotenv(self.env_file)
        self._load_env_variables()

    def _load_env_variables(self):
        """Load configuration from environment variables."""
        env_mapping = {
            'GROQ_API_KEY': 'groq_api_key',
            'GROQ_API_URL': 'groq_api_url',
            'GROQ_MODEL': 'groq_model',
            'GROQ_REQUEST_DELAY_SECONDS': 'groq_request_delay_seconds',
            'MUSIC_DIRECTORY': 'music_directory',
        }

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                self.config[config_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (supports nested keys with dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def validate(self) -> bool:
        """
        Validate required configuration values.

        Returns:
            True if all required values are present
        """
        required_keys = ['groq_api_key', 'groq_api_url', 'groq_model', 'music_directory']
        missing_keys = []

        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

        music_dir = Path(self.get('music_directory'))
        if not music_dir.exists():
            raise ValueError(f"Music directory does not exist: {music_dir}")

        return True

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()
