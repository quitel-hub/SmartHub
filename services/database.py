import os
from supabase import create_client, Client
from core.logger import get_logger

logger = get_logger(__name__)

class DatabaseAdapter:
    """
    Адаптер для роботи з Supabase.
    Реалізує збереження та отримання налаштувань користувачів.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseAdapter, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            logger.warning("SUPABASE_URL або SUPABASE_KEY не знайдено! Робота з БД неможлива.")
            self.supabase = None
            return

        self.supabase: Client = create_client(url, key)

    def get_user_lang(self, user_id: int) -> str:
        """Отримує мову користувача, за замовчуванням 'ukr'"""
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
        """Зберігає або оновлює мову користувача (Upsert)"""
        if not self.supabase:
            return False
            
        try:
            data = {"user_id": user_id, "ocr_lang": lang_code}
            self.supabase.table("user_settings").upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Помилка запису в БД: {e}")
            return False