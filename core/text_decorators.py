from abc import ABC, abstractmethod

# PATTERN 10: DECORATOR

# 1. Базовий інтерфейс (Component)
class TextProcessor(ABC):
    """
    @brief Інтерфейс для обробки тексту після OCR (Component у патерні Decorator).
    """
    @abstractmethod
    def process(self, text: str) -> str:
        """
        @brief Метод для обробки тексту.
        @param text Вхідний текст.
        @return Обмоблений текст.
        """
        pass

# 2. Базовий компонент (Concrete Component)
class BasicTextProcessor(TextProcessor):
    """
    @brief Базовий компонент, який повертає сирий текст без змін (Concrete Component).
    """
    def process(self, text: str) -> str:
        return text

# 3. Базовий клас-декоратор (Base Decorator)
class TextProcessorDecorator(TextProcessor):
    """
    @brief Базовий клас-декоратор (Base Decorator).
    
    Зберігає посилання на вкладений компонент (яким може бути як 
    BasicTextProcessor, так і інший декоратор) і делегує йому виконання.
    """
    def __init__(self, wrapper: TextProcessor):
        self._wrapper = wrapper

    def process(self, text: str) -> str:
        return self._wrapper.process(text)

# 4. Конкретні декоратори (Concrete Decorators)
class StripWhitespaceDecorator(TextProcessorDecorator):
    """
    @brief Конкретний декоратор для видалення зайвих порожніх рядків та пробілів.
    """
    def process(self, text: str) -> str:
        base_text = super().process(text)
        
        lines = [line.strip() for line in base_text.splitlines() if line.strip()]
        return "\n".join(lines)

class AutoCorrectDecorator(TextProcessorDecorator):
    """
    @brief Конкретний декоратор для автовиправлення типових помилок OCR.
    """
    def process(self, text: str) -> str:
        base_text = super().process(text)
        
        corrected_text = base_text.replace(" 0 ", " O ")
        corrections = {
            "інформаціяя": "інформація",
            "алгорітм": "алгоритм"
        }
        for wrong, right in corrections.items():
            corrected_text = corrected_text.replace(wrong, right)
            
        return corrected_text