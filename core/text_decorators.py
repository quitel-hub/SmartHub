from abc import ABC, abstractmethod

# PATTERN 10: DECORATOR

# 1. Базовий інтерфейс (Component)
class TextProcessor(ABC):
    """Інтерфейс для обробки тексту після OCR."""
    @abstractmethod
    def process(self, text: str) -> str:
        pass

# 2. Базовий компонент (Concrete Component)
class BasicTextProcessor(TextProcessor):
    """Початковий компонент, який просто повертає сирий текст."""
    def process(self, text: str) -> str:
        return text

# 3. Базовий клас-декоратор (Base Decorator)
class TextProcessorDecorator(TextProcessor):
    """
    Базовий декоратор. Він зберігає посилання на вкладений компонент
    (яким може бути як BasicTextProcessor, так і інший декоратор).
    """
    def __init__(self, wrapper: TextProcessor):
        self._wrapper = wrapper

    def process(self, text: str) -> str:
        return self._wrapper.process(text)

# 4. Конкретні декоратори (Concrete Decorators)
class StripWhitespaceDecorator(TextProcessorDecorator):
    """Декоратор для видалення зайвих порожніх рядків та пробілів."""
    def process(self, text: str) -> str:
        # Спочатку виконуємо обробку попереднього компонента
        base_text = super().process(text)
        
        # Наша додаткова логіка
        lines = [line.strip() for line in base_text.splitlines() if line.strip()]
        return "\n".join(lines)

class AutoCorrectDecorator(TextProcessorDecorator):
    """Декоратор для виправлення типових помилок OCR."""
    def process(self, text: str) -> str:
        base_text = super().process(text)
        
        # Наприклад, OCR часто плутає цифру 0 і велику О в термінах
        corrected_text = base_text.replace(" 0 ", " O ")
        # Можна додати словник типових помилок
        corrections = {
            "інформаціяя": "інформація",
            "алгорітм": "алгоритм"
        }
        for wrong, right in corrections.items():
            corrected_text = corrected_text.replace(wrong, right)
            
        return corrected_text