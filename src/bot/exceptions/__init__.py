class UserError(Exception):
    """Ошибка, текст которой показывают пользователю (её ловит Dispatcher.on_error)."""


class BonusCooldownError(UserError):
    def __init__(self, seconds_left: int) -> None:
        super().__init__(f"⏳ Бонус будет доступен через {seconds_left} с")


__all__ = ["UserError", "BonusCooldownError"]
