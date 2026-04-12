from abc import ABC, abstractmethod

# PATTERN 11: OBSERVER

class Observer(ABC):
    @abstractmethod
    async def update(self, report, original_message, status_msg):
        pass

class DocumentEventManager:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    async def notify(self, report, original_message, status_msg):
        for obs in self._observers:
            await obs.update(report, original_message, status_msg)

class TelegramDisplayObserver(Observer):
    """Оновлює повідомлення в Телеграмі готовим текстом розпізнавання."""
    async def update(self, report, original_message, status_msg):
        await status_msg.edit_text(str(report), parse_mode="HTML")

class GoogleSheetsObserver(Observer):
    """Фоново зберігає дані в таблицю та відправляє сповіщення про успіх."""
    def __init__(self, sheets_adapter, pool):
        self.sheets_adapter = sheets_adapter
        self.pool = pool

    async def update(self, report, original_message, status_msg):
        user_id = original_message.from_user.id
        is_saved = await self.pool.run_in_thread(self.sheets_adapter.save_report, report, user_id)
        if is_saved:
            await original_message.answer("✅ Дані також успішно експортовано в Google Таблицю!")