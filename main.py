import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from bot.handlers import router

load_dotenv()

async def main():
    print("🚀 Starting SmartHub...")
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is not found in the .env file!")
    
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("🤖 Bot is successfully started and waiting for messages!")
    
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 SmartHub stopped.")