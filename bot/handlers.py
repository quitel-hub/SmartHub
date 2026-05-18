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
from deep_translator import GoogleTranslator
from bot.i18n import get_str, BOT_STRINGS

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
    lang = db.get_user_lang(message.from_user.id)
    text = get_str(lang, "msg_welcome").format(message.from_user.first_name)
    await message.answer(text, reply_markup=get_reply_main_menu(lang), parse_mode="HTML")
    
@router.callback_query(F.data == "menu_main")
async def process_main_menu(callback: CallbackQuery):
    lang = db.get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_str(lang, "msg_main_menu"), 
        reply_markup=get_main_menu(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "menu_send_photo")
async def process_send_photo(callback: CallbackQuery):
    lang = db.get_user_lang(callback.from_user.id)
    back_btn_text = get_str(lang, "btn_back")
    
    await callback.message.edit_text(
        get_str(lang, "msg_send_photo"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardBuilder().button(text=back_btn_text, callback_data="menu_main").as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_settings")
async def process_settings(callback: CallbackQuery):
    lang = db.get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_str(lang, "msg_settings_strategy"),
        parse_mode="HTML",
        reply_markup=get_settings_menu(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "menu_help")
async def process_help_callback(callback: CallbackQuery):
    lang = db.get_user_lang(callback.from_user.id)
    back_btn_text = get_str(lang, "btn_back")
    
    await callback.message.edit_text(
        get_str(lang, "msg_help"), 
        parse_mode="HTML",
        reply_markup=InlineKeyboardBuilder().button(text=back_btn_text, callback_data="menu_main").as_markup()
    )
    await callback.answer()

@router.message(F.text.in_([BOT_STRINGS["ukr"]["btn_recognize"], BOT_STRINGS["eng"]["btn_recognize"]]))
async def handle_reply_send_photo(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    await message.answer(get_str(lang, "msg_send_photo"), parse_mode="HTML")

@router.message(F.text.in_([BOT_STRINGS["ukr"]["btn_help"], BOT_STRINGS["eng"]["btn_help"]]))
async def handle_reply_help(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    await message.answer(get_str(lang, "msg_help"), parse_mode="HTML")

@router.message(Command("settings"))
@router.message(F.text.in_([BOT_STRINGS["ukr"]["btn_settings"], BOT_STRINGS["eng"]["btn_settings"]])) 
async def cmd_settings(message: Message):
    lang = db.get_user_lang(message.from_user.id)
    lang_name = get_str(lang, "btn_lang_ukr") if lang == "ukr" else get_str(lang, "btn_lang_eng")
    text = get_str(lang, "msg_settings_lang").format(lang_name)
    await message.answer(text, reply_markup=get_settings_keyboard(lang), parse_mode="Markdown")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_help_obj.execute(message)
    

@router.message(F.photo)
async def handle_photo(message: Message, bot, state: FSMContext):
    current_state = await state.get_state()
    lang = db.get_user_lang(message.from_user.id)
    
    if current_state == UserState.processing.state:
        await message.answer(get_str(lang, "msg_wait"))
        return
    
    await state.set_state(UserState.processing)
    
    try:
        status_msg = await message.answer(get_str(lang, "msg_photo_received"))
        
        photo_id = message.photo[-1].file_id
        file_info = await bot.get_file(photo_id)
        os.makedirs("temp_downloads", exist_ok=True)
        file_path = f"temp_downloads/{photo_id}.jpg"
        await bot.download_file(file_info.file_path, destination=file_path)
        
        doc_type = "math_exam" 
        processor = ProcessorFactory.create_processor(doc_type)
        
        document = SinglePageDocument(file_path)
        raw_text = await pool.run_in_thread(document.process, processor)
        
        record_id = f"doc_{message.message_id}"
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
        
        answer_text = get_str(lang, "msg_recognized").format(raw_text)
        await message.answer(
            answer_text, 
            reply_markup=get_result_keyboard(lang, record_id),
            parse_mode="HTML"
        )
        
        await event_manager.notify(report, message, status_msg)
            
    finally:
        await state.set_state(UserState.idle)
        
@router.callback_query(F.data.startswith("lang_"))
async def process_lang_selection(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]  
    
    db.set_user_lang(callback.from_user.id, lang_code)
    ack_msg = "Мову змінено на Українську 🇺🇦" if lang_code == "ukr" else "Language changed to English 🇬🇧"
    await callback.answer(ack_msg)
    
    await callback.message.delete()
    
    text = get_str(lang_code, "msg_welcome").format(callback.from_user.first_name)
    await callback.message.answer(
        text,
        reply_markup=get_reply_main_menu(lang_code), 
        parse_mode="HTML"
    )