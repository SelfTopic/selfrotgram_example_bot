from selfrot import BaseRouter

from ...context import AppContext


class CommonRouter(BaseRouter[AppContext]):
    # Порядок важен: апдейт забирает первый подошедший хендлер.
    # Новый роутер из этого пакета добавляется сюда одной строкой.
    auto_connect = (
        ".start_router",
        ".dialogs_router",  # шаги диалога выше общих обработчиков текста
        ".help_router",
        ".commands_router",
        ".deferred_router",
        ".text_router",
        ".events_router",
        ".callbacks_router",
        ".inline_router",
        ".chat_member_router",
        ".profile_router",
    )


router = CommonRouter

__all__ = ["CommonRouter", "router"]
