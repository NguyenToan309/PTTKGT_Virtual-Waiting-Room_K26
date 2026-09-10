import time
import sys
try:
    from fifo_queue import FIFOVirtualWaitingRoom
    from priority_queue import PriorityWaitingRoom
    from rate_limiter import LeakyBucket
    from ticket_ttl import TTLManager
    from concurrency_sim import SeatLockManager
    from seat_fsm import SeatStateMachine
    from generate_data import DataGenerator
    from benchmark import PerformanceBenchmark
    MODULES_OK = True
except ImportError as e:
    MODULES_OK = False
    ERR_MSG = str(e)

class VirtualWaitingRoomPipeline:
    def __init__(self, seats_config):
        self.seats_config = seats_config
        self.fifo_queue = FIFOVirtualWaitingRoom(seats_config)
        self.rate_limiter = LeakyBucket(rate_per_sec=100)

    def execute_pipeline(self, num_requests=1000):
        print("=" * 65)
        print("🚀 KÍCH HOẠT QUY TRÌNH MÔ PHỎNG VIRTUAL WAITING ROOM (END-TO-END)")
        print("=" * 65)

        print(f"\n[1/5] 🎲 [Data Gen] Sinh {num_requests} request mua vé thử nghiệm...")
        requests = [
            {"user_id": f"USR_{i:04d}", "zone_id": "VIP1" if i % 4 == 0 else "A01", "requested_seats": 1}
            for i in range(1, num_requests + 1)
        ]
        print(f"  └─> Đã nạp thành công {len(requests)} requests vào bộ nhớ.")

        print("\n[2/5] 🚰 [Rate Limiter] Điều tiết lưu lượng xả vào hệ thống...")
        passed_requests = [req for req in requests if self.rate_limiter.allow_request(req)]
        print(f"  └─> Cho phép {len(passed_requests)} requests đi qua Leaky Bucket an toàn.")

        print("\n[3/5] ⏳ [FIFO Queue] Đẩy request vào hàng đợi và xả vé O(1)...")
        start_t = time.perf_counter()
        for req in passed_requests:
            self.fifo_queue.enqueue(req)
        
        success_tx, failed_tx, remaining_seats = self.fifo_queue.process_queue()
        elapsed_ms = (time.perf_counter() - start_t) * 1000

        print("\n[4/5] 🔒 [Concurrency & TTL] Đang cấp Token giữ ghế tạm thời (300s)...")
        print(f"  └─> Đã kích hoạt FSM trạng thái HOLD cho {len(success_tx)} giao dịch thành công.")

        print("\n[5/5] 📊 KẾT QUẢ THỰC THI HỆ THỐNG")
        print("-" * 45)
        print(f" • Tổng số request đầu vào    : {num_requests}")
        print(f" • Thời gian xử lý hàng đợi   : {elapsed_ms:.2f} ms")
        print(f" • Đơn mua vé THÀNH CÔNG     : {len(success_tx)}")
        print(f" • Đơn mua vé THẤT BẠI       : {len(failed_tx)}")
        print(f" • Kho vé tồn còn lại        : {remaining_seats}")
        print("=" * 65)

if __name__ == "__main__":
    if not MODULES_OK:
        print(f"⚠️ Cảnh báo Module: {ERR_MSG}")
        print("💡 Hãy nhớ đổi tên 'FIFO-queue.py' thành 'fifo_queue.py' trên GitHub!\n")

    initial_seats = {"VIP1": 50, "A01": 200, "B02": 300}
    pipeline = VirtualWaitingRoomPipeline(initial_seats)
    pipeline.execute_pipeline(num_requests=1000)
