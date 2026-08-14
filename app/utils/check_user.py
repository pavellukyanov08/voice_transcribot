import hashlib
import hmac

from app.core import settings


def check_user_allowed(user_id: int) -> bool:
    return user_id in settings.ALLOWED_USERS


def check_user_admin(user_id: int) -> bool:
    return user_id == settings.ADMIN_ID


def check_telegram_auth(data: dict, bot_token: str) -> bool:
    check_hash = data.pop("hash")
    secret_key = hashlib.sha256(bytes(bot_token, "utf-8")).hexdigest()
    data_check_string = "\n".join(
        f"{key}: {value}" for key, value in data.items()
    )
    computed_hash = hmac.new(secret_key.encode(), data_check_string.encode(), hashlib.sha256).hexdigest()
    return computed_hash == check_hash