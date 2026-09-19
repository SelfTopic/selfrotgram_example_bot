from html import escape
from typing import Sequence

from ..database.models import User

HOME_TEXT = "🏠 <b>Главное меню</b>\nВыбери раздел кнопками ниже. Список команд: /help"

HELP_TEXT = """<b>Что умеет этот бот</b>

<b>Команды и аргументы</b>
/echo текст: повторить
/sum 2 3: сумма (ровно два аргумента)
/roll или «кубик»: бросить кубик (без слэша)
«бот скажи привет»: команда из двух слов без префикса
/ping или !ping: два префикса

<b>Текст</b>
«привет»: приветствие (фильтры через |)
<code>2+2</code>: калькулятор через регулярное выражение

<b>Кнопки</b>
/start и /menu: меню (CallbackPayload)
/counter: счётчик, нажать может только автор

<b>БД и зависимости в контексте</b>
/me, /bonus (раз в минуту), /top

<b>Разное</b>
Отправь фото или отредактируй сообщение
@бот текст: inline-режим
Добавь бота в группу: приветствие вошедших
/stats: только для админов (ADMIN_IDS)"""


def profile_text(user: User) -> str:
    return (
        f"👤 <b>{escape(user.full_name.strip())}</b>\n"
        f"Telegram ID: <code>{user.telegram_id}</code>\n"
        f"Баланс: <b>{user.balance}</b>\n"
        f"В боте с {user.created_at:%d.%m.%Y}"
    )


def top_text(users: Sequence[User]) -> str:
    if not users:
        return "Пока никого нет."
    lines = [
        f"{i}. {escape(u.first_name)}: <b>{u.balance}</b>"
        for i, u in enumerate(users, 1)
    ]
    return "🏆 <b>Топ по балансу</b>\n" + "\n".join(lines)
