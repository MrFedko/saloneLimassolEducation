from aiogram.types import CallbackQuery, Message
from typing import Union
from data.lexicon import lexicon
from .keyboards import start_keyboard, sheet_categories_keyboard, dishes_by_category_keyboard


async def list_start_menu(message: Union[CallbackQuery, Message], **kwargs):
    text = lexicon["/start"].format(name=message.from_user.first_name)
    markup = start_keyboard()

    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        if call.message.photo:
            await call.message.edit_caption(
                caption=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            await call.message.edit_text(
                text,
                reply_markup=markup,
                parse_mode="HTML"
            )


async def list_sheet_categories_menu(message: Union[CallbackQuery, Message], categories: list, callback_data):
    text = lexicon["choose_category"]
    markup = sheet_categories_keyboard(callback_data, categories)

    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        if call.message.photo:
            await call.message.edit_caption(
                caption=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            await call.message.edit_text(
                text,
                reply_markup=markup,
                parse_mode="HTML"
            )

async def list_dishes_by_category_menu(message: Union[CallbackQuery, Message], dishes: list, callback_data):
    text = lexicon["choose_dish"]
    markup = dishes_by_category_keyboard(callback_data, dishes)

    if isinstance(message, Message):
        await message.answer(text, reply_markup=markup)

    elif isinstance(message, CallbackQuery):
        call = message
        if call.message.photo:
            await call.message.delete()
            await call.message.answer(
                text=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            await call.message.edit_text(
                text,
                reply_markup=markup,
                parse_mode="HTML"
            )
