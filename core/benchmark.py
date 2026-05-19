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
        print("\nStarting Sequential Benchmark (1 Thread)")
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

    def execute_benchmark(self, workers_count: int = 4):
        """
        @brief Головна універсальна функція для запуску повного циклу замірів.
        """
        if not os.path.exists(self.image_path):
            print(f"❌ Помилка: Базове фото не знайдено за шляхом {self.image_path}")
            print("Будь ласка, перевірте шлях до файлу")
            return

        self.prepare_environment()
        
        seq_time = self.run_sequential()
        print(f"⏱ Час виконання в 1 потік: {seq_time:.2f} сек")
        
        print("-" * 45)
    
        par_time = self.run_parallel(max_workers=workers_count)
        print(f"⏱ Час виконання в {workers_count} потоків: {par_time:.2f}  сек")
        
        print("-" * 45)
        
        improvement = seq_time / par_time
        print(f"📊 Метрика ефективності:")
        print(f"🚀 Обробка паралельними потоками виявилася в {improvement:.2f}x разів швидшою")
        
        self.clean_environment()

if __name__ == "__main__":
    BASE_IMAGE = r"F:\Projects\SmartHub2\SmartHub\src\test.jpg" 
    
    NUMBER_OF_PHOTOS = 100
    THREADS = 4

    benchmark = OCRBenchmark(image_path=BASE_IMAGE, iterations=NUMBER_OF_PHOTOS)
    benchmark.execute_benchmark(workers_count=THREADS)