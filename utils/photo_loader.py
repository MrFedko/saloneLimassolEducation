from io import BytesIO
import aiohttp
import asyncio
import os
from PIL import Image, UnidentifiedImageError
import json
from data.config import settings
from loader import dataBase
import re


class PhotoLoader:
    def __init__(self, photo_directory, max_concurrent=3, delay=1):
        self.photo_directory = photo_directory
        os.makedirs(self.photo_directory, exist_ok=True)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay
        self.failed = []

    def convert_drive_url(self, url: str) -> str:
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return url

    def _normalize_and_save(self, content: bytes, filepath: str):
        try:
            with Image.open(BytesIO(content)) as img:
                img.verify()

            with Image.open(BytesIO(content)) as img:
                img = img.convert("RGB")
                img.thumbnail((2048, 2048), Image.LANCZOS)

                img.save(
                    filepath,
                    "JPEG",
                    quality=80,
                    optimize=True,
                    progressive=True,
                    subsampling=2
                )
            return True

        except UnidentifiedImageError:
            print("Invalid image format")
            return False

        except Exception as e:
            print(f"Image normalization failed: {e}")
            return False

    def _save_raw(self, content: bytes, filepath: str, content_type: str):
        ext = "bin"

        if "jpeg" in content_type or "jpg" in content_type:
            ext = "jpg"
        elif "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"

        raw_path = filepath.replace(".jpg", f"_raw.{ext}")

        with open(raw_path, "wb") as f:
            f.write(content)

        return raw_path

    async def _download_photo(self, session, table, id_, url, retries=3):
        async with self.semaphore:
            for attempt in range(retries):
                try:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print(f"Bad status {resp.status} for {url}")
                            continue

                        content_type = resp.headers.get("Content-Type", "")
                        content = await resp.read()

                        filename = f"{table}_{id_}.jpg"
                        filepath = os.path.join(self.photo_directory, filename)

                        # ❌ не картинка
                        if not content_type.startswith("image/"):
                            print(f"Not an image: {url} -> {content_type}")

                            raw_path = self._save_raw(content, filepath, content_type)

                            self.failed.append({
                                "table": table,
                                "id": id_,
                                "photo_link": url,
                                "reason": "not_image",
                                "raw_file": raw_path
                            })
                            return

                        # ✅ пробуем нормализацию
                        if self._normalize_and_save(content, filepath):
                            print(f"Downloaded & normalized {filename}")
                            return
                        else:
                            print(f"Normalization failed, saving raw: {filename}")

                            raw_path = self._save_raw(content, filepath, content_type)

                            self.failed.append({
                                "table": table,
                                "id": id_,
                                "photo_link": url,
                                "reason": "normalization_failed",
                                "raw_file": raw_path
                            })
                            return

                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")

                await asyncio.sleep(self.delay)

            # ❌ все попытки неудачны
            self.failed.append({
                "table": table,
                "id": id_,
                "photo_link": url,
                "reason": "download_failed"
            })

    async def download_photos(self, records):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for record in records:
                table = record['table']
                id_ = record['id']
                url = self.convert_drive_url(record['photo_link'])

                tasks.append(self._download_photo(session, table, id_, url))

            await asyncio.gather(*tasks)

    def save_failed(self, filepath="failed.json"):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.failed, f, ensure_ascii=False, indent=2)

    async def download_fails(self, filepath="failed.json"):
        if not os.path.exists(filepath):
            print("No failed file found")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            failed_records = json.load(f)

        # очищаем перед повторной попыткой
        self.failed = []

        await self.download_photos(failed_records)


# async def main():
#     photo_loader = PhotoLoader(settings.PHOTO_PATH, max_concurrent=3, delay=1)
#     await photo_loader.download_photos(dataBase.get_records_with_photo())
#     photo_loader.save_failed()
#     # повторная попытка
#     await photo_loader.download_fails()
#     # сохраняем снова после ретрая
#     photo_loader.save_failed("failed_after_retry.json")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
