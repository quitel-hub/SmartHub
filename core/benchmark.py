import time
import concurrent.futures
import shutil
import os
from core.ocr_engine import OCREngine

class OCRBenchmark:
    def __init__(self, image_path: str, iterations: int = 50):
        self.image_path = image_path
        self.iterations = iterations
        self.ocr = OCREngine()
        self.test_images = []

    def prepare_environment(self):
        """Creates copies of the image to simulate a real workload."""
        print(f"Preparing {self.iterations} images for benchmarking...")
        os.makedirs("temp_bench", exist_ok=True)
        for i in range(self.iterations):
            dest = f"temp_bench/test_img_{i}.jpg"
            shutil.copy(self.image_path, dest)
            self.test_images.append(dest)

    def clean_environment(self):
        """Cleans up temporary files after benchmark."""
        if os.path.exists("temp_bench"):
            shutil.rmtree("temp_bench")

    def run_sequential(self) -> float:
        """Runs OCR processing sequentially (1 thread)."""
        print("\n--- Starting Sequential Benchmark (1 Thread) ---")
        start_time = time.time()
        
        for img in self.test_images:
            self.ocr.extract_text(img)
            
        end_time = time.time()
        return end_time - start_time

    def run_parallel(self, max_workers: int = 4) -> float:
        """Runs OCR processing in parallel using ThreadPoolExecutor."""
        print(f"\n--- Starting Parallel Benchmark ({max_workers} Threads) ---")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.ocr.extract_text, self.test_images)
            
        end_time = time.time()
        return end_time - start_time

    def execute_benchmark(self):
        self.prepare_environment()
        
        seq_time = self.run_sequential()
        print(f"Sequential processing time: {seq_time:.2f} seconds")
        
        par_time = self.run_parallel()
        print(f"Parallel processing time: {par_time:.2f} seconds")
        
        improvement = seq_time / par_time
        print(f"\n✅ Performance Improvement: {improvement:.2f}x faster using parallel threads.")
        
        self.clean_environment()

if __name__ == "__main__":
    test_image = "temp_downloads/AgACAgIAAxkBAAMHacRbtnXjiFz1GW4JDDT4adMuNukAAuEcaxuPvSFKjF82LkLoGEIBAAMCAAN5AAM6BA.jpg" 
    
    if not os.path.exists(test_image):
        print(f"Error: Please place a valid image at {test_image}")
    else:
        benchmark = OCRBenchmark(test_image, iterations=20) 
        benchmark.execute_benchmark()