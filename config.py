import os
import yaml

from typing import Any, Dict


config_path = os.path.abspath(os.path.join(__file__, "../../config.yml"))

DEFAULT_TIMEOUT: float = 10.0
DEFAULT_ENDPOINT: str = "https://todo.pixegami.io"


class TestConfig:
    """For managing test configs and defining common constants"""

    def __init__(self, host_index: int = 0, config_file: str = config_path):
        self._host_index = host_index
        self._config_file = config_file

    @property
    def config_file_path(self) -> str:
        return self._config_file

    def _get_configs_dict(self) -> Dict[str, Any]:
        """Load config.yml into a dict"""
        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                configs = yaml.load(f, Loader=yaml.FullLoader)
                return configs or {}
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"config.yml file not found at: {self._config_file}. "
                f"Please make sure it exists."
            ) from e

    def get_host_url(self) -> str:
        """Return host url from config.yml, fallback to DEFAULT_ENDPOINT"""
        configs = self._get_configs_dict()
        try:
            return configs["hosts"][self._host_index]["url"].rstrip("/")
        except (KeyError, IndexError, TypeError):
            return DEFAULT_ENDPOINT


# Expose constants for quick use in tests
CONFIG = TestConfig()
ENDPOINT: str = CONFIG.get_host_url()
