from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from data.config import settings
from database.crud import Database
from utils.photo_loader import PhotoLoader
from utils.sheets import GoogleSheetsClient
from utils.message_builder import MessageBuilder


session = AiohttpSession()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dataBase = Database(settings.DB_PATH)
client = GoogleSheetsClient(
    creds_path=settings.CREDS_PATH,
    sheet_id=settings.SHEET_ID
)
messageBuilder = MessageBuilder()
photo_loader = PhotoLoader(settings.PHOTO_PATH, max_concurrent=3, delay=1)
