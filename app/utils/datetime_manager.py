from datetime import datetime, timezone


def get_now_utc() -> datetime:
    """
    Возвращает текущее UTC время как aware datetime.
    """
    return datetime.now(timezone.utc)
