from selfrot import BaseRouter, MessageHandler
from selfrot.filter import Command, HasUser
from selfrot.handlers import CallbackQueryHandler
from selfrot.types import DataCallbackQuery, UserMessage

from ...callbacks import Counter, Menu
from ...context import AppContext
from ...exceptions import UserError
from ...keyboards import back_keyboard, counter_keyboard, menu_keyboard
from ...texts import HOME_TEXT, profile_text, top_text
from ...utils import edit_or_ignore


class CounterStart(MessageHandler[AppContext[UserMessage]]):
    query = Command("counter") & HasUser()

    async def handle(self) -> None:
        user_id = self.ctx.message.user.id
        await self.ctx.answer_message(
            "🔢 Счётчик: <b>0</b>", reply_markup=counter_keyboard(0, owner=user_id)
        )


class CounterPressed(CallbackQueryHandler[AppContext[DataCallbackQuery]]):
    # pressed_by: пропускает только нажатие того, чей id лежит в поле owner.
    counter = Counter.filter().pressed_by("owner")
    query = counter

    async def handle(self) -> None:
        payload = self.counter.parse(self.ctx)  # типизированные данные кнопки

        if payload.action == "close":
            await self.ctx.delete_message()
            await self.ctx.answer_callback_query("Закрыто")
            return

        value = {
            "inc": payload.value + 1,
            "dec": payload.value - 1,
            "reset": 0,
        }[payload.action]

        await edit_or_ignore(
            self.ctx,
            f"🔢 Счётчик: <b>{value}</b>",
            counter_keyboard(value, owner=payload.owner),
        )
        await self.ctx.answer_callback_query()


class CounterNotYours(CallbackQueryHandler[AppContext[DataCallbackQuery]]):
    # Стоит после CounterPressed: сюда доходит нажатие на чужой счётчик.
    query = Counter.filter()

    async def handle(self) -> None:
        await self.ctx.answer_callback_query("Это не твой счётчик 🙅", show_alert=True)


class MenuPressed(CallbackQueryHandler[AppContext[DataCallbackQuery]]):
    menu = Menu.filter()
    query = menu

    async def handle(self) -> None:
        section = self.menu.parse(self.ctx).section
        user_id = self.ctx.callback_query.user.id
        markup = back_keyboard()

        match section:
            case "home":
                text, markup = HOME_TEXT, menu_keyboard()
            case "profile":
                user = await self.ctx.user_service.get(user_id)
                if not user:
                    raise UserError("Тебя нет в базе, отправь /start")
                text = profile_text(user)
            case "bonus":
                user = await self.ctx.user_service.claim_bonus(user_id)
                text = f"🎁 Бонус получен! Баланс: <b>{user.balance}</b>"
            case "top":
                text = top_text(await self.ctx.user_service.top())
            case "fact":
                text = f"💡 {self.ctx.facts.random()}"

        await edit_or_ignore(self.ctx, text, markup)
        await self.ctx.answer_callback_query()


class CallbacksRouter(BaseRouter[AppContext]):
    handlers = (CounterStart, CounterPressed, CounterNotYours, MenuPressed)


router = CallbacksRouter
