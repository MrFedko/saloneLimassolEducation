from io import BytesIO

import aiohttp
import asyncio
import os
from PIL import Image


class PhotoLoader:
    def __init__(self, photo_directory, data_base, max_concurrent=3, delay=1):
        self.photo_directory = photo_directory
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay  # задержка в секундах между запросами
        self.db = data_base
        os.makedirs(self.photo_directory, exist_ok=True)

    def _normalize_and_save(self, content: bytes, filepath: str):
        """
        Telegram-safe JPEG:
        нормальное качество + минимальный вес
        """
        try:
            with Image.open(BytesIO(content)) as img:
                img = img.convert("RGB")

                # Telegram реально не выигрывает от >2048px
                img.thumbnail((2048, 2048), Image.LANCZOS)

                img.save(
                    filepath,
                    "JPEG",
                    quality=80,  # sweet spot
                    optimize=True,  # важно!
                    progressive=True,  # уменьшает вес + быстрее грузится
                    subsampling=2  # 4:2:0, почти без потери качества
                )
                return True

        except Exception as e:
            print(f"Image normalization failed: {e}")
            return False

    async def _download_photo(self, session, table, id_, url):
        async with self.semaphore:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        filename = f"{table}_{id_}.jpg"
                        filepath = os.path.join(self.photo_directory, filename)
                        ok = self._normalize_and_save(content, filepath)
                        if ok:
                            print(f"Downloaded & normalized {filename}")
                        else:
                            name = self.db.get_name_by_id(table, id_)
                            print(f"Skipped broken image {name}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")
            await asyncio.sleep(self.delay)  # задержка после каждого запроса

    async def download_photos(self, records):
        """
        records: list of dicts with keys: 'table', 'id', 'photo_link'
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for record in records:
                table = record['table']
                id_ = record['id']
                url = record['photo_link']
                tasks.append(self._download_photo(session, table, id_, url))
            await asyncio.gather(*tasks)

# async def main():
#     photo_loader = PhotoLoader(settings.PHOTO_PATH, max_concurrent=3, delay=1)
#     await photo_loader.download_photos(dataBase.get_records_with_photo())
#
# if __name__ == "__main__":
#     asyncio.run(main())
