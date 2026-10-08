"""Entry point for uvicorn: `uvicorn connector.main:app`. Settings come from the environment."""
import logging

from .app import create_app
from .config import Settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
app = create_app(Settings.from_env())
