import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from core.thread_pool import ProcessorPool
from core.ocr_engine import OCREngine
from core.text_decorators import BasicTextProcessor, StripWhitespaceDecorator, AutoCorrectDecorator
from core.observer import DocumentEventManager, Observer
from core.composite import SinglePageDocument, MultiPageDocument
from core.document_processor import DocumentProcessor, ProcessorFactory, ExamPaperProcessor, MathExamStrategy
from core.report_builder import ReportBuilder
from core.commands import StartCommand, HelpCommand
from core.google_sheets_adapter import GoogleSheetsAdapter
from services.database import DatabaseAdapter
from bot.states import UserState


class TestSmartHubCore(unittest.TestCase):
    
    def test_singleton_thread_pool(self):
        """Перевірка патерну Singleton: має бути лише один екземпляр пулу потоків"""
        pool1 = ProcessorPool()
        pool2 = ProcessorPool()
        self.assertIs(pool1, pool2, "ProcessorPool does not implement Singleton correctly!")

    def test_singleton_database_adapter(self):
        """Перевірка патерну Singleton для підключення до БД (Supabase)"""
        db1 = DatabaseAdapter()
        db2 = DatabaseAdapter()
        self.assertIs(db1, db2, "DatabaseAdapter повинен бути Singleton, щоб не плодити з'єднання!")

    def test_ocr_engine_initialization(self):
        """Перевірка ініціалізації фасаду OCREngine"""
        engine = OCREngine()
        self.assertIsNotNone(engine.tesseract_cmd)
        self.assertTrue(engine.tesseract_cmd.endswith("tesseract.exe") or engine.tesseract_cmd == "tesseract")

    def test_missing_image_handling(self):
        """Перевірка коректної обробки помилок при відсутності файлу (Template Method / Facade)"""
        engine = OCREngine()
        result = engine.extract_text("fake_path_123.jpg")
        self.assertIn("Error", result, "Engine should return an error string for missing files")

    def test_builder_pattern(self):
        """Перевірка Builder: покрокова побудова звіту"""
        builder = ReportBuilder()
        report = (builder
              .set_header("Test Title")
              .set_content("Sample text")
              .set_metadata("Kirilo", "math")
              .get_result())
        
        self.assertIn("Test Title", report.header)
        self.assertIn("Sample text", report.content)
        self.assertIn("Kirilo", report.metadata)

    def test_factory_method_pattern(self):
        """Перевірка Factory: створення правильного процесора"""
        processor = ProcessorFactory.create_processor("math_exam")
        self.assertIsInstance(processor, ExamPaperProcessor)
        self.assertIsInstance(processor.strategy, MathExamStrategy)

    def test_decorator_pattern(self):
        """Перевірка патерну Decorator: очистка тексту та автовиправлення"""
        raw_text = "Ось текст лекції. \n\n\n Термін 0 означає початкову точку. Цей алгорітм складний."
        
        processor = BasicTextProcessor()
        processor = StripWhitespaceDecorator(processor)
        processor = AutoCorrectDecorator(processor)
        
        result = processor.process(raw_text)
        self.assertIn("Термін O означає", result)
        self.assertIn("алгоритм", result)
        self.assertNotIn("алгорітм", result)
        self.assertNotIn("\n\n\n", result) 

    def test_composite_pattern(self):
        """Перевірка патерну Composite: обробка кількох сторінок як однієї сутності"""
        mock_processor = MagicMock(spec=DocumentProcessor)
        mock_processor.process_document.side_effect = ["Текст першої сторінки", "Текст другої сторінки"]

        doc1 = SinglePageDocument("page1.jpg")
        doc2 = SinglePageDocument("page2.jpg")
        
        folder = MultiPageDocument()
        folder.add_page(doc1)
        folder.add_page(doc2)

        result = folder.process(mock_processor)

        self.assertIn("--- Сторінка 1 ---", result)
        self.assertIn("Текст першої сторінки", result)
        self.assertIn("--- Сторінка 2 ---", result)
        self.assertIn("Текст другої сторінки", result)

    def test_state_pattern_states(self):
        """Перевірка наявності потрібних станів у FSM (State Pattern)"""
        self.assertIsNotNone(UserState.idle, "Стан 'idle' має існувати для очікування")
        self.assertIsNotNone(UserState.processing, "Стан 'processing' має існувати для блокування спаму")

    @patch('services.database.DatabaseAdapter.get_user_lang')
    def test_database_mock_get_lang(self, mock_get_lang):
        """Перевірка логіки БД (Mocking) на отримання мови користувача"""
        mock_get_lang.return_value = "eng"
        db = DatabaseAdapter()
        lang = db.get_user_lang(123456)
        self.assertEqual(lang, "eng", "Адаптер БД повинен повертати коректну мову")


class TestSmartHubAsync(unittest.IsolatedAsyncioTestCase):
    
    async def test_command_pattern(self):
        """Перевірка Command: виконання команд бота"""
        mock_message = AsyncMock()
        mock_message.from_user.first_name = "Kirilo"
        
        start_cmd = StartCommand()
        with patch('services.database.DatabaseAdapter.get_user_lang', return_value='ukr'):
            await start_cmd.execute(mock_message)
            
        mock_message.answer.assert_called()
        args = mock_message.answer.call_args[0][0]
        self.assertIn("Привіт, Kirilo", args)  
    async def test_observer_pattern(self):
        """Перевірка патерну Observer: чи викликається update у підписників"""
        manager = DocumentEventManager()
        
        mock_telegram_observer = AsyncMock(spec=Observer)
        mock_sheets_observer = AsyncMock(spec=Observer)
        
        manager.subscribe(mock_telegram_observer)
        manager.subscribe(mock_sheets_observer)
        
        await manager.notify("Fake Report", "Fake Msg", "Fake Status Msg")
        
        mock_telegram_observer.update.assert_called_once_with("Fake Report", "Fake Msg", "Fake Status Msg")
        mock_sheets_observer.update.assert_called_once_with("Fake Report", "Fake Msg", "Fake Status Msg")
        
    async def test_fsm_state_blocking(self):
        """Перевірка логіки блокування спаму через машину станів (State)"""
        mock_state = AsyncMock()
        mock_state.get_state.return_value = UserState.processing.state
        
        current_state = await mock_state.get_state()
        self.assertEqual(current_state, "UserState:processing", "Стан має блокувати нові фотографії")

if __name__ == '__main__':
    unittest.main()