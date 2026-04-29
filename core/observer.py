from abc import ABC, abstractmethod

# PATTERN 11: OBSERVER

class Observer(ABC):
    """
    @brief Абстрактний інтерфейс спостерігача (Observer).
    
    Керує об'єктами, які повинні реагувати на завершення обробки документа.
    """
    @abstractmethod
    async def update(self, report, original_message, status_msg):
        """
        @brief Метод оновлення стану спостерігача.
        
        @param report Сформований звіт OCRReport.
        @param original_message Оригінальне повідомлення користувача в Telegram.
        @param status_msg Повідомлення зі статусом ("Обробка..."), яке потрібно оновити.
        """
        pass

class DocumentEventManager:
    """
    @brief Менеджер подій (Subject у патерні Observer).
    
    Зберігає список підписників (спостерігачів) та сповіщає їх про події.
    """
    def __init__(self):
        """@brief Ініціалізує порожній список спостерігачів."""
        self._observers = []

    def subscribe(self, observer: Observer):
        """
        @brief Підписує нового спостерігача на події.
        @param observer Об'єкт, що реалізує інтерфейс Observer.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    async def notify(self, report, original_message, status_msg):
        """
        @brief Сповіщає всіх підписаних спостерігачів про готовність результату.
        
        @param report Сформований звіт OCRReport.
        @param original_message Оригінальне повідомлення користувача в Telegram.
        @param status_msg Повідомлення зі статусом для редагування.
        """
        for obs in self._observers:
            await obs.update(report, original_message, status_msg)

class TelegramDisplayObserver(Observer):
    """
    @brief Спостерігач для відображення результату користувачу.
    
    Оновлює статус-повідомлення в Телеграмі готовим розпізнаним текстом.
    """
    async def update(self, report, original_message, status_msg):
        await status_msg.edit_text(str(report), parse_mode="HTML")

class GoogleSheetsObserver(Observer):

    """
    @brief Спостерігач для експорту результатів у хмару.
    
    Фоново зберігає дані в Google Таблицю та відправляє користувачу сповіщення про успіх.
    """
    def __init__(self, sheets_adapter, pool):
        """
        @brief Ініціалізує спостерігача адаптером таблиць та пулом потоків.
        
        @param sheets_adapter Екземпляр GoogleSheetsAdapter.
        @param pool Екземпляр ProcessorPool для виконання зберігання у фоновому потоці.
        """
        self.sheets_adapter = sheets_adapter
        self.pool = pool

    async def update(self, report, original_message, status_msg):
        """@copydoc Observer.update"""
        user_id = original_message.from_user.id
        # Виконуємо синхронне збереження у фоновому потоці
        is_saved = await self.pool.run_in_thread(self.sheets_adapter.save_report, report, user_id)
        if is_saved:
            await original_message.answer("✅ Дані також успішно експортовано в Google Таблицю!")