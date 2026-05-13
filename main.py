import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web
from core.google_sheets_adapter import GoogleSheetsAdapter

load_dotenv() 

from bot.handlers import router
from services.database import DatabaseAdapter

async def get_records(request):
    try:
        gs_adapter = GoogleSheetsAdapter()
        # Отримуємо дані з Sheets (використовуємо існуючий метод адаптера)
        rows = gs_adapter.sheet.get_all_values() 
        
        if not rows:
            return web.json_response([])

        records = []
        for index, row in enumerate(rows):
            # Парсинг метаданих (як у нашому JS коді)
            meta = row[0] if len(row) > 0 else ""
            content = row[3] if len(row) > 3 else "Текст відсутній"
            
            records.append({
                "id": str(index),
                "author": "User", # Можна розпарсити meta регулярками за потреби
                "docType": "OCR",
                "date": "",
                "content": content
            })
            
        return web.json_response(records[::-1]) # Реверс, щоб нові були зверху
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
    

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
    
    app.router.add_get("/api/records", get_records)
    
if __name__ == "__main__":
    asyncio.run(main())