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
from bot.keyboards import get_main_menu, get_settings_menu, get_settings_keyboard, get_reply_main_menu, get_result_keyboard
from services.database import DatabaseAdapter
from googletrans import Translator
from bot.i18n import get_str

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
translator = Translator()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(UserState.idle)
    lang = db.get_user_lang(message.from_user.id)
    text = get_str(lang, "msg_welcome").format(message.from_user.first_name)
    await message.answer(text, reply_markup=get_reply_main_menu(lang), parse_mode="HTML")
    
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

@router.message(F.text == "📤 Розпізнати конспект")
async def handle_reply_send_photo(message: Message):
    await message.answer(
        "📸 <b>Чекаю на фото!</b>\n\nНадішли мені зображення конспекту або білета, і я почну розпізнавання.",
        parse_mode="HTML"
    )

@router.message(F.text == "ℹ️ Довідка")
async def handle_reply_help(message: Message):
    help_text = (
        "🛠 <b>Довідка SmartHub:</b>\n\n"
        "1. Натисни «Розпізнати конспект».\n"
        "2. Надішли одне або декілька фото.\n"
        "3. Бот використає <i>Tesseract OCR</i> та збереже дані в Supabase."
    )
    await message.answer(help_text, parse_mode="HTML")
    
    
@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_help_obj.execute(message)
    

@router.message(F.photo)
async def handle_photo(message: Message, bot, state: FSMContext):
    """Обробник фото з патерном State: блокування спаму"""
    current_state = await state.get_state()
    lang = db.get_user_lang(message.from_user.id)
    
    if current_state == UserState.processing.state:
        wait_msg = "⏳ Зачекайте, я ще обробляю фото!" if lang == "ukr" else "⏳ Please wait, processing previous photo!"
        await message.answer(wait_msg)
        return
    
    await state.set_state(UserState.processing)
    
    try:
        status_text = "📸 Фото отримано! Розпізнаю..." if lang == "ukr" else "📸 Photo received! Extracting..."
        status_msg = await message.answer(status_text)
        
        photo_id = message.photo[-1].file_id
        file_info = await bot.get_file(photo_id)
        os.makedirs("temp_downloads", exist_ok=True)
        file_path = f"temp_downloads/{photo_id}.jpg"
        await bot.download_file(file_info.file_path, destination=file_path)
        
        doc_type = "math_exam" 
        processor = ProcessorFactory.create_processor(doc_type)
        
        document = SinglePageDocument(file_path)
        raw_text = await pool.run_in_thread(document.process, processor)
        
        # 1. СТВОРЮЄМО ЗМІННУ record_id
        record_id = f"doc_{message.message_id}"
        
        # 2. ЗБЕРІГАЄМО ТЕКСТ У СТЕЙТ ДЛЯ ПЕРЕКЛАДАЧА
        await state.update_data({f"text_{record_id}": raw_text})
        
        db.save_ocr_record(
            author=message.from_user.first_name,
            doc_type=doc_type,
            content=raw_text
        )
        
        report = (report_builder
                  .set_header("OCR Extraction Result")
                  .set_content(raw_text)
                  .set_metadata(author_name=message.from_user.first_name, doc_type=doc_type)
                  .set_footer()
                  .get_result())
        
        # Видаємо фінальний результат із підключеною кнопкою перекладу
        answer_text = get_str(lang, "msg_recognized").format(raw_text)
        await message.answer(
            answer_text, 
            reply_markup=get_result_keyboard(lang, record_id),
            parse_mode="HTML"
        )
        
        await event_manager.notify(report, message, status_msg)
            
    finally:
        await state.set_state(UserState.idle)
        
@router.message(Command("settings"))
@router.message(F.text == "⚙️ Налаштування OCR") 
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

@router.callback_query(F.data.startswith("translate_"))
async def process_translation(callback: CallbackQuery, state: FSMContext):
    record_id = callback.data.split("_")[1]
    lang = db.get_user_lang(callback.from_user.id)
    target_lang = 'en' if lang == 'ukr' else 'uk'
    
    data = await state.get_data()
    original_text = data.get(f"text_{record_id}", "Текст для перекладу не знайдено.")
    
    try:
        translated = translator.translate(original_text, dest=target_lang)
        result_text = translated.text
    except Exception as e:
        result_text = f"Translation error: {e}"
        
    response_msg = get_str(lang, "msg_translated").format(result_text)
    await callback.message.reply(response_msg, parse_mode="HTML")
    await callback.answer()