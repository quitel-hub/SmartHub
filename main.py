import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from bot.handlers import router

load_dotenv()

async def main():
    print("🚀 Запуск SmartHub")
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN не знайдено у файлі .env!")
    
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("🤖 Бот успішно запущений і чекає на повідомлення!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print ("\n🛑 Роботу SmartHub завершено.")