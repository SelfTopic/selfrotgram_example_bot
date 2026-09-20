from html import escape
from typing import Sequence

from ..database.models import User

HOME_TEXT = "🏠 <b>Главное меню</b>\nВыбери раздел кнопками ниже. Список команд: /help"

HELP_TEXT = """<b>Что умеет этот бот</b>

<b>Команды: аргументы как данные (CommandArgs)</b>
/echo текст: повторить
/calc 2 + 3: калькулятор (оператор из четырёх)
/roll [граней]: кубик, по умолчанию 6 (от 2 до 1000)
/ping или !ping: два префикса
«бот скажи привет»: команда без префикса
Неверные аргументы: подсказка с форматом

<b>Текст</b>
«привет»: приветствие (фильтры через |)
<code>2+2</code>: калькулятор через регулярное выражение

<b>Кнопки (CallbackPayload)</b>
/start и /menu: меню
/counter: счётчик, нажать может только автор

<b>Диалог (FSM)</b>
/transfer в ответ на чьё-то сообщение: перевод монет в три шага
/cancel: выйти из диалога (сам исчезает через 5 минут)

<b>Отложенные вызовы</b>
/secret: сообщение удалится само
/remind 10 текст: напомнить через 10 секунд
/report: «готовлю отчёт», потом правка сообщения

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
