import glob
import os

from aiogram import types, F as f, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import FSInputFile, InputMediaPhoto
from magic_filter import F as MF
from PIL import Image
from loader import dataBase, messageBuilder, client, photo_loader
from .keyboards import menu_cd, back_button_final
from .menuLists import list_start_menu, list_sheet_categories_menu, list_dishes_by_category_menu
from data.config import settings

router = Router()


async def clear_photo_folder(photo_path):
    files = glob.glob(os.path.join(photo_path, '*.jpg'))  # или другие расширения, если нужно
    for f in files:
        try:
            os.remove(f)
            print(f"Deleted {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await list_start_menu(message)


@router.message(Command("reboot"))
async def cmd_reboot(message: types.Message, state: FSMContext):
    await state.clear()
    dataBase.clean_all_values()
    await clear_photo_folder(settings.PHOTO_PATH)
    for table_id, table_name in settings.db_tables.items():
        await client.upload_sheet_to_db(table_id, table_name, dataBase)
    await photo_loader.download_photos(dataBase.get_records_with_photo())
    await message.answer("The data has been updated, the photos have been uploaded, everything is ready!")
    await list_start_menu(message)


@router.callback_query(
    menu_cd.filter(MF.level == 0), flags={"chat_action": "typing"}
)
async def start_menu_callback(
        call: types.CallbackQuery,
        callback_data: menu_cd,
        state: FSMContext,
):
    await state.clear()
    await list_start_menu(call)


@router.callback_query(
    menu_cd.filter(MF.level == 1), flags={"chat_action": "typing"}
)
async def sheet_categories_callback(
        call: types.CallbackQuery,
        callback_data: menu_cd,
        state: FSMContext,
):
    await state.update_data(sheet_id=callback_data.sheet_id)
    categories = dataBase.get_categories(settings.db_tables[callback_data.sheet_id])
    await state.update_data(categories=categories)
    """сохраняем лист категорий в состояние, а индекс категории в callback_data"""
    await list_sheet_categories_menu(call, categories, callback_data)


@router.callback_query(
    menu_cd.filter(MF.level == 2), flags={"chat_action": "typing"}
)
async def dishes_by_category_callback(
        call: types.CallbackQuery,
        callback_data: menu_cd,
        state: FSMContext,
):
    data = await state.get_data()
    sheet_id = data.get("sheet_id")
    categories = data.get("categories")
    category_index = callback_data.category_index
    category_name = categories[category_index]
    dishes = dataBase.get_dishes_by_category(
        settings.db_tables[sheet_id], category_name
    )
    await state.update_data(dishes=dishes)
    """сохраняем лист блюд в состоянии, а индекс блюда в callback_data"""
    await list_dishes_by_category_menu(call, dishes, callback_data)


@router.callback_query(
    menu_cd.filter(MF.level == 3), flags={"chat_action": "typing"}
)
async def dish_detail_callback(
        call: types.CallbackQuery,
        callback_data: menu_cd,
        state: FSMContext,
):
    MAX_CAPTION_LENGTH = 1024
    data = await state.get_data()
    sheet_id = data.get("sheet_id")
    dishes = data.get("dishes")
    dishes_list_index = callback_data.dishes_list_index
    table_name = settings.db_tables[sheet_id]
    dish_name = dishes[dishes_list_index]
    dish_info = dataBase.get_dish_detail(
        table_name, dish_name
    )
    text = messageBuilder.message_return(settings.db_tables[sheet_id])(dish_info)
    photo_link = dish_info.get("photo_link")
    photo_path = f"{settings.PHOTO_PATH}{table_name}_{dish_info['id']}.jpg"
    if photo_link and os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        if len(text) <= MAX_CAPTION_LENGTH:
            # Если текст помещается в подпись — отправляем вместе с фото
            await call.message.edit_media(
                media=types.InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                reply_markup=back_button_final(callback_data)
            )
        else:
            # Если текст слишком длинный — разбиваем
            caption_part = text[:MAX_CAPTION_LENGTH]
            rest_part = text[MAX_CAPTION_LENGTH:]
            chunks = [rest_part[i:i + MAX_CAPTION_LENGTH] for i in range(0, len(text), MAX_CAPTION_LENGTH)]
            await call.message.edit_media(
                media=types.InputMediaPhoto(media=photo, caption=caption_part, parse_mode="HTML"),
                reply_markup=back_button_final(callback_data)
            )
            # Отправляем остаток текста отдельным сообщением
            for chunk in chunks[1:]:
                if not chunk.strip():
                    continue
                await call.message.answer(chunk, parse_mode="HTML")
    else:
        # Если фото нет, просто отправляем текст (можно разбить на части тоже, если надо)
        if len(text) <= MAX_CAPTION_LENGTH:
            await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_button_final(callback_data))
        else:
            # Разбиваем и отправляем частями
            chunks = [text[i:i + MAX_CAPTION_LENGTH] for i in range(0, len(text), MAX_CAPTION_LENGTH)]
            await call.message.edit_text(chunks[0], parse_mode="HTML", reply_markup=back_button_final(callback_data))
            for chunk in chunks[1:]:
                if not chunk.strip():
                    continue
                await call.message.answer(chunk, parse_mode="HTML")
