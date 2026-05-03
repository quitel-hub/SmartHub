import os
from core.observer import DocumentEventManager, TelegramDisplayObserver, GoogleSheetsObserver
from core.composite import SinglePageDocument   
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards import get_main_menu, get_settings_menu
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, Dispatcher
from bot.keyboards import get_settings_keyboard
from services.database import DatabaseAdapter

from core.document_processor import ProcessorFactory
from core.report_builder import ReportBuilder
from core.thread_pool import ProcessorPool
from core.commands import StartCommand, HelpCommand
from bot.states import UserState
from core.google_sheets_adapter import GoogleSheetsAdapter

router = Router()
pool = ProcessorPool()
report_builder = ReportBuilder()
cmd_start_obj = StartCommand()
cmd_help_obj = HelpCommand()
db = DatabaseAdapter()

SPREADSHEET_ID = "11Xvb3qQ3ZfVRkIp7TBgcJgd7WIYzfNbnTLzV9fq4K0w" 
sheets_adapter = GoogleSheetsAdapter(SPREADSHEET_ID)

event_manager = DocumentEventManager()
event_manager.subscribe(TelegramDisplayObserver())
event_manager.subscribe(GoogleSheetsObserver(sheets_adapter, pool))

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(UserState.idle)
    welcome_text = (
        f"Привіт, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "Я <b>SmartHub</b> - твій інтелектуальний аналізатор конспектів.\n"
        "Обери дію в меню нижче 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="HTML")
    
@router.callback_query(F.data == "menu_main")
async def process_main_menu(callback: CallbackQuery):
    """Повернення до головного меню."""
    await callback.message.edit_text(
        "Головне меню 🏠\nОбери потрібну дію:", 
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_send_photo")
async def process_send_photo(callback: CallbackQuery):
    """Реакція на кнопку 'Розпізнати'."""
    await callback.message.edit_text(
        "📸 <b>Чекаю на фото!</b>\n\nНадішли мені зображення конспекту або білета, і я почну розпізнавання.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Назад", callback_data="menu_main").as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_settings")
async def process_settings(callback: CallbackQuery):
    """Відкриває меню налаштувань стратегії OCR."""
    await callback.message.edit_text(
        "⚙️ <b>Налаштування OCR</b>\n\nОбери алгоритм розпізнавання за замовчуванням:",
        parse_mode="HTML",
        reply_markup=get_settings_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_help")
async def process_help_callback(callback: CallbackQuery):
    """Обробник кнопки Довідка."""
    help_text = (
        "🛠 <b>Довідка SmartHub:</b>\n\n"
        "1. Натисни «Розпізнати конспект».\n"
        "2. Надішли одне або декілька фото.\n"
        "3. Бот використає <i>Tesseract OCR</i> та збереже дані в Google Sheets."
    )
    await callback.message.edit_text(
        help_text, 
        parse_mode="HTML",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Назад", callback_data="menu_main").as_markup()
    )
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_help_obj.execute(message)
    

@router.message(F.photo)
async def handle_photo(message: Message, bot, state: FSMContext):
    """Обробник фото з патерном State: блокування спаму"""
    
    current_state = await state.get_state()
    if current_state == UserState.processing.state:
        await message.answer("⏳ Зачекайте, я ще обробляю ваше попереднє фото! Не поспішайте.")
        return
    
    await state.set_state(UserState.processing)
    
    try:
        status_msg = await message.answer("📸 Фото отримано! Ставлю в чергу на розпізнавання (OCR)...")
        
        photo_id = message.photo[-1].file_id
        file_info = await bot.get_file(photo_id)
        os.makedirs("temp_downloads", exist_ok=True)
        file_path = f"temp_downloads/{photo_id}.jpg"
        await bot.download_file(file_info.file_path, destination=file_path)
        
        doc_type = "math_exam" 
        processor = ProcessorFactory.create_processor(doc_type)
        
        document = SinglePageDocument(file_path)
        raw_text = await pool.run_in_thread(document.process, processor)
        
        report = (report_builder
                  .set_header("OCR Extraction Result")
                  .set_content(raw_text)
                  .set_metadata(author_name=message.from_user.first_name, doc_type=doc_type)
                  .set_footer()
                  .get_result())
        
        await event_manager.notify(report, message, status_msg)
            
    finally:
        await state.set_state(UserState.idle)
        
@router.message(Command("settings"))
@router.message(F.text == "⚙️ Налаштування OCR") # Тепер реагує і на кнопку з меню
async def cmd_settings(message: Message):
    """Обробник команди /settings та кнопки налаштувань"""
    user_id = message.from_user.id
    current_lang = db.get_user_lang(user_id)
    
    lang_name = "Українська 🇺🇦" if current_lang == "ukr" else "English 🇬🇧"
    
    await message.answer(
        f"Поточна мова розпізнавання: **{lang_name}**\n\nОбери нову мову:", 
        reply_markup=get_settings_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback_query: CallbackQuery):
    """Обробник натискань на кнопки вибору мови"""
    user_id = callback_query.from_user.id
    lang_code = callback_query.data.split('_')[1] 
    
    success = db.set_user_lang(user_id, lang_code)
    lang_name = "Українську 🇺🇦" if lang_code == "ukr" else "English 🇬🇧"
    
    if success:
        await callback_query.answer(f"Мову змінено на {lang_name}")
        await callback_query.message.edit_text(
            f"✅ Налаштування збережено!\nПоточна мова: **{lang_name}**\n\nНадішли зображення для обробки.",
            parse_mode="Markdown"
        )
    else:
        await callback_query.answer("Помилка збереження в БД.", show_alert=True)