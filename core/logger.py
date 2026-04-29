import logging
import time
from functools import wraps

# Налаштування базового логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs/smarthub.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SmartHub")

def performance_logger(func):
    """
    @brief Декоратор для логування продуктивності виконання функцій.
    
    Записує в лог час початку виконання функції та загальний 
    витрачений час після її завершення.
    
    @param func Функція, яку потрібно обгорнути декоратором.
    @return Обгорнута функція.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Started executing: {func.__name__}")
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        logger.info(f"Finished {func.__name__} in {end_time - start_time:.2f} seconds.")
        return result
    return wrapper