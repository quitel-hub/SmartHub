from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading

class ProcessorPool:
    _instance = None
    _init_lock = threading.Lock()

    def __new__(cls):
      with cls._init_lock:
        if cls._instance is None:
            cls._instance = super(ProcessorPool, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=4)
            cls._instance.db_lock = threading.Lock()
        return cls._instance

    async def run_in_thread(self, func, *args):
        """Runs a blocking function in a background thread."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)