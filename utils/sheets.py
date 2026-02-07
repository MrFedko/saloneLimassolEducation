import re
import asyncio
import gspread_asyncio
from google.oauth2.service_account import Credentials
from data.config import settings
from googleapiclient.discovery import build
from database.crud import Database

class GoogleSheetsClient:
    def __init__(self, creds_path: str, sheet_id: str):
        self.creds_path = creds_path
        self.sheet_id = sheet_id
        self.agcm = gspread_asyncio.AsyncioGspreadClientManager(self._get_creds)
        creds = self._get_creds()
        self.drive_service = build('drive', 'v3', credentials=creds)

    def _get_creds(self):
        """Загрузка и настройка credentials"""
        creds = Credentials.from_service_account_file(self.creds_path)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    async def authorize(self):
        """Авторизация и получение клиента"""
        return await self.agcm.authorize()

    async def get_spreadsheet(self):
        """Получение таблицы по sheet_id"""
        agc = await self.authorize()
        return await agc.open_by_key(self.sheet_id)

    async def get_worksheets(self):
        """Получение всех листов таблицы"""
        ss = await self.get_spreadsheet()
        return await ss.worksheets()

    async def get_worksheet_values_by_id(self, worksheet_id: int):
        """Получение листа по его ID"""
        ss = await self.get_spreadsheet()
        ws = await ss.get_worksheet_by_id(worksheet_id)
        return await ws.get_all_values()

    async def upload_sheet_to_db(self, worksheet_id: int, db_table: str, db):
        """Загрузка данных листа в БД"""
        data = await self.get_worksheet_values_by_id(worksheet_id)
        for row in data[1:]:
            # Преобразуем ссылки в каждом элементе строки
            new_row = []
            for cell in row:
                if isinstance(cell, str):
                    # Заменяем все ссылки формата Google Drive в ячейке (если их несколько, заменим все)
                    new_cell = re.sub(
                        r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/view\?usp=drive_link',
                        lambda m: f"https://drive.google.com/uc?export=view&id={m.group(1)}",
                        cell
                    )
                    new_row.append(new_cell)
                else:
                    new_row.append(cell)
            db.insert_row(db_table, new_row)


# async def main():
#     dataBase = Database(settings.DB_PATH)
#     gs_client = GoogleSheetsClient(
#         creds_path=settings.CREDS_PATH,
#         sheet_id=settings.SHEET_ID
#     )
#     for table_id, table_name in settings.db_tables.items():
#         await gs_client.upload_sheet_to_db(table_id, table_name, dataBase)
#
# if __name__ == "__main__":
#     asyncio.run(main())
