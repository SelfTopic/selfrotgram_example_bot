# selfrotgram example bot

Показательный бот на [selfrotgram](https://github.com/SelfTopic/selfrotgram) 0.1.1: один
бот, в котором есть основные виды апдейтов и приёмы библиотеки: команды с типизированными
аргументами, кнопки, inline, участники чата, диалоги на FSM, отложенные вызовы, БД и
зависимости в контексте. Логика игрушечная, важно как это написано. Полный список команд
бот показывает по `/help`.

## Запуск

```bash
poetry install
cp .env.example .env    # вписать BOT_TOKEN (и ADMIN_IDS для /stats)
poetry run python -m src.bot
```

По умолчанию база SQLite (`dev.db`), таблицы создаются при старте. Для Postgres задайте
`DATABASE_URL=postgresql+psycopg://...` и поставьте драйвер.

В @BotFather для inline-режима включите `/setinline`; `/setinlinefeedback` нужен только
для `ChosenInlineResult`. Чтобы бот видел вход и выход участников группы, сделайте его
админом чата. Перевод монет (`/transfer`) нужен группе: команда отправляется в ответ на сообщение
получателя, и тот должен уже писать боту (в личке получателя нет).

## Что показывает

| Возможность | Где смотреть |
|---|---|
| Аргументы команд как данные: `CommandArgs`, `Rest`, `Literal`, значения по умолчанию, ограничения pydantic | [commands_router.py](src/bot/routers/common/commands_router.py) |
| Одна подсказка про формат для неверных аргументов любой команды (`CommandArgsError`) | [\_\_main\_\_.py](src/bot/__main__.py) (`on_error`) |
| Префиксы `/!`, имя из двух слов без префикса, `args_count`, комбинаторы `&` `\|` `~` | [commands_router.py](src/bot/routers/common/commands_router.py), [start_router.py](src/bot/routers/common/start_router.py) |
| **FSM**: `States`, `State(Model)` с типизированными данными, `InState`, `NoState`, `ctx.fsm`, `MemoryStorage(ttl)`; диалог перевода монет в три шага | [dialogs_router.py](src/bot/routers/common/dialogs_router.py) |
| Кнопки подтверждения вместе с состоянием: чужое нажатие состояния не находит | [dialogs_router.py](src/bot/routers/common/dialogs_router.py) |
| **Отложенные вызовы**: `self.defer(...)`, `after_handle` (и своя сессия БД там) | [deferred_router.py](src/bot/routers/common/deferred_router.py) |
| Порядок обработки апдейтов одного пользователя (`ordering_key`) | [\_\_main\_\_.py](src/bot/__main__.py) |
| Текстовые фильтры, `TextRegexp` | [text_router.py](src/bot/routers/common/text_router.py) |
| Сужение типов фильтром (`HasPhoto`), редактирование сообщений | [events_router.py](src/bot/routers/common/events_router.py) |
| `CallbackPayload`, `pressed_by`, меню и счётчик | [callbacks_router.py](src/bot/routers/common/callbacks_router.py), [callbacks.py](src/bot/callbacks.py) |
| Inline-запросы | [inline_router.py](src/bot/routers/common/inline_router.py) |
| `chat_member` и `my_chat_member` | [chat_member_router.py](src/bot/routers/common/chat_member_router.py) |
| Зависимости в контексте (общие и с БД) | [context.py](src/bot/context.py) |
| Сессия БД на апдейт, атомарные upsert, кулдаун и списание | [database_middleware.py](src/bot/middlewares/database_middleware.py), [repositories/](src/bot/repositories/) |
| Мидлварь на роутере (только для админов) | [routers/admin/](src/bot/routers/admin/) |
| `auto_connect`, `Bot.defaults`, `on_error` диспетчера | [\_\_main\_\_.py](src/bot/__main__.py), [routers/](src/bot/routers/) |

## Проверка проекта

Проверки берутся из самой библиотеки:

```bash
# нет ли забытых, недостижимых или продублированных хендлеров
poetry run selfrot check src.bot.__main__:Dispatcher --strict
# дерево роутеров: хендлеры, вид апдейта и фильтр каждого, allowed_updates
poetry run selfrot tree src.bot.__main__:Dispatcher
```

`selfrot check` только собирает диспетчер и в Telegram не ходит.
