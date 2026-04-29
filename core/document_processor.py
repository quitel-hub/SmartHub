from abc import ABC, abstractmethod
import cv2
import pytesseract
from core.text_decorators import BasicTextProcessor, StripWhitespaceDecorator, AutoCorrectDecorator

# PATTERN 1: STRATEGY
class OCRStrategy(ABC):
    """
    @brief Абстрактна стратегія розпізнавання тексту (Strategy Pattern).
    """
    @abstractmethod
    def extract(self, image) -> str:
        """@brief Витягує текст із зображення."""
        pass

class StandardTextStrategy(OCRStrategy):
    """@brief Стратегія для розпізнавання звичайних текстових документів."""
    def extract(self, image) -> str:
        return pytesseract.image_to_string(image, lang='ukr+eng')

class MathExamStrategy(OCRStrategy):
    """@brief Стратегія для складних макетів та математичних формул."""
    def extract(self, image) -> str:
        custom_config = r'--oem 3 --psm 3'
        return pytesseract.image_to_string(image, lang='ukr+eng', config=custom_config)


# PATTERN 2: TEMPLATE METHOD
class DocumentProcessor(ABC):
    """
    @brief Визначає скелет алгоритму обробки документа (Template Method).
    
    Реалізує загальну послідовність (завантаження -> препроцесинг -> розпізнавання -> очищення),
    дозволяючи підкласам перевизначати конкретні кроки.
    """
    def __init__(self, strategy: OCRStrategy):
        self.strategy = strategy
        self.tesseract_cmd = r'F:\Projects\tesseract\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def process_document(self, file_path: str) -> str:
        """
        @brief Шаблонний метод, що викликає кроки алгоритму у суворому порядку.
        
        @param file_path Шлях до файлу зображення.
        @return Відформатований розпізнаний текст.
        """
        image = self._load_image(file_path)
        if image is None:
            return "Error: Image not found or cannot be read."
        
        processed_image = self._preprocess(image)
        raw_text = self._extract_text(processed_image)
        
        processor = BasicTextProcessor()              
        processor = StripWhitespaceDecorator(processor)  
        processor = AutoCorrectDecorator(processor)      
        clean_text = processor.process(raw_text)
        
        return self._format_result(clean_text)

    def _load_image(self, file_path: str):
        """@brief Крок 1: Завантаження зображення через OpenCV."""
        return cv2.imread(file_path)

    @abstractmethod
    def _preprocess(self, image):
        """
        @brief Крок 2: Попереднє оброблення (має бути реалізовано у підкласах).
        """
        pass

    def _extract_text(self, image) -> str:
        """@brief Крок 3: Виконання OCR через делегування стратегії."""
        return self.strategy.extract(image)

    def _format_result(self, text: str) -> str:
        """@brief Крок 4: Фінальне форматування."""
        return text.strip()


class ExamPaperProcessor(DocumentProcessor):
    """
    @brief Конкретна реалізація обробника для екзаменаційних білетів.
    """
    def _preprocess(self, image):
        """@brief Переводить зображення у відтінки сірого та застосовує поріг Otsu."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return processed_img
    
class ProcessorFactory:
    """
    @brief Фабрика для створення обробників документів (Factory Method).
    
    Інкапсулює логіку вибору та інстанціювання правильного процесора 
    та стратегії залежно від типу документа.
    """
    @staticmethod
    def create_processor(doc_type: str) -> DocumentProcessor:
        """
        @brief Створює обробник на основі типу документа.
        
        @param doc_type Тип документа (наприклад, 'math_exam' або 'plain_text').
        @return Налаштований екземпляр DocumentProcessor.
        @raises ValueError Якщо тип документа невідомий.
        """
        if doc_type == "math_exam":
            return ExamPaperProcessor(MathExamStrategy())
        elif doc_type == "plain_text":
            return ExamPaperProcessor(StandardTextStrategy())
        else:
            raise ValueError(f"Unknown document type: {doc_type}")