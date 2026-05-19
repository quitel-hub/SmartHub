"""
@file main.py
@brief Головний модуль запуску екосистеми SmartHub (Веб-сервер + Telegram-бот).

Цей файл ініціалізує та запускає асинхронний веб-сервер на базі aiohttp 
для обслуговування React-дашборду та REST API. Паралельно у фоновому 
режимі запускається Telegram-бот на базі aiogram.
"""

import asyncio
import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiohttp import web
from aiogram.types import BotCommand

load_dotenv()

from bot.handlers import router
from services.database import DatabaseAdapter


async def setup_bot_commands(bot: Bot):
    """Встановлює системне меню команд Telegram (кнопка зліва від введення)."""
    commands = [
        BotCommand(command="start", description="🚀 Головне меню та перезапуск"),
        BotCommand(command="settings", description="⚙️ Налаштування мови та OCR"),
        BotCommand(command="help", description="ℹ️ Довідка по роботі з ботом"),
    ]
    await bot.set_my_commands(commands)
    

async def api_get_records(request):
    """
    @brief Обробник REST API для отримання історії розпізнаних конспектів.
    
    Виконує запит до бази даних Supabase та форматує результати 
    для відображення на React-дашборді.
    
    @param request Об'єкт aiohttp.web.Request із даними HTTP-запиту.
    @return JSON-відповідь (aiohttp.web.Response) з масивом об'єктів конспектів.
    """
    try:
        db_adapter = DatabaseAdapter()
        records_data = db_adapter.get_all_records()
      
        formatted_records = []
        for row in records_data:
            formatted_records.append({
                "id": str(row.get("id")),
                "author": row.get("author", "Анонім"),
                "docType": row.get("doc_type", "plain_text"),
                "date": row.get("created_at", "").split("T")[0] if row.get("created_at") else "Нещодавно",
                "content": row.get("content", "Текст відсутній")
            })
            
        return web.json_response(formatted_records)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_translate(request):
    """
    @brief Обробник REST API для асинхронного перекладу тексту "на льоту".
    
    Загортає синхронний виклик deep-translator у окремий потік 
    (через asyncio.to_thread), щоб запобігти блокуванню головного event loop.
    
    @param request Об'єкт aiohttp.web.Request, що очікує JSON із ключами 'text' та 'target'.
    @return JSON-відповідь (aiohttp.web.Response) з ключем 'translated'.
    """
    try:
        data = await request.json()
        text = data.get("text", "")
        target_lang = data.get("target", "en")
        
        if not text or text == "Текст відсутній":
            return web.json_response({"translated": "Порожній текст для перекладу."})
            
        from deep_translator import GoogleTranslator
        
        def _do_translate():
            return GoogleTranslator(source='auto', target=target_lang).translate(text)

        translated_text = await asyncio.to_thread(_do_translate)
        
        return web.json_response({"translated": translated_text})
    except Exception as e:
        print(f"Translation API Error: {e}") #
        return web.json_response({"error": str(e)}, status=500)

async def serve_favicon(request):
    favicon_path = os.path.join("static", "favicon.svg")
    if os.path.exists(favicon_path):
        return web.FileResponse(favicon_path)
    return web.Response(status=404)

async def serve_index(request):
    """
    @brief Роздача головної сторінки React-додатка (SPA).
    
    @param request Об'єкт HTTP-запиту.
    @return aiohttp.web.FileResponse з файлом index.html, або 404 помилка, якщо фронтенд не зібрано.
    """
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return web.FileResponse(index_path)
    return web.Response(text="SmartHub: API is active, but static files are missing.", status=404)


async def main():
    app = web.Application()
    app.router.add_get("/api/records", api_get_records)
    app.router.add_post("/api/translate", api_translate)
    app.router.add_get("/favicon.svg", serve_favicon)
    
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
    await setup_bot_commands(bot)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())