import asyncio
import os
from dotenv import load_dotenv


load_dotenv()

async def main():
    print("🚀 SmartHub ініціалізовано!")
    print("Запуск пулу потоків...")
    print("Запуск Telegram-бота...")
    
if __name__ == "__main__":
    asyncio.run(main())