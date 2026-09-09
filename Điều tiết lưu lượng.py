import time
from dataclasses import dataclass
from typing import List


# ============================================================
# 1. LỚP LƯU THÔNG TIN REQUEST
# ============================================================

@dataclass
class RequestResult:
    """
    Lưu kết quả xử lý của một request.
    """

    request_id: int
    timestamp: float
    status: str
    value: float
    message: str


# ============================================================
# 2. THUẬT TOÁN LEAKY BUCKET
# ============================================================

class LeakyBucket:
    """
    Thuật toán Leaky Bucket.

    Ý tưởng:
    - Bucket có dung lượng tối đa.
    - Request đi vào bucket.
    - Request được xử lý/rò ra với tốc độ cố định.
    - Nếu bucket còn đủ chỗ -> ACCEPT.
    - Nếu bucket đầy -> REJECT.
    """

    def __init__(self, capacity: float, leak_rate: float):
        """
        capacity:
            Dung lượng tối đa của bucket.

        leak_rate:
            Tốc độ xử lý request mỗi giây.
        """

        if capacity <= 0:
            raise ValueError("Capacity phai lon hon 0.")

        if leak_rate <= 0:
            raise ValueError("Leak rate phai lon hon 0.")

        self.capacity = capacity
        self.leak_rate = leak_rate

        # Số request hiện đang nằm trong bucket
        self.water = 0.0

        # Thời điểm cập nhật cuối cùng
        self.last_time = time.monotonic()

        # Thống kê
        self.accepted_requests = 0
        self.rejected_requests = 0

    # --------------------------------------------------------
    # Cập nhật lượng request đã được xử lý ra khỏi bucket
    # --------------------------------------------------------

    def leak(self):
        """
        Làm giảm lượng request trong bucket dựa trên
        khoảng thời gian đã trôi qua.
        """

        current_time = time.monotonic()

        # Tính thời gian đã trôi qua
        elapsed = current_time - self.last_time

        # Số request được xử lý trong khoảng thời gian đó
        leaked_amount = elapsed * self.leak_rate

        # Không để water âm
        self.water = max(0.0, self.water - leaked_amount)

        # Cập nhật thời gian
        self.last_time = current_time

    # --------------------------------------------------------
    # Xử lý request
    # --------------------------------------------------------

    def allow_request(self, request_size: float = 1.0):
        """
        Kiểm tra request có được chấp nhận hay không.

        Trả về:
            True  -> ACCEPT
            False -> REJECT
        """

        if request_size <= 0:
            raise ValueError("Request size phai lon hon 0.")

        # Cập nhật trạng thái bucket trước
        self.leak()

        # Kiểm tra bucket còn đủ chỗ hay không
        if self.water + request_size <= self.capacity:

            # Đưa request vào bucket
            self.water += request_size

            # Tăng số request được chấp nhận
            self.accepted_requests += 1

            return True

        else:

            # Bucket không đủ chỗ
            self.rejected_requests += 1

            return False

    # --------------------------------------------------------
    # Lấy lượng request hiện tại trong bucket
    # --------------------------------------------------------

    def get_current_load(self):
        """
        Trả về lượng request hiện tại.
        """

        self.leak()

        return self.water

    # --------------------------------------------------------
    # Lấy phần trăm bucket đang sử dụng
    # --------------------------------------------------------

    def get_usage_percent(self):
        """
        Trả về phần trăm dung lượng bucket đang sử dụng.
        """

        current_load = self.get_current_load()

        return (current_load / self.capacity) * 100

    # --------------------------------------------------------
    # Lấy thống kê
    # --------------------------------------------------------

    def get_statistics(self):

        total = (
            self.accepted_requests
            + self.rejected_requests
        )

        if total > 0:
            accepted_percent = (
                self.accepted_requests / total
            ) * 100

            rejected_percent = (
                self.rejected_requests / total
            ) * 100
        else:
            accepted_percent = 0
            rejected_percent = 0

        return {
            "accepted": self.accepted_requests,
            "rejected": self.rejected_requests,
            "total": total,
            "accepted_percent": accepted_percent,
            "rejected_percent": rejected_percent
        }


# ============================================================
# 3. THUẬT TOÁN TOKEN BUCKET
# ============================================================

class TokenBucket:
    """
    Thuật toán Token Bucket.

    Ý tưởng:
    - Bucket chứa token.
    - Token được bổ sung theo refill_rate.
    - Mỗi request cần một số token nhất định.
    - Có đủ token -> ACCEPT.
    - Không đủ token -> REJECT.
    """

    def __init__(self, capacity: float, refill_rate: float):
        """
        capacity:
            Số token tối đa bucket có thể chứa.

        refill_rate:
            Số token được bổ sung mỗi giây.
        """

        if capacity <= 0:
            raise ValueError("Capacity phai lon hon 0.")

        if refill_rate <= 0:
            raise ValueError("Refill rate phai lon hon 0.")

        self.capacity = capacity
        self.refill_rate = refill_rate

        # Ban đầu bucket đầy token
        self.tokens = float(capacity)

        # Thời điểm cập nhật cuối
        self.last_time = time.monotonic()

        # Thống kê
        self.accepted_requests = 0
        self.rejected_requests = 0

    # --------------------------------------------------------
    # Bổ sung token
    # --------------------------------------------------------

    def refill(self):
        """
        Bổ sung token dựa trên thời gian đã trôi qua.
        """

        current_time = time.monotonic()

        # Tính thời gian đã trôi qua
        elapsed = current_time - self.last_time

        # Số token được tạo thêm
        new_tokens = elapsed * self.refill_rate

        # Cộng token
        self.tokens += new_tokens

        # Không cho token vượt quá capacity
        self.tokens = min(
            self.capacity,
            self.tokens
        )

        # Cập nhật thời gian
        self.last_time = current_time

    # --------------------------------------------------------
    # Xử lý request
    # --------------------------------------------------------

    def allow_request(self, request_size: float = 1.0):
        """
        Kiểm tra request có đủ token để xử lý không.

        Trả về:
            True  -> ACCEPT
            False -> REJECT
        """

        if request_size <= 0:
            raise ValueError("Request size phai lon hon 0.")

        # Cập nhật token trước
        self.refill()

        # Kiểm tra số token
        if self.tokens >= request_size:

            # Trừ token
            self.tokens -= request_size

            # Tăng số request được chấp nhận
            self.accepted_requests += 1

            return True

        else:

            # Không đủ token
            self.rejected_requests += 1

            return False

    # --------------------------------------------------------
    # Lấy số token hiện tại
    # --------------------------------------------------------

    def get_current_tokens(self):
        """
        Trả về số token hiện tại.
        """

        self.refill()

        return self.tokens

    # --------------------------------------------------------
    # Lấy phần trăm token đang có
    # --------------------------------------------------------

    def get_usage_percent(self):
        """
        Trả về phần trăm token hiện tại so với capacity.
        """

        current_tokens = self.get_current_tokens()

        return (current_tokens / self.capacity) * 100

    # --------------------------------------------------------
    # Lấy thống kê
    # --------------------------------------------------------

    def get_statistics(self):

        total = (
            self.accepted_requests
            + self.rejected_requests
        )

        if total > 0:
            accepted_percent = (
                self.accepted_requests / total
            ) * 100

            rejected_percent = (
                self.rejected_requests / total
            ) * 100

        else:
            accepted_percent = 0
            rejected_percent = 0

        return {
            "accepted": self.accepted_requests,
            "rejected": self.rejected_requests,
            "total": total,
            "accepted_percent": accepted_percent,
            "rejected_percent": rejected_percent
        }


# ============================================================
# 4. HIỂN THỊ KẾT QUẢ
# ============================================================

def print_result(
    request_id,
    algorithm,
    status,
    value,
    message
):
    """
    In kết quả một request.
    """

    print(
        f"Request {request_id:02d} | "
        f"{algorithm:<15} | "
        f"{status:<7} | "
        f"Giá trị = {value:6.2f} | "
        f"{message}"
    )


# ============================================================
# 5. MÔ PHỎNG LEAKY BUCKET
# ============================================================

def simulate_leaky_bucket():

    print("\n")
    print("=" * 75)
    print("                 MÔ PHỎNG LEAKY BUCKET")
    print("=" * 75)

    # --------------------------------------------------------
    # Cấu hình
    # --------------------------------------------------------

    capacity = 5
    leak_rate = 2

    print(f"Capacity   : {capacity} request")
    print(f"Leak rate  : {leak_rate} request/giây")

    print("-" * 75)

    bucket = LeakyBucket(
        capacity=capacity,
        leak_rate=leak_rate
    )

    results: List[RequestResult] = []

    # --------------------------------------------------------
    # Gửi 15 request
    # --------------------------------------------------------

    for request_id in range(1, 16):

        current_time = time.monotonic()

        accepted = bucket.allow_request()

        if accepted:

            status = "ACCEPT"

            message = (
                "Request được đưa vào bucket"
            )

        else:

            status = "REJECT"

            message = (
                "Bucket đầy, request bị từ chối"
            )

        current_load = bucket.get_current_load()

        print_result(
            request_id,
            "Leaky Bucket",
            status,
            current_load,
            message
        )

        # Lưu kết quả
        results.append(
            RequestResult(
                request_id=request_id,
                timestamp=current_time,
                status=status,
                value=current_load,
                message=message
            )
        )

        # Giả lập request đến liên tục
        time.sleep(0.1)

    # --------------------------------------------------------
    # Thống kê
    # --------------------------------------------------------

    stats = bucket.get_statistics()

    print("-" * 75)
    print("THỐNG KÊ LEAKY BUCKET")

    print(
        f"Tổng request      : {stats['total']}"
    )

    print(
        f"ACCEPT             : {stats['accepted']}"
    )

    print(
        f"REJECT             : {stats['rejected']}"
    )

    print(
        f"Tỷ lệ ACCEPT       : "
        f"{stats['accepted_percent']:.2f}%"
    )

    print(
        f"Tỷ lệ REJECT       : "
        f"{stats['rejected_percent']:.2f}%"
    )

    return results


# ============================================================
# 6. MÔ PHỎNG TOKEN BUCKET
# ============================================================

def simulate_token_bucket():

    print("\n")
    print("=" * 75)
    print("                 MÔ PHỎNG TOKEN BUCKET")
    print("=" * 75)

    # --------------------------------------------------------
    # Cấu hình
    # --------------------------------------------------------

    capacity = 5
    refill_rate = 2

    print(f"Capacity    : {capacity} token")
    print(f"Refill rate : {refill_rate} token/giây")

    print("-" * 75)

    bucket = TokenBucket(
        capacity=capacity,
        refill_rate=refill_rate
    )

    results: List[RequestResult] = []

    # --------------------------------------------------------
    # Gửi 15 request
    # --------------------------------------------------------

    for request_id in range(1, 16):

        current_time = time.monotonic()

        accepted = bucket.allow_request()

        if accepted:

            status = "ACCEPT"

            message = (
                "Đủ token, request được xử lý"
            )

        else:

            status = "REJECT"

            message = (
                "Không đủ token, request bị từ chối"
            )

        current_tokens = bucket.get_current_tokens()

        print_result(
            request_id,
            "Token Bucket",
            status,
            current_tokens,
            message
        )

        # Lưu kết quả
        results.append(
            RequestResult(
                request_id=request_id,
                timestamp=current_time,
                status=status,
                value=current_tokens,
                message=message
            )
        )

        # Giả lập request đến liên tục
        time.sleep(0.1)

    # --------------------------------------------------------
    # Thống kê
    # --------------------------------------------------------

    stats = bucket.get_statistics()

    print("-" * 75)
    print("THỐNG KÊ TOKEN BUCKET")

    print(
        f"Tổng request      : {stats['total']}"
    )

    print(
        f"ACCEPT             : {stats['accepted']}"
    )

    print(
        f"REJECT             : {stats['rejected']}"
    )

    print(
        f"Tỷ lệ ACCEPT       : "
        f"{stats['accepted_percent']:.2f}%"
    )

    print(
        f"Tỷ lệ REJECT       : "
        f"{stats['rejected_percent']:.2f}%"
    )

    return results


# ============================================================
# 7. KIỂM TRA KHẢ NĂNG BURST CỦA TOKEN BUCKET
# ============================================================

def test_burst_traffic():

    print("\n")
    print("=" * 75)
    print("                  KIỂM TRA BURST TRAFFIC")
    print("=" * 75)

    print(
        "Mô phỏng nhiều request đến liên tiếp trong thời gian ngắn."
    )

    print("-" * 75)

    # Bucket có tối đa 5 token
    bucket = TokenBucket(
        capacity=5,
        refill_rate=2
    )

    for request_id in range(1, 11):

        accepted = bucket.allow_request()

        tokens = bucket.get_current_tokens()

        if accepted:
            status = "ACCEPT"
        else:
            status = "REJECT"

        print(
            f"Request {request_id:02d} | "
            f"{status:<7} | "
            f"Token còn lại = {tokens:.2f}"
        )

        # Không sleep -> mô phỏng burst
        time.sleep(0.01)

    print("-" * 75)

    print(
        "Kết luận: Token Bucket có thể xử lý một nhóm "
        "request tăng đột biến nếu bucket đang có đủ token."
    )


# ============================================================
# 8. KIỂM TRA KHẢ NĂNG REFILL
# ============================================================

def test_token_refill():

    print("\n")
    print("=" * 75)
    print("                    KIỂM TRA REFILL")
    print("=" * 75)

    bucket = TokenBucket(
        capacity=5,
        refill_rate=2
    )

    print(
        f"Ban đầu có {bucket.get_current_tokens():.2f} token."
    )

    # Sử dụng hết token
    print("\nSử dụng 5 request:")

    for i in range(1, 6):

        result = bucket.allow_request()

        print(
            f"Request {i}: "
            f"{'ACCEPT' if result else 'REJECT'} | "
            f"Token = {bucket.get_current_tokens():.2f}"
        )

    print("\nSau khi sử dụng token:")

    print(
        f"Token hiện tại = "
        f"{bucket.get_current_tokens():.2f}"
    )

    # Cho bucket nghỉ 2 giây
    print("\nCho bucket nghỉ 2 giây để refill...")

    time.sleep(2)

    print(
        f"Token sau 2 giây = "
        f"{bucket.get_current_tokens():.2f}"
    )

    # Thử request mới
    result = bucket.allow_request()

    print(
        f"Request mới: "
        f"{'ACCEPT' if result else 'REJECT'}"
    )


# ============================================================
# 9. SO SÁNH HAI THUẬT TOÁN
# ============================================================

def compare_algorithms():

    print("\n")
    print("=" * 75)
    print("                SO SÁNH LEAKY BUCKET")
    print("                       VÀ TOKEN BUCKET")
    print("=" * 75)

    print()

    print(
        f"{'Tiêu chí':<25}"
        f"{'Leaky Bucket':<25}"
        f"{'Token Bucket':<25}"
    )

    print("-" * 75)

    print(
        f"{'Cơ chế':<25}"
        f"{'Request chảy ra đều':<25}"
        f"{'Token được bổ sung':<25}"
    )

    print(
        f"{'Tốc độ đầu ra':<25}"
        f"{'Ổn định':<25}"
        f"{'Linh hoạt':<25}"
    )

    print(
        f"{'Burst traffic':<25}"
        f"{'Hạn chế':<25}"
        f"{'Hỗ trợ tốt':<25}"
    )

    print(
        f"{'Khi bucket đầy':<25}"
        f"{'REJECT request':<25}"
        f"{'Không đủ token':<25}"
    )

    print(
        f"{'Ứng dụng':<25}"
        f"{'Làm phẳng lưu lượng':<25}"
        f"{'Rate limiting/API':<25}"
    )

    print("-" * 75)


# ============================================================
# 10. MENU CHƯƠNG TRÌNH
# ============================================================

def show_menu():

    print("\n")
    print("=" * 60)
    print("              TRAFFIC CONTROL SYSTEM")
    print("=" * 60)

    print("1. Chạy mô phỏng Leaky Bucket")
    print("2. Chạy mô phỏng Token Bucket")
    print("3. Kiểm tra Burst Traffic")
    print("4. Kiểm tra Token Refill")
    print("5. So sánh Leaky Bucket và Token Bucket")
    print("6. Chạy toàn bộ chương trình")
    print("0. Thoát")

    print("=" * 60)


# ============================================================
# 11. HÀM MAIN
# ============================================================

def main():

    while True:

        show_menu()

        choice = input(
            "Nhập lựa chọn của bạn: "
        ).strip()

        if choice == "1":

            simulate_leaky_bucket()

        elif choice == "2":

            simulate_token_bucket()

        elif choice == "3":

            test_burst_traffic()

        elif choice == "4":

            test_token_refill()

        elif choice == "5":

            compare_algorithms()

        elif choice == "6":

            print("\nĐANG CHẠY TOÀN BỘ CHƯƠNG TRÌNH...")

            simulate_leaky_bucket()

            simulate_token_bucket()

            test_burst_traffic()

            test_token_refill()

            compare_algorithms()

        elif choice == "0":

            print("\nChương trình kết thúc.")
            break

        else:

            print(
                "\nLựa chọn không hợp lệ!"
                " Vui lòng nhập từ 0 đến 6."
            )


# ============================================================
# 12. CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()