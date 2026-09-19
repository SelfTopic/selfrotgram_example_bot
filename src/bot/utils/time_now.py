from datetime import UTC, datetime


def utcnow() -> datetime:
    """Наивное UTC-время: так его хранят и сравнивают колонки без часового пояса."""
    return datetime.now(UTC).replace(tzinfo=None)
