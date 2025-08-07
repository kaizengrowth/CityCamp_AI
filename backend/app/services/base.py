import logging
from abc import ABC
from typing import Optional

from app.core.config import Settings
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base class for all services to provide common functionality and patterns"""

    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup()

    def _setup(self):
        """Override in subclasses for service-specific initialization"""
        pass

    def _validate_required_config(self, *config_keys: str) -> bool:
        """Validate that required configuration keys are present"""
        for key in config_keys:
            if not hasattr(self.settings, key) or not getattr(self.settings, key):
                self.logger.warning(f"Missing required configuration: {key}")
                return False
        return True

    def _log_operation(self, operation: str, details: Optional[str] = None):
        """Standard logging for service operations"""
        message = f"{operation}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
