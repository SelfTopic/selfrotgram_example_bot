from typing import Literal

from selfrot import CallbackPayload


class Menu(CallbackPayload, prefix="menu"):
    """Кнопки главного меню: menu:profile."""

    section: Literal["home", "profile", "bonus", "top", "fact"]


class Counter(CallbackPayload, prefix="cnt"):
    """
    Счётчик хранит своё значение в самой кнопке (cnt:inc:5:123456789), а владелец
    нужен, чтобы в группе нажать мог только тот, кто его создал.
    """

    action: Literal["inc", "dec", "reset", "close"]
    value: int
    owner: int
