"""
@file keyboards.py
@brief Модуль генерації клавіатур користувацького інтерфейсу Telegram-бота.

Містить функції-фабрики для створення інлайн (Inline) та звичайних (Reply) 
клавіатур. Усі клавіатури підтримують динамічну локалізацію (i18n) 
залежно від обраної мови користувача.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from bot.i18n import get_str

def get_reply_main_menu(lang: str = "ukr") -> ReplyKeyboardMarkup:
    """
    @brief Генерує постійне нижнє меню керування (Reply Keyboard).
    
    @param lang Код мови інтерфейсу (наприклад, 'ukr' або 'eng').
    @return Об'єкт ReplyKeyboardMarkup із базовими командами навігації.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_str(lang, "btn_recognize"))
    builder.button(text=get_str(lang, "btn_settings"))
    builder.button(text=get_str(lang, "btn_help"))
    
    builder.adjust(1, 2)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Select action / Оберіть дію..."
    )

def get_main_menu(lang: str = "ukr") -> InlineKeyboardMarkup:
    """
    @brief Генерує головне інлайн-меню бота.
    
    @param lang Код мови інтерфейсу.
    @return Об'єкт InlineKeyboardMarkup із кнопками основних дій та посиланням на Web-панель.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text=get_str(lang, "btn_recognize"), callback_data="menu_send_photo")
    builder.button(text=get_str(lang, "btn_settings"), callback_data="menu_settings")
    builder.button(text=get_str(lang, "btn_help"), callback_data="menu_help")
    builder.button(text=get_str(lang, "btn_web"), url="https://smarthub-1vrp.onrender.com") 
    
    builder.adjust(1, 2, 1)
    return builder.as_markup()
    
def get_settings_menu(lang: str = "ukr") -> InlineKeyboardMarkup:
    """
    @brief Генерує меню вибору стратегії розпізнавання (Pattern Strategy).
    
    @param lang Код мови інтерфейсу.
    @return Об'єкт InlineKeyboardMarkup із переліком доступних OCR-алгоритмів.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text=get_str(lang, "btn_strategy_plain"), callback_data="set_strategy_plain")
    builder.button(text=get_str(lang, "btn_strategy_math"), callback_data="set_strategy_math")
    builder.button(text=get_str(lang, "btn_back"), callback_data="menu_main")
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_settings_keyboard(lang: str = "ukr") -> InlineKeyboardMarkup:
    """
    @brief Генерує інлайн-клавіатуру для вибору мови інтерфейсу (i18n).
    
    @param lang Код мови інтерфейсу для локалізації самих кнопок вибору.
    @return Об'єкт InlineKeyboardMarkup із переліком підтримуваних мов.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text=get_str(lang, "btn_lang_ukr"), callback_data="lang_ukr")
    builder.button(text=get_str(lang, "btn_lang_eng"), callback_data="lang_eng")
    
    builder.adjust(2) 
    return builder.as_markup()

def get_result_keyboard(lang: str = "ukr", record_id: str = "") -> InlineKeyboardMarkup:
    """
    @brief Генерує клавіатуру під результатом OCR із кнопкою перекладу.
    
    @param lang Код мови інтерфейсу.
    @param record_id Унікальний ідентифікатор запису (повідомлення) для маршрутизації callback-запиту.
    @return Об'єкт InlineKeyboardMarkup із кнопкою "Перекласти".
    """
    builder = InlineKeyboardBuilder()
    builder.button(text=get_str(lang, "btn_translate"), callback_data=f"translate_{record_id}")
    return builder.as_markup()