from abc import ABC, abstractmethod
from aiogram.types import Message


# PATTERN 5: COMMAND
class BotCommand(ABC):
    """
    @brief Інтерфейс для обробки команд Telegram-бота (Патерн Command).
    
    Інкапсулює запит як об'єкт, дозволяючи параметризувати клієнтів 
    із різними запитами та підтримувати скасування операцій.
    """
    @abstractmethod
    async def execute(self, message: Message):
        """
        @brief Виконує команду.
        @param message Об'єкт повідомлення від Telegram.
        """
        pass

class StartCommand(BotCommand):
    """
    @brief Конкретна команда для обробки `/start`.
    """
    async def execute(self, message: Message):
        welcome_text = (
            f"Привіт, {message.from_user.first_name}! 👋\n\n"
            "Я SmartHub - твій інтелектуальний аналізатор конспектів.\n"
            "Просто надішли мені фото лекції або дошки, і я розпізнаю текст, "
            "витягну терміни та збережу їх у базу!"
        )
        await message.answer(welcome_text)

class HelpCommand(BotCommand):
    """
    @brief Конкретна команда для обробки `/help`.
    """
    async def execute(self, message: Message):
        help_text = (
            "🛠 **Довідка SmartHub:**\n"
            "1. Надішли фото конспекту або білета.\n"
            "2. Дочекайся завершення обробки OCR.\n"
            "3. Бот автоматично згенерує звіт."
        )
        await message.answer(help_text, parse_mode="Markdown")