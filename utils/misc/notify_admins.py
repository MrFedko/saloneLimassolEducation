from aiogram import Bot
from data.config import settings


async def on_startup_notify(bot: Bot):
    for admin in settings.admins:
        await bot.send_message(admin, "Бот Запущен")


async def on_shutdown_notify(bot: Bot):
    for admin in settings.admins:
        await bot.send_message(admin, "Бот Остановлен")
