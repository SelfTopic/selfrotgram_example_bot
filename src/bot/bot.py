from selfrot import Bot, BotDefaults


class DemoBot(Bot):
    # Подставляется в каждый вызов, где parse_mode не задан, в том числе внутрь
    # результатов inline-запросов. Поэтому пользовательский текст экранируем.
    defaults = BotDefaults(parse_mode="HTML")
