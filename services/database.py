"""
@file database.py
@brief Модуль інтеграції з хмарною базою даних Supabase.
"""

import os
from supabase import create_client, Client
from core.logger import get_logger

logger = get_logger(__name__)

class DatabaseAdapter:
    """
    @brief Патерн Адаптер для взаємодії з PostgreSQL через Supabase API.
    
    Забезпечує абстракцію над CRUD-операціями для таблиць користувацьких 
    налаштувань та збереження історії OCR-транскрипцій.
    """
    _instance = None

    def __new__(cls):
        """
        @brief Реалізація патерну Singleton.
        
        Створює новий екземпляр класу лише якщо він ще не існує. 
        В іншому випадку повертає наявний об'єкт.
        
        @return Єдиний (глобальний) екземпляр класу DatabaseAdapter.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseAdapter, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        @brief Внутрішній метод ініціалізації клієнта Supabase.
        
        Зчитує облікові дані (URL та KEY) зі змінних середовища та 
        створює HTTP-клієнт для взаємодії з REST API бази даних.
        """
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            logger.warning("SUPABASE_URL або SUPABASE_KEY не знайдено! Робота з БД неможлива.")
            self.supabase = None
            return

        self.supabase: Client = create_client(url, key)

    def get_user_lang(self, user_id: int) -> str:
        """
        @brief Отримує мову інтерфейсу для конкретного користувача.
        
        @param user_id Унікальний ідентифікатор користувача Telegram.
        @return Код мови (наприклад, 'ukr' або 'eng').
        """
        if not self.supabase:
            return "ukr"
            
        try:
            response = self.supabase.table("user_settings").select("ocr_lang").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]["ocr_lang"]
        except Exception as e:
            logger.error(f"Помилка читання з БД: {e}")
            
        return "ukr"

    def set_user_lang(self, user_id: int, lang_code: str) -> bool:
        """
        @brief Зберігає або оновлює мову інтерфейсу користувача (операція Upsert).
        
        @param user_id Унікальний ідентифікатор користувача Telegram.
        @param lang_code Код нової мови ('ukr' або 'eng').
        @return True у разі успішного оновлення, False — у разі помилки.
        """
        if not self.supabase:
            return False
            
        try:
            data = {"user_id": user_id, "ocr_lang": lang_code}
            self.supabase.table("user_settings").upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Помилка запису в БД: {e}")
            return False
    
    def save_ocr_record(self, author: str, doc_type: str, content: str) -> bool:
        """
        @brief Зберігає результат розпізнавання конспекту в базу даних.
        
        @param author Ім'я або нікнейм користувача.
        @param doc_type Категорія документа (наприклад, 'math_exam').
        @param content Розпізнаний текст документа.
        """
        if not self.supabase:
            return False
        try:
            data = {
                "author": author,
                "doc_type": doc_type,
                "content": content
            }
            self.supabase.table("ocr_records").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Помилка збереження конспекту в БД: {e}")
            return False

    def get_all_records(self) -> list:
        """
        @brief Отримує повну історію збережених конспектів.
        
        Використовується REST API сервером для передачі даних на React-дашборд. 
        Записи автоматично сортуються від найновішого до найстарішого (ORDER BY created_at DESC).
        
        @return Список словників із даними конспектів. Порожній список, якщо даних немає або сталася помилка.
        """
        if not self.supabase:
            return []
        try:
            response = self.supabase.table("ocr_records").select("*").order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Помилка отримання конспектів з БД: {e}")
            return []