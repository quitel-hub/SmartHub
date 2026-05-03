import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

load_dotenv() 

from bot.handlers import router
from services.database import DatabaseAdapter

async def main():
    print("🚀 Starting SmartHub...")
    db = DatabaseAdapter()
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ Помилка: BOT_TOKEN не знайдено в .env")
        return
    
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("🤖 Bot is successfully started and waiting for messages!")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 SmartHub stopped.")