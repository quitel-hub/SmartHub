from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from bot.i18n import get_str

def get_reply_main_menu(lang: str = "ukr") -> ReplyKeyboardMarkup:
    """Генерує постійне нижнє меню керування (Reply Keyboard) з урахуванням мови."""
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
    """Генерує головне Inline-меню бота."""
    builder = InlineKeyboardBuilder()
    builder.button(text=get_str(lang, "btn_recognize"), callback_data="menu_send_photo")
    builder.button(text=get_str(lang, "btn_settings"), callback_data="menu_settings")
    builder.button(text=get_str(lang, "btn_help"), callback_data="menu_help")
    builder.button(text=get_str(lang, "btn_web"), url="https://smarthub-1vrp.onrender.com") 
    
    builder.adjust(1, 2, 1)
    return builder.as_markup()
    
def get_settings_menu(lang: str = "ukr") -> InlineKeyboardMarkup:
    """Меню вибору стратегії розпізнавання (Pattern Strategy)."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=get_str(lang, "btn_strategy_plain"), callback_data="set_strategy_plain")
    builder.button(text=get_str(lang, "btn_strategy_math"), callback_data="set_strategy_math")
    builder.button(text=get_str(lang, "btn_back"), callback_data="menu_main")
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_settings_keyboard(lang: str = "ukr") -> InlineKeyboardMarkup:
    """Генерує інлайн-клавіатуру для вибору мови OCR."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=get_str(lang, "btn_lang_ukr"), callback_data="lang_ukr")
    builder.button(text=get_str(lang, "btn_lang_eng"), callback_data="lang_eng")
    
    builder.adjust(2) 
    return builder.as_markup()

def get_result_keyboard(lang: str = "ukr", record_id: str = "") -> InlineKeyboardMarkup:
    """Клавіатура під результатом OCR з кнопкою Перекладу."""
    builder = InlineKeyboardBuilder()
    builder.button(text=get_str(lang, "btn_translate"), callback_data=f"translate_{record_id}")
    return builder.as_markup()