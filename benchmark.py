import csv
import os
import time
import tracemalloc
from collections import deque


# Các bộ dữ liệu cần benchmark
DATA_SIZES = [
    1000,
    5000,
    10000,
    50000,
    100000
]


# =========================================================
# ĐỌC DỮ LIỆU
# =========================================================

def load_data(filename):
    requests = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            request = {
                "request_id": row["request_id"],
                "user_id": row["user_id"],
                "timestamp": int(row["timestamp"]),
                "priority": int(row["priority"])
            }

            requests.append(request)

    return requests


# =========================================================
# FIFO QUEUE
# =========================================================

def run_fifo(requests):

    queue = deque()

    # Đưa request vào hàng đợi
    for request in requests:
        queue.append(request)

    # Xử lý request theo thứ tự đến trước
    while queue:
        queue.popleft()


# =========================================================
# MAX-HEAP
# =========================================================

class MaxHeap:

    def __init__(self):
        self.heap = []

    def push(self, request):

        self.heap.append(request)

        index = len(self.heap) - 1

        while index > 0:

            parent = (index - 1) // 2

            if self.heap[parent]["priority"] >= self.heap[index]["priority"]:
                break

            self.heap[parent], self.heap[index] = \
                self.heap[index], self.heap[parent]

            index = parent

    def pop(self):

        if len(self.heap) == 0:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]

        self.heap[0] = self.heap.pop()

        index = 0

        while True:

            left = 2 * index + 1
            right = 2 * index + 2

            largest = index

            if (
                left < len(self.heap)
                and self.heap[left]["priority"]
                > self.heap[largest]["priority"]
            ):
                largest = left

            if (
                right < len(self.heap)
                and self.heap[right]["priority"]
                > self.heap[largest]["priority"]
            ):
                largest = right

            if largest == index:
                break

            self.heap[index], self.heap[largest] = \
                self.heap[largest], self.heap[index]

            index = largest

        return root


def run_max_heap(requests):

    heap = MaxHeap()

    # Thêm request vào Max-Heap
    for request in requests:
        heap.push(request)

    # Lấy request có độ ưu tiên cao nhất
    while heap.heap:
        heap.pop()


# =========================================================
# ĐO THỜI GIAN + BỘ NHỚ
# =========================================================

def benchmark_algorithm(algorithm, requests):

    # Bắt đầu theo dõi bộ nhớ
    tracemalloc.start()

    # Bắt đầu đo thời gian
    start_time = time.perf_counter()

    # Chạy thuật toán
    algorithm(requests)

    # Kết thúc đo thời gian
    end_time = time.perf_counter()

    # Lấy thông tin bộ nhớ
    current_memory, peak_memory = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    # Đổi sang ms
    time_ms = (end_time - start_time) * 1000

    # Đổi sang MB
    memory_mb = peak_memory / (1024 * 1024)

    return time_ms, memory_mb


# =========================================================
# CHẠY BENCHMARK
# =========================================================

def main():

    # Tạo thư mục results
    os.makedirs("results", exist_ok=True)

    result_file = "results/benchmark_results.csv"

    results = []

    print("=" * 60)
    print("BENCHMARK FIFO QUEUE VS MAX-HEAP")
    print("=" * 60)

    for n in DATA_SIZES:

        filename = f"data/requests_{n}.csv"

        print(f"\nDang benchmark {n:,} request...")
        
        # Đọc dữ liệu
        requests = load_data(filename)

        # -------------------------
        # FIFO
        # -------------------------

        fifo_time, fifo_memory = benchmark_algorithm(
            run_fifo,
            requests
        )

        print(
            f"FIFO     : "
            f"{fifo_time:.4f} ms | "
            f"{fifo_memory:.4f} MB"
        )

        # -------------------------
        # MAX-HEAP
        # -------------------------

        heap_time, heap_memory = benchmark_algorithm(
            run_max_heap,
            requests
        )

        print(
            f"Max-Heap : "
            f"{heap_time:.4f} ms | "
            f"{heap_memory:.4f} MB"
        )

        # Lưu kết quả
        results.append([
            n,
            round(fifo_time, 4),
            round(fifo_memory, 4),
            round(heap_time, 4),
            round(heap_memory, 4)
        ])

    # =====================================================
    # GHI FILE CSV
    # =====================================================

    with open(
        result_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Requests",
            "FIFO_Time_ms",
            "FIFO_Memory_MB",
            "MaxHeap_Time_ms",
            "MaxHeap_Memory_MB"
        ])

        writer.writerows(results)

    print("\n" + "=" * 60)
    print("BENCHMARK HOAN TAT!")
    print(f"Ket qua da luu tai: {result_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()