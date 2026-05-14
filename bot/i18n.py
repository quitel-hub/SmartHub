BOT_STRINGS = {
    "ukr": {
        "btn_recognize": "📤 Розпізнати конспект",
        "btn_settings": "⚙️ Налаштування OCR",
        "btn_help": "ℹ️ Довідка",
        "btn_web": "🌐 Відкрити Web-панель",
        
        "btn_back": "🔙 Назад",
        "btn_translate": "🔄 Перекласти текст",
        
        "btn_strategy_plain": "📝 Звичайний текст",
        "btn_strategy_math": "🧮 Формули (Math)",
        
        "btn_lang_ukr": "🇺🇦 Українська",
        "btn_lang_eng": "🇬🇧 English",
        
        "msg_welcome": "Привіт, <b>{}</b>! 👋\nЯ <b>SmartHub</b> - аналізатор конспектів.\nОбери дію:",
        "msg_send_photo": "📸 <b>Чекаю на фото!</b>\nНадішли зображення для розпізнавання.",
        "msg_help": "🛠 <b>Довідка:</b>\nНадішли фото, і я розпізнаю його через Tesseract OCR.",
        "msg_recognized": "✅ <b>Текст успішно розпізнано:</b>\n\n<code>{}</code>",
        "msg_translated": "🇺🇸/🇬🇧 <b>Переклад (English):</b>\n\n<code>{}</code>",
        "msg_main_menu": "Головне меню 🏠\nОбери потрібну дію:",
        "msg_settings_strategy": "⚙️ <b>Налаштування OCR</b>\n\nОбери алгоритм:",
        "msg_settings_lang": "Поточна мова: **{}**\n\nОбери нову:",
        "msg_wait": "⏳ Зачекайте, я ще обробляю фото!",
        "msg_photo_received": "📸 Фото отримано! Розпізнаю...",
        "msg_text_not_found": "Текст не знайдено."
    },
    "eng": {
        "btn_recognize": "📤 Recognize Notes",
        "btn_settings": "⚙️ OCR Settings",
        "btn_help": "ℹ️ Help",
        "btn_web": "🌐 Open Dashboard",
        
        "btn_back": "🔙 Back",
        "btn_translate": "🔄 Translate Text",
        
        "btn_strategy_plain": "📝 Plain Text",
        "btn_strategy_math": "🧮 Math Formulas",
        
        "btn_lang_ukr": "🇺🇦 Ukrainian",
        "btn_lang_eng": "🇬🇧 English",
        
        "msg_welcome": "Hello, <b>{}</b>! 👋\nI am <b>SmartHub</b> - notes analyzer.\nChoose an action:",
        "msg_send_photo": "📸 <b>Awaiting photo!</b>\nSend an image for processing.",
        "msg_help": "🛠 <b>Help:</b>\nSend a photo and I will run Tesseract OCR extraction.",
        "msg_recognized": "✅ <b>Successfully extracted:</b>\n\n<code>{}</code>",
        "msg_translated": "🇺🇦 <b>Translation (Ukrainian):</b>\n\n<code>{}</code>",
        "msg_main_menu": "Main Menu 🏠\nChoose an action:",
        "msg_settings_strategy": "⚙️ <b>OCR Settings</b>\n\nChoose algorithm:",
        "msg_settings_lang": "Current language: **{}**\n\nChoose new:",
        "msg_wait": "⏳ Please wait, processing previous photo!",
        "msg_photo_received": "📸 Photo received! Extracting...",
        "msg_text_not_found": "Text not found."
    }
}

def get_str(lang: str, key: str) -> str:
    """Отримує рядок для потрібної мови (fallback на ukr)"""
    return BOT_STRINGS.get(lang, BOT_STRINGS["ukr"]).get(key, key)