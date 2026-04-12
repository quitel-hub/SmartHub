from abc import ABC, abstractmethod
from core.document_processor import DocumentProcessor

# PATTERN 12: COMPOSITE

class ProcessableDocument(ABC):
    """
    Абстрактний базовий клас для всіх документів.
    Визначає спільний інтерфейс для одиничних сторінок та їх колекцій.
    """
    @abstractmethod
    def process(self, processor: DocumentProcessor) -> str:
        pass

class SinglePageDocument(ProcessableDocument):
    """Класичний одиничний документ (одне фото)."""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def process(self, processor: DocumentProcessor) -> str:
        return processor.process_document(self.file_path)

class MultiPageDocument(ProcessableDocument):
    """
    Колекція документів (наприклад, конспект з кількох фотографій).
    Може містити як SinglePageDocument, так і інші MultiPageDocument.
    """
    def __init__(self):
        self.pages = []

    def add_page(self, document: ProcessableDocument):
        self.pages.append(document)

    def remove_page(self, document: ProcessableDocument):
        self.pages.remove(document)

    def process(self, processor: DocumentProcessor) -> str:
        results = []
        for i, page in enumerate(self.pages, 1):
            results.append(f"\n📄 <b>--- Сторінка {i} ---</b>\n")
            results.append(page.process(processor))
        
        return "\n".join(results)