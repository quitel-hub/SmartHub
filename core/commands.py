from abc import ABC, abstractmethod
from aiogram.types import Message


# PATTERN 5: COMMAND
class BotCommand(ABC):
    """The Command interface for handling Telegram bot commands."""
    @abstractmethod
    async def execute(self, message: Message):
        pass

class StartCommand(BotCommand):
    """Concrete command for /start"""
    async def execute(self, message: Message):
        welcome_text = (
            f"Привіт, {message.from_user.first_name}! 👋\n\n"
            "Я SmartHub - твій інтелектуальний аналізатор конспектів.\n"
            "Просто надішли мені фото лекції або дошки, і я розпізнаю текст, "
            "витягну терміни та збережу їх у базу!"
        )
        await message.answer(welcome_text)

class HelpCommand(BotCommand):
    """Concrete command for /help"""
    async def execute(self, message: Message):
        help_text = (
            "🛠 **Довідка SmartHub:**\n"
            "1. Надішли фото конспекту або білета.\n"
            "2. Дочекайся завершення обробки OCR.\n"
            "3. Бот автоматично згенерує звіт."
        )
        await message.answer(help_text, parse_mode="Markdown")