from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from data.config import settings


class menu_cd(CallbackData, prefix="show_menu"):
    level: int = 0
    sheet_id: int = 0
    category_index: int = 0
    dishes_list_index: int = 0


def start_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    list_buttons = list(settings.worksheet_ids.keys())
    buttons = []
    for name in list_buttons:
        buttons.append(
            InlineKeyboardButton(
                text=name,
                callback_data=menu_cd(
                    level=1,
                    sheet_id=settings.worksheet_ids[name][0]
                ).pack()
            )
        )
    markup.row(*buttons, width=1)
    return markup.as_markup()


def sheet_categories_keyboard(callback_data: menu_cd, categories: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    buttons = []
    for category in categories:
        buttons.append(
            InlineKeyboardButton(
                text=category,
                callback_data=menu_cd(
                    level=2,
                    sheet_id=callback_data.sheet_id,
                    category_index=categories.index(category)
                ).pack()
            )
        )
    markup.row(*buttons, width=1)
    back_button = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data=menu_cd(
            level=0
        ).pack()
    )
    markup.row(back_button)
    return markup.as_markup()

def dishes_by_category_keyboard(callback_data: menu_cd, dishes: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    buttons = []
    for dish in dishes:
        buttons.append(
            InlineKeyboardButton(
                text=dish,
                callback_data=menu_cd(
                    level=3,
                    sheet_id=callback_data.sheet_id,
                    category_index=callback_data.category_index,
                    dishes_list_index=dishes.index(dish)
                ).pack()
            )
        )
    markup.row(*buttons, width=1)
    back_button = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data=menu_cd(
            level=1,
            sheet_id=callback_data.sheet_id,
            category_index=callback_data.category_index,
        ).pack()
    )
    markup.row(back_button)
    return markup.as_markup()


def back_button_final(callback_data: menu_cd) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    back_button = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data=menu_cd(
            level=2,
            sheet_id=callback_data.sheet_id,
            category_index=callback_data.category_index,
        ).pack()
    )
    markup.row(back_button)
    return markup.as_markup()
