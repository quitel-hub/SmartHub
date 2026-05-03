import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web

load_dotenv() 

from bot.handlers import router
from services.database import DatabaseAdapter

async def handle(request):
    return web.Response(text="SmartHub Bot is Running!")

async def main():
    
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000)) 
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server started on port {port}")
    
    db = DatabaseAdapter()
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("🚀 Starting SmartHub Bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())