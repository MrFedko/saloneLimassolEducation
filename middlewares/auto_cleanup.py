from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext


class AutoCleanupMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state: FSMContext = data.get("state")

        # работаем только если есть FSM
        if state:
            try:
                current_data = await state.get_data()
                messages = current_data.get("extra_messages", [])

                chat_id = None

                # определяем chat_id
                if isinstance(event, CallbackQuery):
                    chat_id = event.message.chat.id
                elif isinstance(event, Message):
                    chat_id = event.chat.id

                # удаляем сообщения
                if chat_id and messages:
                    for msg_id in messages:
                        try:
                            await event.bot.delete_message(chat_id, msg_id)
                        except:
                            pass

                # очищаем список
                await state.update_data(extra_messages=[])

            except Exception as e:
                print(f"[AutoCleanupMiddleware] error: {e}")

        return await handler(event, data)
