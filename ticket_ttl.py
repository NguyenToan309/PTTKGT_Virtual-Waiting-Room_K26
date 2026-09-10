import heapq
import time

class HoldManager:
    def __init__(self, ttl_seconds=300):
        self.ttl_seconds = ttl_seconds
        self.min_heap = []  # Lưu tuple: (expiration_time, seat_id, user_id)
        self.active_holds = {}  # Lưu seat_id -> expiration_time để tra cứu nhanh

    def hold_seat(self, user_id, seat_id):
        """Thêm lượt giữ ghế (TTL 300s) - Độ phức tạp O(log h)"""
        current_time = time.time()
        expiration_time = current_time + self.ttl_seconds
        
        heapq.heappush(self.min_heap, (expiration_time, seat_id, user_id))
        self.active_holds[seat_id] = expiration_time
        
        print(f"✅ [HOLD] Seat '{seat_id}' held for {user_id}. Expire at: {time.strftime('%H:%M:%S', time.localtime(expiration_time))}")

    def cleanup_expired_holds(self):
        """Tự động tìm và giải phóng các ghế hết hạn - Độ phức tạp O(log h)"""
        current_time = time.time()
        released_seats = []

        while self.min_heap and self.min_heap[0][0] <= current_time:
            exp_time, seat_id, user_id = heapq.heappop(self.min_heap)
            
            if seat_id in self.active_holds and self.active_holds[seat_id] == exp_time:
                del self.active_holds[seat_id]
                released_seats.append((seat_id, user_id))
                print(f"⏰ [EXPIRED] Seat '{seat_id}' held by {user_id} HAS EXPIRED! Automatically released back to pool.")

        return released_seats

    def manual_release(self, seat_id):
        """Hủy giữ ghế chủ động khi người dùng hủy bỏ"""
        if seat_id in self.active_holds:
            del self.active_holds[seat_id]
            print(f"🔄 [CANCEL] Hold for Seat '{seat_id}' manually cancelled.")


if __name__ == "__main__":
    manager = HoldManager(ttl_seconds=5)

    print("--- 1. NGƯỜI DÙNG GIỮ GHẾ ---")
    manager.hold_seat("User_A", "Seat_VIP_01")
    manager.hold_seat("User_B", "Seat_VIP_02")

    print("\n--- 2. KIỂM TRA TỰ ĐỘNG THU HỒI SAU 6 GIÂY ---")
    time.sleep(6)
    manager.cleanup_expired_holds()
