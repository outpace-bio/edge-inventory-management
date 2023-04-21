from pydantic import BaseModel

from .settings import settings


class LogConfig(BaseModel):
    """
    Logging configuration to be set for the server
    """

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": settings.LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        settings.APP_NAME: {
            "handlers": ["default"], "level": settings.LOG_LEVEL
        },
    }