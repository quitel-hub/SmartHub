from abc import ABC, abstractmethod
from core.document_processor import DocumentProcessor

# PATTERN 12: COMPOSITE

class ProcessableDocument(ABC):
    """
    @brief Абстрактний базовий клас для всіх документів (Component у патерні Composite).
    
    Визначає спільний інтерфейс для одиничних сторінок та їх колекцій, 
    дозволяючи клієнту однаково працювати з ними.
    """
    @abstractmethod
    def process(self, processor: DocumentProcessor) -> str:
        """
        @brief Абстрактний метод обробки документа.
        
        @param processor Об'єкт процесора (наслідник DocumentProcessor).
        @return Результат обробки тексту.
        """
        pass

class SinglePageDocument(ProcessableDocument):
    """
    @brief Класичний одиничний документ (Leaf у патерні Composite).
    
    Представляє одну фотографію або сторінку конспекту.
    """
    def __init__(self, file_path: str):
        """
        @brief Ініціалізує одиничний документ.
        @param file_path Шлях до файлу зображення.
        """
        self.file_path = file_path

    def process(self, processor: DocumentProcessor) -> str:
        """
        @brief Виконує обробку однієї сторінки за допомогою процесора.
        
        @param processor Об'єкт процесора для розпізнавання.
        @return Розпізнаний текст сторінки.
        """
        return processor.process_document(self.file_path)

class MultiPageDocument(ProcessableDocument):
    """
    @brief Колекція документів (Composite у патерні Composite).
    
    Може містити як SinglePageDocument, так і інші MultiPageDocument 
    (наприклад, конспект, що складається з кількох фотографій).
    """
    def __init__(self):
        """@brief Ініціалізує порожню колекцію сторінок."""
        self.pages = []

    def add_page(self, document: ProcessableDocument):
        """
        @brief Додає сторінку до колекції.
        @param document Об'єкт документа (SinglePageDocument або MultiPageDocument).
        """
        self.pages.append(document)

    def remove_page(self, document: ProcessableDocument):
        """
        @brief Видаляє сторінку з колекції.
        @param document Об'єкт документа для видалення.
        """
        self.pages.remove(document)

    def process(self, processor: DocumentProcessor) -> str:
        """
        @brief Послідовно обробляє всі сторінки в колекції.
        
        @param processor Об'єкт процесора для розпізнавання.
        @return Об'єднаний текст з усіх сторінок із розділителями.
        """
        results = []
        for i, page in enumerate(self.pages, 1):
            results.append(f"\n📄 <b>--- Сторінка {i} ---</b>\n")
            results.append(page.process(processor))
        
        return "\n".join(results)