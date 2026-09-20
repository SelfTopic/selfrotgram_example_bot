from html import escape

from pydantic import BaseModel
from selfrot import BaseRouter, MessageHandler, State, States
from selfrot.filter import Command, HasText, HasUser, InState, NoState, TextStartswith
from selfrot.handlers import CallbackQueryHandler
from selfrot.types import DataCallbackQuery, TextMessage, UserMessage

from ...callbacks import TransferChoice
from ...context import AppContext
from ...exceptions import UserError
from ...keyboards import transfer_keyboard
from ...utils import edit_or_ignore

# Диалог перевода монет в три шага: /transfer (в ответ на сообщение получателя) →
# сумма → подтверждение кнопкой. Данные каждого шага типизированы: fsm.get(...)
# возвращает модель, а не словарь.


class Receiver(BaseModel):
    id: int
    name: str


class TransferData(Receiver):
    amount: int


class Transfer(States):
    amount = State(Receiver)  # ждём сумму; данные: получатель
    confirm = State(TransferData)  # ждём подтверждение; данные: получатель и сумма


class TransferStart(MessageHandler[AppContext[UserMessage]]):
    query = Command("transfer") & HasUser() & NoState()  # начать можно, только вне диалога

    async def handle(self) -> None:
        reply = self.ctx.message.reply_to_message
        receiver = reply.user if reply else None
        if receiver is None or receiver.is_bot or receiver.id == self.ctx.message.user.id:
            raise UserError(
                "Отправьте /transfer в ответ на сообщение того, кому хотите перевести монеты"
            )

        await self.ctx.fsm.set(
            Transfer.amount, Receiver(id=receiver.id, name=receiver.first_name)
        )
        await self.ctx.reply_message(
            f"Сколько монет перевести <b>{escape(receiver.first_name)}</b>? "
            "Отмена: /cancel"
        )


class TransferBusy(MessageHandler[AppContext[TextMessage]]):
    # ~NoState(): диалог уже идёт. Стоит после TransferStart: до него доходят
    # только те, кого он не пропустил.
    query = Command("transfer") & ~NoState()

    async def handle(self) -> None:
        await self.ctx.reply_message("Сначала закончите текущий диалог или отправьте /cancel")


class Cancel(MessageHandler[AppContext[TextMessage]]):
    # Выше шагов диалога: работает на любом из них.
    query = Command("cancel") & ~NoState()

    async def handle(self) -> None:
        await self.ctx.fsm.clear()
        await self.ctx.reply_message("Отменено")


class TransferAmount(MessageHandler[AppContext[TextMessage]]):
    # InState ничего не гарантирует про поля, поэтому текст берём фильтром HasText.
    # ~TextStartswith("/"): команды во время диалога не съедаются, а идут дальше.
    query = InState(Transfer.amount) & HasText() & ~TextStartswith("/")

    async def pre_handle(self) -> None:
        self.amount = int(self.ctx.message.text)  # ValueError уходит в on_error
        if self.amount <= 0:
            raise ValueError("сумма должна быть положительной")

    async def handle(self) -> None:
        receiver = await self.ctx.fsm.get(Transfer.amount)  # Receiver, не dict
        await self.ctx.fsm.set(
            Transfer.confirm,
            TransferData(id=receiver.id, name=receiver.name, amount=self.amount),
        )
        await self.ctx.reply_message(
            f"Перевести <b>{self.amount}</b> монет пользователю "
            f"<b>{escape(receiver.name)}</b>?",
            reply_markup=transfer_keyboard(),
        )

    async def on_error(self, exc: Exception) -> None:
        if isinstance(exc, ValueError):
            await self.ctx.reply_message("Нужно целое положительное число. Отмена: /cancel")
            return

        raise exc


class TransferYes(CallbackQueryHandler[AppContext[DataCallbackQuery]]):
    # Кнопка и состояние вместе: чужое нажатие (или после /cancel и истечения ttl)
    # состояния не находит, и хендлер не срабатывает.
    query = TransferChoice.filter(action="yes") & InState(Transfer.confirm)

    async def handle(self) -> None:
        await self.ctx.answer_callback_query()  # сразу убираем «часики» на кнопке
        data = await self.ctx.fsm.get(Transfer.confirm)  # TransferData
        await self.ctx.fsm.clear()  # до перевода: повторное нажатие уже ничего не найдёт

        sender, _ = await self.ctx.user_service.transfer(
            self.ctx.callback_query.user.id, data.id, data.amount
        )
        await edit_or_ignore(
            self.ctx,
            f"✅ Переведено <b>{data.amount}</b> → <b>{escape(data.name)}</b>. "
            f"Ваш баланс: <b>{sender.balance}</b>",
        )


class TransferNo(CallbackQueryHandler[AppContext[DataCallbackQuery]]):
    query = TransferChoice.filter(action="no") & InState(Transfer.confirm)

    async def handle(self) -> None:
        await self.ctx.fsm.clear()
        await self.ctx.answer_callback_query()
        await edit_or_ignore(self.ctx, "Перевод отменён")


class TransferStale(CallbackQueryHandler[AppContext[DataCallbackQuery]]):
    # Последний: сюда доходят кнопки без подходящего состояния.
    query = TransferChoice.filter()

    async def handle(self) -> None:
        await self.ctx.answer_callback_query(
            "Диалог устарел или это не ваш перевод", show_alert=True
        )


class DialogsRouter(BaseRouter[AppContext]):
    handlers = (
        TransferStart,
        TransferBusy,
        Cancel,
        TransferAmount,
        TransferYes,
        TransferNo,
        TransferStale,
    )


router = DialogsRouter
