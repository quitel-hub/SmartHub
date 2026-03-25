from concurrent.futures import ThreadPoolExecutor
import asyncio

class ProcessorPool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProcessorPool, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=4)
        return cls._instance

    async def run_in_thread(self, func, *args):
        """Runs a blocking function in a background thread."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)