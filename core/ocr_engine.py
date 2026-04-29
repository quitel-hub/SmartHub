import cv2
import pytesseract
import numpy as np
import os
from abc import ABC, abstractmethod

class OCRStrategy(ABC):
    """
    @brief Абстрактний базовий клас для алгоритмів розпізнавання тексту.
    
    Реалізує патерн Strategy. Дозволяє динамічно змінювати алгоритми 
    розпізнавання (наприклад, звичайний текст, математичні формули тощо) 
    без зміни основного коду рушія.
    """
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """
        @brief Абстрактний метод витягування тексту.
        
        @param image_path Шлях до файлу зображення.
        @return Розпізнаний текст у вигляді рядка.
        """
        pass

class StandardOCRStrategy(OCRStrategy):
    """
    @brief Стандартна стратегія OCR з використанням OpenCV препроцесингу.
    
    Використовує конвертацію в градації сірого та метод Otsu's thresholding 
    для покращення контрастності перед передачею в Tesseract.
    """
    def _preprocess_image(self, image_path: str):
        """
        @brief Підготовлює зображення для кращого OCR розпізнавання.
        
        @param image_path Шлях до файлу зображення.
        @return Оброблене зображення (numpy.ndarray) або None, якщо файл не знайдено.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        return processed_img

    def extract_text(self, image_path: str) -> str:
        """
        @brief Витягує текст використовуючи оптимізовані налаштування Tesseract.
        
        @param image_path Шлях до файлу зображення.
        @return Розпізнаний текст або повідомлення про помилку.
        """
        try:
            processed_img = self._preprocess_image(image_path)
            
            if processed_img is None:
                return "Error: Could not process image file."

            # Оптимізовані налаштування: OEM 3 (Default), PSM 3 (Fully automatic page segmentation)
            custom_config = r'--oem 3 --psm 3'
            
            text = pytesseract.image_to_string(
                processed_img, 
                lang='ukr+eng', 
                config=custom_config
            )
            
            return text.strip()
        except Exception as e:
            return f"OCR Engine Error: {str(e)}"


class OCREngine:
    """
    @brief Головний рушій оптичного розпізнавання символів.
    
    Виступає як "Контекст" у патерні Strategy та "Фасад" (Facade) для 
    взаємодії бота з Tesseract. 
    """
    def __init__(self, strategy: OCRStrategy = None):
        """
        @brief Ініціалізує OCREngine із вказаною стратегією та шляхом до Tesseract.
        
        @param strategy Об'єкт стратегії розпізнавання. Якщо не вказано, 
                        використовується StandardOCRStrategy за замовчуванням.
        """
        # Твій конкретний шлях до Tesseract
        self.tesseract_cmd = r'F:\Projects\tesseract\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        # Встановлюємо стратегію за замовчуванням
        self._strategy = strategy if strategy else StandardOCRStrategy()

    def set_strategy(self, strategy: OCRStrategy):
        """
        @brief Динамічно змінює стратегію розпізнавання під час виконання.
        
        @param strategy Нова стратегія, що наслідує OCRStrategy.
        """
        self._strategy = strategy

    def extract_text(self, image_path: str) -> str:
        """
        @brief Делегує завдання розпізнавання поточній стратегії.
        
        @param image_path Шлях до зображення для розпізнавання.
        @return Результат розпізнавання тексту.
        """
        return self._strategy.extract_text(image_path)