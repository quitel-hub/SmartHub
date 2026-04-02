import unittest
import os
from core.thread_pool import ProcessorPool
from core.ocr_engine import OCREngine

class TestSmartHubCore(unittest.TestCase):
    
    def test_singleton_thread_pool(self):
        """Перевірка патерну Singleton: має бути лише один екземпляр пулу потоків"""
        pool1 = ProcessorPool()
        pool2 = ProcessorPool()
        self.assertIs(pool1, pool2, "ProcessorPool does not implement Singleton correctly!")

    def test_ocr_engine_initialization(self):
        """Перевірка ініціалізації фасаду OCREngine"""
        engine = OCREngine()
        self.assertIsNotNone(engine.tesseract_cmd)
        self.assertTrue(engine.tesseract_cmd.endswith("tesseract.exe"))

    def test_missing_image_handling(self):
        """Перевірка коректної обробки помилок при відсутності файлу (Template Method / Facade)"""
        engine = OCREngine()
        result = engine.extract_text("fake_path_123.jpg")
        self.assertIn("Error", result, "Engine should return an error string for missing files")

if __name__ == '__main__':
    unittest.main()