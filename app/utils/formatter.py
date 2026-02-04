from datetime import datetime
from textwrap import shorten


class Formatter:
    @staticmethod
    def normalize_date(date: datetime | str) -> str:
        if isinstance(date, datetime):
            return date.strftime("%d.%m.%Y %H:%M")
        try:
            return datetime.fromisoformat(date).strftime("%d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            return str(date)

    @staticmethod
    def preview_text(content: str, width: int = 40) -> str:
        return shorten(content, width=width, placeholder="…")