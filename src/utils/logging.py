import logging
import os
from logging.handlers import RotatingFileHandler
from src.config.settings import settings


def setup_logging():
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                settings.log_file,
                maxBytes=10485760,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete. Level: {settings.log_level}")
    return logger


logger = setup_logging() 