import os


def get_version() -> str:
    result = os.getenv("VERSION")
    return result if result else ""
