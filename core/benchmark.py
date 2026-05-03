import time
import concurrent.futures
import shutil
import os
from core.ocr_engine import OCREngine

class OCRBenchmark:
    """
    @brief Клас для тестування продуктивності алгоритмів OCR.
    
    Використовується для порівняння послідовної (однопоточної) 
    та паралельної (мультипоточної) версій обробки зображень.
    Відповідає вимогам лабораторної роботи щодо вимірювання часу виконання.
    """
    def __init__(self, image_path: str, iterations: int = 50):
        """
        @brief Ініціалізує бенчмарк.
        
        @param image_path Шлях до тестового зображення.
        @param iterations Кількість ітерацій (копій зображення) для обробки.
        """
        self.image_path = image_path
        self.iterations = iterations
        self.ocr = OCREngine()
        self.test_images = []

    def prepare_environment(self):
        """
        @brief Створює копії тестового зображення для симуляції реального навантаження.
        """
        print(f"Preparing {self.iterations} images for benchmarking...")
        os.makedirs("temp_bench", exist_ok=True)
        for i in range(self.iterations):
            dest = f"temp_bench/test_img_{i}.jpg"
            shutil.copy(self.image_path, dest)
            self.test_images.append(dest)

    def clean_environment(self):
        """
        @brief Очищає тимчасові файли після завершення бенчмарку.
        """
        if os.path.exists("temp_bench"):
            shutil.rmtree("temp_bench")

    def run_sequential(self) -> float:
        """
        @brief Виконує послідовне (не паралельне) розпізнавання тексту.
        
        @return Час виконання в секундах.
        """
        print("\n--- Starting Sequential Benchmark (1 Thread) ---")
        start_time = time.time()
        
        for img in self.test_images:
            self.ocr.extract_text(img)
            
        end_time = time.time()
        return end_time - start_time

    def run_parallel(self, max_workers: int = 4) -> float:
        """
        @brief Виконує розпізнавання тексту паралельно з використанням ThreadPoolExecutor.
        
        @param max_workers Кількість потоків.
        @return Час виконання в секундах.
        """
        print(f"\n--- Starting Parallel Benchmark ({max_workers} Threads) ---")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.ocr.extract_text, self.test_images)
            
        end_time = time.time()
        return end_time - start_time

    def execute_benchmark(self):
        """
        @brief Запускає повний цикл тестування та виводить порівняльні результати.
        """
        self.prepare_environment()
        
        seq_time = self.run_sequential()
        print(f"Sequential processing time: {seq_time:.2f} seconds")
        
        par_time = self.run_parallel()
        print(f"Parallel processing time: {par_time:.2f} seconds")
        
        improvement = seq_time / par_time
        print(f"\n✅ Performance Improvement: {improvement:.2f}x faster using parallel threads.")
        
        self.clean_environment()

if __name__ == "__main__":
    test_image = "temp_downloads/test.jpg" 
    
    if not os.path.exists(test_image):
        print(f"Error: Please place a valid image at {test_image}")
    else:
        benchmark = OCRBenchmark(test_image, iterations=20) 
        benchmark.execute_benchmark()