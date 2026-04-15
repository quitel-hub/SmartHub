from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """Генерує головне Inline-меню бота."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📤 Розпізнати конспект", callback_data="menu_send_photo")
    builder.button(text="⚙️ Налаштування OCR", callback_data="menu_settings")
    builder.button(text="ℹ️ Довідка", callback_data="menu_help")
    builder.button(text="🌐 Відкрити Web-панель", url="https://smart-hub-psi.vercel.app/") 
    
    builder.adjust(1, 2, 1)
    
    return builder.as_markup()

def get_settings_menu() -> InlineKeyboardMarkup:
    """Меню вибору стратегії розпізнавання (Pattern Strategy)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Звичайний текст", callback_data="set_strategy_plain")
    builder.button(text="🧮 Формули (Math)", callback_data="set_strategy_math")
    builder.button(text="🔙 Назад", callback_data="menu_main")
    builder.adjust(2, 1)
    return builder.as_markup()