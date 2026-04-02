from abc import ABC, abstractmethod
import cv2
import pytesseract


# PATTERN 1: STRATEGY
class OCRStrategy(ABC):
    """Abstract base class for OCR parsing strategies."""
    @abstractmethod
    def extract(self, image) -> str:
        pass

class StandardTextStrategy(OCRStrategy):
    """Strategy for simple, plain text documents."""
    def extract(self, image) -> str:
        return pytesseract.image_to_string(image, lang='ukr+eng')

class MathExamStrategy(OCRStrategy):
    """Strategy for complex layouts and mathematical formulas."""
    def extract(self, image) -> str:
        custom_config = r'--oem 3 --psm 3'
        return pytesseract.image_to_string(image, lang='ukr+eng', config=custom_config)


# PATTERN 2: TEMPLATE METHOD
class DocumentProcessor(ABC):
    """
    Defines the skeleton of the document processing algorithm.
    Subclasses must implement specific preprocessing steps.
    """
    def __init__(self, strategy: OCRStrategy):
        self.strategy = strategy
        self.tesseract_cmd = r'F:\Projects\tesseract\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def process_document(self, file_path: str) -> str:

        image = self._load_image(file_path)
        if image is None:
            return "Error: Image not found or cannot be read."
        
        processed_image = self._preprocess(image)
        
        text = self._extract_text(processed_image)
        
        return self._format_result(text)

    def _load_image(self, file_path: str):
        return cv2.imread(file_path)

    @abstractmethod
    def _preprocess(self, image):
        """Abstract step: Must be overridden by subclasses."""
        pass

    def _extract_text(self, image) -> str:
        return self.strategy.extract(image)

    def _format_result(self, text: str) -> str:
        return text.strip()


class ExamPaperProcessor(DocumentProcessor):
    """Concrete implementation for exam papers with specific preprocessing."""
    def _preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return processed_img
    
class ProcessorFactory:
    """
    Factory Method pattern: Creates the appropriate DocumentProcessor 
    based on the requested document type.
    """
    @staticmethod
    def create_processor(doc_type: str) -> DocumentProcessor:
        if doc_type == "math_exam":
            return ExamPaperProcessor(MathExamStrategy())
        elif doc_type == "plain_text":
            return ExamPaperProcessor(StandardTextStrategy())
        else:
            raise ValueError(f"Unknown document type: {doc_type}")