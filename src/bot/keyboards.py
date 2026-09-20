from selfrot import InlineKeyboard, button
from selfrot.types import InlineKeyboardMarkup

from .callbacks import Counter, Menu, TransferChoice


def menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboard(width=2)  # по две кнопки в ряд
    kb.button("👤 Профиль", Menu(section="profile"))
    kb.button("🎁 Бонус", Menu(section="bonus"))
    kb.button("🏆 Топ", Menu(section="top"))
    kb.button("💡 Факт", Menu(section="fact"))
    kb.row(button("📚 Репозиторий", url="https://github.com/SelfTopic/selfrotgram_example_bot"))
    return kb.markup()


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboard().button("⬅️ В меню", Menu(section="home")).markup()


def counter_keyboard(value: int, owner: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboard(width=3)
    kb.button("−1", Counter(action="dec", value=value, owner=owner))
    kb.button("🔄", Counter(action="reset", value=value, owner=owner))
    kb.button("+1", Counter(action="inc", value=value, owner=owner))
    kb.row(button("✖ Закрыть", Counter(action="close", value=value, owner=owner)))
    return kb.markup()


def transfer_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboard(width=2)
    kb.button("✅ Перевести", TransferChoice(action="yes"))
    kb.button("❌ Отмена", TransferChoice(action="no"))
    return kb.markup()
