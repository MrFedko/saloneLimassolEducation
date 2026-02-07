from aiogram.utils.chat_action import ChatActionMiddleware
from handlers import user_handlers
import asyncio
from loader import dp, bot
from utils.misc.set_bot_commands import set_default_commands
from utils.misc.notify_admins import on_startup_notify, on_shutdown_notify


async def on_startup(bot):
    await set_default_commands(bot)
    await on_startup_notify(bot)


async def on_shutdown(bot):
    await on_shutdown_notify(bot)


def connect_routers():
    dp.include_routers(
        user_handlers.router,
    )


async def main():
    dp.message.middleware.register(ChatActionMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    connect_routers()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
