import os

log_path_app = os.path.join("/", "src/logs/film_api.json")
log_path_uvicorn = os.path.join("/", "src/logs/uvicorn.json")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "ecs_logging.StdlibFormatter",
        },
        "uvicorn-default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "use_colors": None,
        },
        "uvicorn-access": {
            "()": "uvicorn.logging.AccessFormatter",
            "use_colors": None,
        },
    },
    "handlers": {
        "film_api_handler": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.FileHandler",
            "filename": log_path_app,
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "uvicorn-default": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.FileHandler",
            "filename": log_path_uvicorn,
        },
        "uvicorn-access": {
            "formatter": "uvicorn-access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "film_api": {
            "handlers": ["film_api_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["uvicorn-default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["uvicorn-access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console",
        ],
    },
}
