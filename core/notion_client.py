import os
import json
from typing import Optional
from pathlib import Path

class NotionClient:
    """Shared Notion API client for syncing markdown content"""

    def __init__(self):
        """Initialize NotionClient with configuration from file and environment"""
        self.api_key = os.environ.get('NOTION_API_KEY')
        self.debug = os.environ.get('NOTION_DEBUG', 'false').lower() == 'true'
        self.dry_run = os.environ.get('NOTION_DRY_RUN', 'false').lower() == 'true'
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from config/notion_config.json"""
        config_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'

        default_config = {
            "databases": {},
            "settings": {
                "enabled": True,
                "delete_duplicates": True
            }
        }

        if not config_path.exists():
            self._log(f"Config file not found: {config_path}")
            return default_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._log(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            self._log(f"Failed to load config: {e}")
            return default_config

    def is_available(self) -> bool:
        """Check if Notion client is properly configured"""
        if not self.api_key:
            self._log("NOTION_API_KEY not configured")
            return False

        if not self.config.get('settings', {}).get('enabled', True):
            self._log("Notion sync disabled in config")
            return False

        return True

    def _get_database_id(self, task_id: str) -> Optional[str]:
        """
        Get database ID for a task.
        Priority: Environment variable > Config file > None
        """
        # 1. Check environment variable override
        env_var_name = f'NOTION_DB_{task_id.upper()}'
        env_db_id = os.environ.get(env_var_name)
        if env_db_id:
            self._log(f"Using database ID from env var {env_var_name}")
            return env_db_id

        # 2. Check config file
        config_db_id = self.config.get('databases', {}).get(task_id)
        if config_db_id:
            self._log(f"Using database ID from config for {task_id}")
            return config_db_id

        # 3. Not found
        self._log(f"No database ID configured for {task_id}")
        return None

    def _log(self, message: str):
        """Print debug message if debug mode is enabled"""
        if self.debug:
            print(f"[Notion] {message}")
