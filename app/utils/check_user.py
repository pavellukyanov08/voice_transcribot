from app.core import settings


def check_user_allowed(user_id: int) -> bool:
    return user_id in settings.ALLOWED_USERS


def check_user_admin(user_id: int) -> bool:
    return user_id == settings.ADMIN_ID