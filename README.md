# selfrotgram example bot

Показательный бот на [selfrotgram](https://github.com/SelfTopic/selfrotgram): один бот,
в котором есть все основные виды апдейтов и приёмы библиотеки. Логика игрушечная, важно
как это написано.

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
админом чата.

## Что где смотреть

| Что показывает | Где |
|---|---|
| Команды, аргументы, `args_count`, префиксы, `pre_handle`/`on_error` | [commands_router.py](src/bot/routers/common/commands_router.py) |
| Текстовые фильтры, `TextRegexp`, комбинаторы `&` и `\|` | [text_router.py](src/bot/routers/common/text_router.py) |
| Сужение типов фильтром (`HasPhoto`), редактирование сообщений | [events_router.py](src/bot/routers/common/events_router.py) |
| `CallbackPayload`, `pressed_by`, меню и счётчик | [callbacks_router.py](src/bot/routers/common/callbacks_router.py), [callbacks.py](src/bot/callbacks.py) |
| Inline-запросы | [inline_router.py](src/bot/routers/common/inline_router.py) |
| `chat_member` и `my_chat_member` | [chat_member_router.py](src/bot/routers/common/chat_member_router.py) |
| Зависимости в контексте (общие и с БД) | [context.py](src/bot/context.py) |
| Сессия БД на апдейт, атомарный upsert и кулдаун | [database_middleware.py](src/bot/middlewares/database_middleware.py), [repositories/](src/bot/repositories/) |
| Мидлварь на роутере (только для админов) | [routers/admin/](src/bot/routers/admin/) |
| `auto_connect`, `Bot.defaults`, `on_error` диспетчера | [\_\_main\_\_.py](src/bot/__main__.py), [routers/](src/bot/routers/) |

Команды бота: `/help`.
