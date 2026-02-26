import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command


router = Router()

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

@router.message(F.photo)
async def handle_photo(message: Message, bot):
    """Обробник фотографій (конспектів)"""

    status_msg = await message.answer("📸 Фото отримано! Ставлю в чергу на розпізнавання (OCR)...")
    
    photo_id = message.photo[-1].file_id
    file_info = await bot.get_file(photo_id)
    
    os.makedirs("temp_downloads", exist_ok=True)
    file_path = f"temp_downloads/{photo_id}.jpg"
    
    await bot.download_file(file_info.file_path, destination=file_path)
    await status_msg.edit_text(f"✅ Фото успішно збережено для аналізу!\nШлях: `{file_path}`")