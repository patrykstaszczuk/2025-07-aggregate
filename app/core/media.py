import os
from functools import lru_cache

MEDIA_DIR = os.getenv("MEDIA_DIR", "app/media")


@lru_cache
def get_media_dir() -> str:
    return MEDIA_DIR
