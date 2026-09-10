"""
Module 5: Xử lý tranh chấp mua ghế (Concurrency Control & Thuật toán PTTKGT)
Môn học: Phân tích và Thiết kế Giải thuật - K26 UTH

TÓM TẮT THUẬT TOÁN ÁP DỤNG:
1. Chia để trị & Khóa nguyên tử: Fine-grained Mutex Lock từng ghế O(1), chống bán trùng.
2. Tham lam (Chương 6): Tìm ghế đơn gần sân khấu nhất O(S).
3. Quy hoạch động / Cửa sổ trượt (Chương 5): Tìm cụm k ghế liền kề nhau O(M).
4. Sắp xếp chống Deadlock (Chương 2): Sắp xếp mã ghế O(k log k) trước khi Lock.
"""

import threading
import time
import math
import random
from typing import Dict, List, Optional, Tuple


class Seat:
    """Đối tượng ghế và Khóa độc lập (Fine-grained Lock)"""
    def __init__(self, seat_id: str, row: str, col: int, seat_type: str = "VIP"):
        self.seat_id = seat_id
        self.row = row
        self.col = col
        self.seat_type = seat_type
        self.status = "AVAILABLE"  # AVAILABLE -> SOLD
        self.owner: Optional[str] = None
        self.lock = threading.Lock()  # Khóa riêng từng ghế (O(1))


class SmartSeatBookingManager:
    def __init__(self, rows: List[str], cols_per_row: int = 10):
        self.rows = rows
        self.cols_per_row = cols_per_row
        self.seats: Dict[str, Seat] = {}
        self.stats_lock = threading.Lock()
        self.successful_bookings: List[Tuple[str, str, float]] = []

        # Khởi tạo sơ đồ rạp
        for r in rows:
            for c in range(1, cols_per_row + 1):
                s_id = f"{r}_{c:02d}"
                s_type = "VIP" if r in ["A", "B"] else "STANDARD"
                self.seats[s_id] = Seat(seat_id=s_id, row=r, col=c, seat_type=s_type)

    # --------------------------------------------------------------------------
    # 1. THAM LAM (CHƯƠNG 6): Tìm ghế trống gần tâm sân khấu nhất - O(S)
    # --------------------------------------------------------------------------
    def greedy_find_best_seat(self, preferred_type: str = "VIP") -> Optional[str]:
        center_col = (self.cols_per_row + 1) / 2.0
        best_seat_id, min_dist = None, float('inf')

        for seat_id, seat in self.seats.items():
            if seat.seat_type == preferred_type and seat.status == "AVAILABLE":
                row_dist = ord(seat.row) - ord('A') + 1
                col_dist = seat.col - center_col
                dist = math.sqrt(row_dist**2 + col_dist**2)

                # Chọn tối ưu cục bộ
                if dist < min_dist:
                    min_dist, best_seat_id = dist, seat_id

        return best_seat_id

    # --------------------------------------------------------------------------
    # 2. QUY HOẠCH ĐỘNG / CỬA SỔ TRƯỢT (CHƯƠNG 5): Tìm cụm k ghế liền kề - O(M)
    # --------------------------------------------------------------------------
    def find_contiguous_seats(self, row: str, k: int) -> Optional[List[str]]:
        row_seats = [self.seats[f"{row}_{c:02d}"] for c in range(1, self.cols_per_row + 1)]
        center_col = (self.cols_per_row + 1) / 2.0
        best_window, min_offset = None, float('inf')

        for start in range(len(row_seats) - k + 1):
            window = row_seats[start : start + k]
            # Điều kiện: Cả k ghế đều đang trống
            if all(s.status == "AVAILABLE" for s in window):
                avg_col = sum(s.col for s in window) / k
                offset = abs(avg_col - center_col)
                if offset < min_offset:
                    min_offset, best_window = offset, [s.seat_id for s in window]

        return best_window

    # --------------------------------------------------------------------------
    # 3. ĐẶT 1 GHẾ (CONCURRENCY LOCK & ATOMIC CHECK-AND-SET) - O(1)
    # --------------------------------------------------------------------------
    def book_single_seat(self, user_id: str, seat_id: str) -> bool:
        if seat_id not in self.seats:
            return False

        seat = self.seats[seat_id]
        # Vùng khóa kiểm tra và cập nhật nguyên tử (Critical Section)
        with seat.lock:
            if seat.status == "AVAILABLE":
                time.sleep(0.001)  # Giả lập độ trễ I/O
                seat.owner = user_id
                seat.status = "SOLD"
                with self.stats_lock:
                    self.successful_bookings.append((user_id, seat_id, time.time()))
                return True
            return False

    # --------------------------------------------------------------------------
    # 4. SẮP XẾP CHỐNG DEADLOCK (CHƯƠNG 2): Mua đồng thời cụm k ghế - O(k log k)
    # --------------------------------------------------------------------------
    def book_multiple_seats(self, user_id: str, seat_ids: List[str]) -> bool:
        # Sắp xếp thứ tự ghế để phá vỡ chu trình chờ (Tránh Deadlock)
        sorted_ids = sorted(seat_ids)
        locks = [self.seats[s_id].lock for s_id in sorted_ids if s_id in self.seats]

        # Khóa tuần tự
        for lock in locks:
            lock.acquire()

        try:
            # Kiểm tra nguyên tử cả cụm ghế
            if all(self.seats[s_id].status == "AVAILABLE" for s_id in sorted_ids):
                for s_id in sorted_ids:
                    self.seats[s_id].owner = user_id
                    self.seats[s_id].status = "SOLD"
                    with self.stats_lock:
                        self.successful_bookings.append((user_id, s_id, time.time()))
                return True
            return False
        finally:
            # Nhả khóa ngược lại
            for lock in reversed(locks):
                lock.release()


# ==============================================================================
# BỘ TEST & MÔ PHỎNG TRANH CHẤP ĐA LUỒNG
# ==============================================================================
if __name__ == "__main__":
    manager = SmartSeatBookingManager(rows=["A", "B", "C"], cols_per_row=10)

    print("--- 1. TEST THUẬT TOÁN THAM LAM (CHỌN GHẾ TỐI ƯU NHẤT) ---")
    best_seat = manager.greedy_find_best_seat(preferred_type="VIP")
    print(f"✅ Gợi ý ghế VIP tốt nhất: {best_seat}")
    manager.book_single_seat("User_VIP_1", best_seat)

    print("\n--- 2. TEST QUY HOẠCH ĐỘNG (TÌM CỤM 3 GHẾ LIỀN KỀ) ---")
    group_seats = manager.find_contiguous_seats(row="B", k=3)
    print(f"✅ Cụm 3 ghế liền kề tối ưu: {group_seats}")
    if group_seats:
        manager.book_multiple_seats("Group_A", group_seats)

    print("\n--- 3. TEST TRANH CHẤP ĐA LUỒNG (10 LUỒNG MUA 1 GHẾ 'A_01') ---")
    threads = []
    target = "A_01"

    def buy(idx):
        time.sleep(random.uniform(0.001, 0.003))
        res = manager.book_single_seat(f"User_{idx:02d}", target)
        status = "THÀNH CÔNG ✅" if res else "THẤT BẠI (Ghế đã bán) ❌"
        print(f"Luồng {idx:02d} mua {target} -> {status}")

    for i in range(1, 11):
        t = threading.Thread(target=buy, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_bought = len([x for x in manager.successful_bookings if x[1] == target])
    print(f"\n📊 KẾT QUẢ: Duy nhất {total_bought} người mua được ghế '{target}'. Không bán trùng ghế!")
