from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class DateTimeManager:
    @staticmethod
    def get_now_utc() -> datetime:
        """
        Возвращает текущее UTC время как aware datetime.
        """
        return datetime.now(timezone.utc)

    @staticmethod
    def get_now_in_timezone(*, user_timezone: str) -> datetime:
        """
        Возвращает текущее время в часовом поясе пользователя как aware datetime.
        """
        try:
            return datetime.now(ZoneInfo(user_timezone))
        except Exception as e:
            raise ValueError(f"Incorrect timezone: {user_timezone}") from e

    @staticmethod
    def user_local_to_utc(*, date_time: datetime, user_timezone: str) -> datetime:
        """
        Конвертирует naive локальное время пользователя в aware UTC datetime.
        """
        if date_time.tzinfo is not None:
            raise ValueError("date_time must be naive local datetime")

        tz = ZoneInfo(user_timezone)
        local_dt = date_time.replace(tzinfo=tz)
        utc_dt = local_dt.astimezone(timezone.utc)
        return utc_dt
