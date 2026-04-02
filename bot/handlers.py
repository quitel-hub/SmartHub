import os
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

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

SPREADSHEET_ID = "11Xvb3qQ3ZfVRkIp7TBgcJgd7WIYzfNbnTLzV9fq4K0w" 
sheets_adapter = GoogleSheetsAdapter(SPREADSHEET_ID)


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обробник команди /start"""
    welcome_text = (
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        "Я SmartHub - твій інтелектуальний аналізатор конспектів.\n"
        "Просто надішли мені фото лекції або дошки, і я розпізнаю текст, "
        "витягну терміни та збережу їх у базу!"
    )
    await message.answer(welcome_text)

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
        
        raw_text = await pool.run_in_thread(processor.process_document, file_path)
        
        report = (report_builder
                  .set_header("OCR Extraction Result")
                  .set_content(raw_text)
                  .set_metadata(author_name=message.from_user.first_name, doc_type=doc_type)
                  .set_footer()
                  .get_result())
        
        await status_msg.edit_text(str(report), parse_mode="HTML")
        is_saved = await pool.run_in_thread(sheets_adapter.save_report, report, message.from_user.id)
        if is_saved:
            await message.answer("✅ Дані також успішно експортовано в Google Таблицю!")
            
    finally:
        await state.set_state(UserState.idle)