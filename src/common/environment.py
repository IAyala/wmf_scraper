import os
from typing import Optional


def get_version() -> Optional[str]:
    return os.getenv("VERSION")
