import random

_FACTS = (
    "Типы и методы selfrotgram генерируются из спецификации Bot API, а не пишутся руками.",
    "Фильтр HasPhoto гарантирует поле photo: в хендлере не нужен `if message.photo is None`.",
    "callback_data у Telegram не длиннее 64 байт; CallbackPayload проверяет это при сборке кнопки.",
    "allowed_updates диспетчер считает сам, по зарегистрированным хендлерам.",
    "Мидлварь вложенного роутера срабатывает только если в его поддереве нашёлся хендлер.",
)


class FactsService:
    """Не зависит от БД, поэтому один на всё приложение (см. Dispatcher.create_context)."""

    def random(self) -> str:
        return random.choice(_FACTS)
