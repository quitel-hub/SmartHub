import cv2
import pytesseract
import numpy as np
import os

class OCREngine:
    def __init__(self):
        self.tesseract_cmd = r'F:\Projects\tesseract\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def _preprocess_image(self, image_path: str):
        """Prepares the image for better OCR recognition"""
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        return processed_img

    def extract_text(self, image_path: str) -> str:
        """Extracts text using optimized settings"""
        try:
            processed_img = self._preprocess_image(image_path)
            
            if processed_img is None:
                return "Error: Could not process image file."

            custom_config = r'--oem 3 --psm 3'
            
            
            text = pytesseract.image_to_string(
                processed_img, 
                lang='ukr+eng', 
                config=custom_config
            )
            
            return text.strip()
        except Exception as e:
            return f"OCR Engine Error: {str(e)}"