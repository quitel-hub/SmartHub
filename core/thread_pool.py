from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading

class ProcessorPool:
    """
    @brief Реалізація патерну Singleton для управління пулом потоків.
    
    Забезпечує паралельне виконання синхронних завдань (наприклад, OCR розпізнавання 
    або запити до Google Sheets) у фонових потоках, щоб не блокувати головний 
    асинхронний цикл подій Telegram-бота.
    """
    
    _instance = None
    _init_lock = threading.Lock()

    def __new__(cls):
        """
        @brief Гарантує створення та повернення лише одного екземпляра пулу (Singleton).
        
        Використовує блокування (Lock) для забезпечення потокобезпеки 
        при першому створенні об'єкта.
        """
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super(ProcessorPool, cls).__new__(cls)
                cls._instance.executor = ThreadPoolExecutor(max_workers=4)
                cls._instance.db_lock = threading.Lock()
            return cls._instance

    async def run_in_thread(self, func, *args):
        """
        @brief Запускає синхронну (блокуючу) функцію у фоновому потоці.
        
        @param func Функція, яку потрібно виконати.
        @param args Аргументи, які передаються у функцію.
        @return Результат виконання функції `func`.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)