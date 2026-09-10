
import time
import heapq
from collections import deque

class MaxHeapPriorityQueueWithAging:
    def __init__(self, aging_rate=0.5):
        self._heap = []  # Max-Heap lưu dưới dạng min-heap với giá trị âm (-score)
        self.aging_rate = aging_rate

    def _get_effective_score(self, base_priority, arrival_time):
        """Tính điểm ưu tiên thực tế (Cơ chế Aging chống đói tài nguyên)"""
        waiting_time = time.time() - arrival_time
        return base_priority + (waiting_time * self.aging_rate)

    def enqueue(self, request_id, base_priority):
        """Thêm request vào hàng đợi ưu tiên. Độ phức tạp: O(log n)"""
        arrival_time = time.time()
        score = self._get_effective_score(base_priority, arrival_time)
        # Đảo dấu score (-score) để heapq (min-heap) biến thành Max-Heap
        element = (-score, arrival_time, request_id, base_priority)
        heapq.heappush(self._heap, element)

    def dequeue(self):
        """Lấy request có độ ưu tiên cao nhất ra khỏi hàng đợi. Độ phức tạp: O(log n)"""
        if not self._heap:
            return None
        
        # Cập nhật lại điểm Aging cho toàn bộ heap trước khi lấy ra
        self._recalculate_heap()
        _, arrival_time, request_id, base_pri = heapq.heappop(self._heap)
        return request_id

    def _recalculate_heap(self):
        """Cập nhật lại điểm số các phần tử theo thời gian chờ thực tế"""
        temp = []
        while self._heap:
            _, arrival_time, req_id, base_pri = heapq.heappop(self._heap)
            new_score = self._get_effective_score(base_pri, arrival_time)
            temp.append((-new_score, arrival_time, req_id, base_pri))
        self._heap = temp
        heapq.heapify(self._heap)


# ==========================================
# BỘ TEST & SO SÁNH THỨ TỰ PHỤC VỤ VỚI FIFO
# ==========================================
if __name__ == "__main__":
    requests_data = [
        ("Req_Thường_1", 1),
        ("Req_Thường_2", 1),
        ("Req_VIP_1", 10),
        ("Req_Thường_3", 1)
    ]

    print("--- 1. MÔ HÌNH FIFO (First In, First Out) ---")
    fifo = deque([req[0] for req in requests_data])
    while fifo:
        print(f"Phục vụ: {fifo.popleft()}")

    print("\n--- 2. MÔ HÌNH HÀNG ĐỢI ƯU TIÊN (Max-Heap + Aging) ---")
    pq = MaxHeapPriorityQueueWithAging(aging_rate=1.0)
    for req_id, pri in requests_data:
        pq.enqueue(req_id, pri)
        time.sleep(0.05) # Giả lập khoảng cách thời gian đến

    while pq._heap:
        print(f"Phục vụ: {pq.dequeue()}")
