from os import environ

from dotenv import load_dotenv

load_dotenv()

# ADMIN_IDS=123,456 в .env; свой id показывает команда /me.
ADMIN_IDS: tuple[int, ...] = tuple(
    int(part) for part in environ.get("ADMIN_IDS", "").replace(" ", "").split(",") if part
)
