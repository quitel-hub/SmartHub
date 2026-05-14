import asyncio
import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web

load_dotenv()

from bot.handlers import router
from services.database import DatabaseAdapter

async def api_get_records(request):
    try:
        records = [
            {
                "id": "1", 
                "author": "Студент", 
                "docType": "math_exam", 
                "date": "2026-05-14", 
                "content": "Розпізнаний текст конспекту з вищої математики..."
            }
        ]
        return web.json_response(records)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def serve_index(request):
    return web.FileResponse(os.path.join("static", "index.html"))

async def main():
    app = web.Application()
    app.router.add_get("/api/records", api_get_records)
    
    static_dir = os.path.join(os.getcwd(), "static")
    if os.path.exists(static_dir):
        app.router.add_static("/assets/", path=os.path.join(static_dir, "assets"), name="assets")
        # Головний роут віддає сам дашборд
        app.router.add_get("/", serve_index)
    else:
        async def fallback(req):
            return web.Response(text="SmartHub: API is running, but static files not found.")
        app.router.add_get("/", fallback)

    # Start Web-dashboard
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server & Dashboard started on port {port}")
    
    # Start bot
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