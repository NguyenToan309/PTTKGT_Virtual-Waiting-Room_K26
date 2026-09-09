import time
from dataclasses import dataclass
from collections import deque
from typing import Optional


# ============================================================
# 1. LỚP LƯU THÔNG TIN REQUEST
# ============================================================

@dataclass
class RequestResult:
    """
    Lưu kết quả xử lý của một request.

    Các trạng thái:
    - GRANTED : Request được cấp lượt xử lý.
    - WAITING : Request đang chờ trong hàng đợi.
    - REJECTED: Request bị từ chối.
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
    Thuật toán Leaky Bucket có hàng đợi.

    Nguyên lý:
    - Request đến sẽ được đưa vào hàng đợi nếu bucket còn chỗ.
    - Request trong hàng đợi được xử lý với tốc độ leak_rate
      cố định.
    - Request được xử lý sẽ có trạng thái GRANTED.
    - Request chưa được xử lý sẽ ở trạng thái WAITING.
    - Nếu hàng đợi đầy, request mới sẽ REJECTED.
    """

    def __init__(self, capacity: int, leak_rate: float):
        """
        Parameters
        ----------
        capacity : int
            Số request tối đa có thể chờ trong bucket.

        leak_rate : float
            Số request được xử lý mỗi giây.
        """

        if capacity <= 0:
            raise ValueError(
                "Capacity phải lớn hơn 0."
            )

        if leak_rate <= 0:
            raise ValueError(
                "Leak rate phải lớn hơn 0."
            )

        self.capacity = capacity
        self.leak_rate = leak_rate

        # Hàng đợi lưu ID của các request đang chờ
        self.queue = deque()

        # Thời điểm cập nhật gần nhất
        self.last_time = time.monotonic()

        # Phần thời gian xử lý còn dư
        self.service_credit = 0.0

        # Thống kê
        self.granted_requests = 0
        self.waiting_requests = 0
        self.rejected_requests = 0

    # --------------------------------------------------------
    # Cập nhật và xử lý request trong queue
    # --------------------------------------------------------

    def leak(self):
        """
        Xử lý các request trong hàng đợi theo leak_rate.

        Request được lấy ra khỏi queue theo nguyên tắc FIFO.
        """

        current_time = time.monotonic()

        # Tính thời gian đã trôi qua
        elapsed = current_time - self.last_time

        self.last_time = current_time

        # Tích lũy khả năng xử lý
        self.service_credit += (
            elapsed * self.leak_rate
        )

        granted_ids = []

        # Mỗi 1 đơn vị credit xử lý 1 request
        while (
            self.service_credit >= 1.0
            and self.queue
        ):

            request_id = self.queue.popleft()

            self.service_credit -= 1.0

            self.granted_requests += 1

            granted_ids.append(request_id)

        return granted_ids

    # --------------------------------------------------------
    # Tiếp nhận request
    # --------------------------------------------------------

    def allow_request(self, request_id: int):
        """
        Đưa request vào hệ thống.

        Trả về:
            GRANTED  -> request được xử lý
            WAITING  -> request được đưa vào queue
            REJECTED -> queue đã đầy
        """

        # Trước tiên xử lý các request đã chờ
        granted_ids = self.leak()

        # Kiểm tra queue còn chỗ không
        if len(self.queue) < self.capacity:

            # Đưa request vào queue
            self.queue.append(request_id)

            self.waiting_requests += 1

            return "WAITING", granted_ids

        # Queue đầy
        self.rejected_requests += 1

        return "REJECTED", granted_ids

    # --------------------------------------------------------
    # Lấy số request đang chờ
    # --------------------------------------------------------

    def get_queue_size(self):
        """
        Trả về số request hiện đang chờ.
        """

        return len(self.queue)

    # --------------------------------------------------------
    # Lấy phần trăm sử dụng bucket
    # --------------------------------------------------------

    def get_usage_percent(self):
        """
        Trả về phần trăm dung lượng bucket đang sử dụng.
        """

        if self.capacity == 0:
            return 0.0

        return (
            len(self.queue) / self.capacity
        ) * 100

    # --------------------------------------------------------
    # Lấy thống kê
    # --------------------------------------------------------

    def get_statistics(self):

        total = (
            self.granted_requests
            + self.waiting_requests
            + self.rejected_requests
        )

        if total > 0:

            granted_percent = (
                self.granted_requests / total
            ) * 100

            waiting_percent = (
                self.waiting_requests / total
            ) * 100

            rejected_percent = (
                self.rejected_requests / total
            ) * 100

        else:

            granted_percent = 0.0
            waiting_percent = 0.0
            rejected_percent = 0.0

        return {
            "granted": self.granted_requests,
            "waiting": self.waiting_requests,
            "rejected": self.rejected_requests,
            "total": total,
            "granted_percent": granted_percent,
            "waiting_percent": waiting_percent,
            "rejected_percent": rejected_percent
        }


# ============================================================
# 3. THUẬT TOÁN TOKEN BUCKET
# ============================================================

class TokenBucket:
    """
    Thuật toán Token Bucket.

    Nguyên lý:
    - Bucket chứa một số lượng token.
    - Token được bổ sung theo refill_rate.
    - Mỗi request cần token để được xử lý.
    - Có đủ token -> GRANTED.
    - Không đủ token -> REJECTED.
    """

    def __init__(
        self,
        capacity: float,
        refill_rate: float
    ):
        """
        Parameters
        ----------
        capacity : float
            Số token tối đa.

        refill_rate : float
            Số token được bổ sung mỗi giây.
        """

        if capacity <= 0:
            raise ValueError(
                "Capacity phải lớn hơn 0."
            )

        if refill_rate <= 0:
            raise ValueError(
                "Refill rate phải lớn hơn 0."
            )

        self.capacity = capacity
        self.refill_rate = refill_rate

        # Ban đầu bucket đầy token
        self.tokens = float(capacity)

        # Thời điểm cập nhật gần nhất
        self.last_time = time.monotonic()

        # Thống kê
        self.granted_requests = 0
        self.rejected_requests = 0

    # --------------------------------------------------------
    # Bổ sung token
    # --------------------------------------------------------

    def refill(self):
        """
        Bổ sung token dựa trên thời gian đã trôi qua.
        """

        current_time = time.monotonic()

        elapsed = current_time - self.last_time

        # Tính số token mới
        new_tokens = (
            elapsed * self.refill_rate
        )

        self.tokens += new_tokens

        # Không vượt quá capacity
        self.tokens = min(
            self.capacity,
            self.tokens
        )

        self.last_time = current_time

    # --------------------------------------------------------
    # Xử lý request
    # --------------------------------------------------------

    def allow_request(
        self,
        request_id: int,
        request_size: float = 1.0
    ):
        """
        Kiểm tra request có đủ token không.

        Trả về:
            GRANTED  -> đủ token
            REJECTED -> không đủ token
        """

        if request_size <= 0:
            raise ValueError(
                "Request size phải lớn hơn 0."
            )

        # Cập nhật token
        self.refill()

        # Có đủ token
        if self.tokens >= request_size:

            # Trừ token
            self.tokens -= request_size

            self.granted_requests += 1

            return "GRANTED"

        # Không đủ token
        self.rejected_requests += 1

        return "REJECTED"

    # --------------------------------------------------------
    # Lấy token hiện tại
    # --------------------------------------------------------

    def get_current_tokens(self):
        """
        Trả về số token hiện tại.

        Không gọi refill() ở đây để tránh cập nhật
        thời gian dư thừa.
        """

        return self.tokens

    # --------------------------------------------------------
    # Phần trăm token hiện tại
    # --------------------------------------------------------

    def get_usage_percent(self):

        if self.capacity == 0:
            return 0.0

        return (
            self.tokens / self.capacity
        ) * 100

    # --------------------------------------------------------
    # Thống kê
    # --------------------------------------------------------

    def get_statistics(self):

        total = (
            self.granted_requests
            + self.rejected_requests
        )

        if total > 0:

            granted_percent = (
                self.granted_requests / total
            ) * 100

            rejected_percent = (
                self.rejected_requests / total
            ) * 100

        else:

            granted_percent = 0.0
            rejected_percent = 0.0

        return {
            "granted": self.granted_requests,
            "rejected": self.rejected_requests,
            "total": total,
            "granted_percent": granted_percent,
            "rejected_percent": rejected_percent
        }


# ============================================================
# 4. HÀM HIỂN THỊ KẾT QUẢ
# ============================================================

def print_result(
    request_id,
    algorithm,
    status,
    value,
    message
):
    """
    In kết quả xử lý request.
    """

    print(
        f"Request {request_id:02d} | "
        f"{algorithm:<15} | "
        f"{status:<8} | "
        f"Giá trị = {value:6.2f} | "
        f"{message}"
    )


# ============================================================
# 5. MÔ PHỎNG LEAKY BUCKET
# ============================================================

def simulate_leaky_bucket():

    print("\n")
    print("=" * 85)
    print("                  MÔ PHỎNG LEAKY BUCKET")
    print("=" * 85)

    capacity = 5
    leak_rate = 2

    print(
        f"Capacity  : {capacity} request"
    )

    print(
        f"Leak rate : {leak_rate} request/giây"
    )

    print("-" * 85)

    bucket = LeakyBucket(
        capacity,
        leak_rate
    )

    results = []

    # Gửi 15 request
    for request_id in range(1, 16):

        timestamp = time.monotonic()

        status, granted_ids = (
            bucket.allow_request(request_id)
        )

        # ----------------------------------------------------
        # Hiển thị những request vừa được cấp lượt
        # ----------------------------------------------------

        if granted_ids:

            for granted_id in granted_ids:

                print(
                    f"Request {granted_id:02d} | "
                    f"Leaky Bucket    | "
                    f"GRANTED  | "
                    f"Được cấp lượt xử lý"
                )

        # ----------------------------------------------------
        # Hiển thị trạng thái request hiện tại
        # ----------------------------------------------------

        if status == "WAITING":

            message = (
                "WAITING / IN QUEUE - "
                "Request được đưa vào hàng đợi"
            )

        else:

            message = (
                "REJECTED - "
                "Hàng đợi đã đầy"
            )

        queue_size = bucket.get_queue_size()

        print_result(
            request_id,
            "Leaky Bucket",
            status,
            queue_size,
            message
        )

        results.append(
            RequestResult(
                request_id,
                timestamp,
                status,
                queue_size,
                message
            )
        )

        # Mô phỏng request đến liên tục
        time.sleep(0.1)

    # --------------------------------------------------------
    # Cho hệ thống tiếp tục xử lý queue
    # --------------------------------------------------------

    print("\nĐang xử lý các request còn chờ...")

    time.sleep(1)

    granted_ids = bucket.leak()

    for request_id in granted_ids:

        print(
            f"Request {request_id:02d} | "
            f"Leaky Bucket    | "
            f"GRANTED  | "
            f"Được cấp lượt xử lý"
        )

    # --------------------------------------------------------
    # Thống kê
    # --------------------------------------------------------

    stats = bucket.get_statistics()

    print("\n")
    print("-" * 85)
    print("THỐNG KÊ LEAKY BUCKET")
    print("-" * 85)

    print(
        f"Tổng request       : "
        f"{stats['total']}"
    )

    print(
        f"GRANTED            : "
        f"{stats['granted']}"
    )

    print(
        f"WAITING            : "
        f"{stats['waiting']}"
    )

    print(
        f"REJECTED           : "
        f"{stats['rejected']}"
    )

    print(
        f"Tỷ lệ GRANTED      : "
        f"{stats['granted_percent']:.2f}%"
    )

    print(
        f"Tỷ lệ WAITING      : "
        f"{stats['waiting_percent']:.2f}%"
    )

    print(
        f"Tỷ lệ REJECTED     : "
        f"{stats['rejected_percent']:.2f}%"
    )

    return results


# ============================================================
# 6. MÔ PHỎNG TOKEN BUCKET
# ============================================================

def simulate_token_bucket():

    print("\n")
    print("=" * 85)
    print("                  MÔ PHỎNG TOKEN BUCKET")
    print("=" * 85)

    capacity = 5
    refill_rate = 2

    print(
        f"Capacity    : {capacity} token"
    )

    print(
        f"Refill rate : {refill_rate} token/giây"
    )

    print("-" * 85)

    bucket = TokenBucket(
        capacity,
        refill_rate
    )

    results = []

    for request_id in range(1, 16):

        timestamp = time.monotonic()

        status = bucket.allow_request(
            request_id
        )

        if status == "GRANTED":

            message = (
                "Đủ token - "
                "Request được cấp lượt"
            )

        else:

            message = (
                "Không đủ token - "
                "Request bị từ chối"
            )

        tokens = bucket.get_current_tokens()

        print_result(
            request_id,
            "Token Bucket",
            status,
            tokens,
            message
        )

        results.append(
            RequestResult(
                request_id,
                timestamp,
                status,
                tokens,
                message
            )
        )

        # Request đến liên tục
        time.sleep(0.1)

    # --------------------------------------------------------
    # Thống kê
    # --------------------------------------------------------

    stats = bucket.get_statistics()

    print("\n")
    print("-" * 85)
    print("THỐNG KÊ TOKEN BUCKET")
    print("-" * 85)

    print(
        f"Tổng request       : "
        f"{stats['total']}"
    )

    print(
        f"GRANTED            : "
        f"{stats['granted']}"
    )

    print(
        f"REJECTED           : "
        f"{stats['rejected']}"
    )

    print(
        f"Tỷ lệ GRANTED      : "
        f"{stats['granted_percent']:.2f}%"
    )

    print(
        f"Tỷ lệ REJECTED     : "
        f"{stats['rejected_percent']:.2f}%"
    )

    return results


# ============================================================
# 7. KIỂM TRA BURST TRAFFIC
# ============================================================

def test_burst_traffic():

    print("\n")
    print("=" * 85)
    print("                    KIỂM TRA BURST TRAFFIC")
    print("=" * 85)

    print(
        "Mô phỏng nhiều request đến liên tiếp "
        "trong khoảng thời gian rất ngắn."
    )

    print("-" * 85)

    bucket = TokenBucket(
        capacity=5,
        refill_rate=2
    )

    for request_id in range(1, 11):

        status = bucket.allow_request(
            request_id
        )

        tokens = bucket.get_current_tokens()

        print(
            f"Request {request_id:02d} | "
            f"{status:<8} | "
            f"Token còn lại = {tokens:.2f}"
        )

        # Khoảng cách rất nhỏ để mô phỏng burst
        time.sleep(0.01)

    print("-" * 85)

    print(
        "Kết luận:"
    )

    print(
        "- Token Bucket cho phép xử lý nhiều request "
        "liên tiếp khi bucket đang có đủ token."
    )

    print(
        "- Khi token không còn đủ, request tiếp theo "
        "sẽ bị REJECTED."
    )


# ============================================================
# 8. KIỂM TRA TOKEN REFILL
# ============================================================

def test_token_refill():

    print("\n")
    print("=" * 85)
    print("                    KIỂM TRA TOKEN REFILL")
    print("=" * 85)

    bucket = TokenBucket(
        capacity=5,
        refill_rate=2
    )

    print(
        f"Token ban đầu: "
        f"{bucket.get_current_tokens():.2f}"
    )

    # --------------------------------------------------------
    # Sử dụng 5 token
    # --------------------------------------------------------

    print("\nSử dụng 5 request:")

    for request_id in range(1, 6):

        status = bucket.allow_request(
            request_id
        )

        print(
            f"Request {request_id}: "
            f"{status:<8} | "
            f"Token = "
            f"{bucket.get_current_tokens():.2f}"
        )

    print("\nToken sau khi xử lý:")

    print(
        f"{bucket.get_current_tokens():.2f} token"
    )

    # --------------------------------------------------------
    # Chờ refill
    # --------------------------------------------------------

    print(
        "\nCho bucket nghỉ 2 giây "
        "để token được bổ sung..."
    )

    time.sleep(2)

    # Phải gọi refill một lần để cập nhật trạng thái
    bucket.refill()

    print(
        f"Token sau 2 giây: "
        f"{bucket.get_current_tokens():.2f}"
    )

    # --------------------------------------------------------
    # Request mới
    # --------------------------------------------------------

    status = bucket.allow_request(6)

    print(
        f"Request 06: {status}"
    )


# ============================================================
# 9. SO SÁNH HAI THUẬT TOÁN
# ============================================================

def compare_algorithms():

    print("\n")
    print("=" * 85)
    print("             SO SÁNH LEAKY BUCKET VÀ TOKEN BUCKET")
    print("=" * 85)

    print()

    print(
        f"{'Tiêu chí':<25}"
        f"{'Leaky Bucket':<30}"
        f"{'Token Bucket':<30}"
    )

    print("-" * 85)

    print(
        f"{'Cơ chế':<25}"
        f"{'Hàng đợi FIFO':<30}"
        f"{'Bucket chứa token':<30}"
    )

    print(
        f"{'Xử lý request':<25}"
        f"{'Theo tốc độ cố định':<30}"
        f"{'Dựa trên số token':<30}"
    )

    print(
        f"{'Trạng thái':<25}"
        f"{'GRANTED / WAITING / REJECTED':<30}"
        f"{'GRANTED / REJECTED':<30}"
    )

    print(
        f"{'Burst traffic':<25}"
        f"{'Hạn chế':<30}"
        f"{'Hỗ trợ tốt':<30}"
    )

    print(
        f"{'Khi vượt giới hạn':<25}"
        f"{'REJECTED khi queue đầy':<30}"
        f"{'REJECTED khi hết token':<30}"
    )

    print(
        f"{'Ứng dụng':<25}"
        f"{'Ổn định tốc độ đầu ra':<30}"
        f"{'Rate limiting / API':<30}"
    )

    print("-" * 85)

    # --------------------------------------------------------
    # Độ phức tạp
    # --------------------------------------------------------

    print("\nPHÂN TÍCH ĐỘ PHỨC TẠP")

    print("\nLeaky Bucket:")

    print(
        "  - Time Complexity: "
        "O(1) amortized / request."
    )

    print(
        "    Mỗi request sử dụng phép tính thời gian "
        "và thao tác queue FIFO."
    )

    print(
        "    Trong một lần cập nhật có thể xử lý nhiều "
        "request đang chờ, nhưng mỗi request chỉ được "
        "lấy khỏi queue một lần."
    )

    print(
        "  - Space Complexity: O(n)."
    )

    print(
        "    n là số request tối đa đang chờ trong queue."
    )

    print("\nToken Bucket:")

    print(
        "  - Time Complexity: O(1) / request."
    )

    print(
        "    Chỉ thực hiện phép tính thời gian, "
        "cộng token, trừ token và so sánh."
    )

    print(
        "  - Space Complexity: O(1)."
    )

    print(
        "    Chỉ lưu các biến trạng thái như "
        "tokens, capacity, refill_rate và last_time."
    )


# ============================================================
# 10. HIỂN THỊ MENU
# ============================================================

def show_menu():

    print("\n")
    print("=" * 65)
    print("                 TRAFFIC CONTROL SYSTEM")
    print("=" * 65)

    print("1. Chạy mô phỏng Leaky Bucket")
    print("2. Chạy mô phỏng Token Bucket")
    print("3. Kiểm tra Burst Traffic")
    print("4. Kiểm tra Token Refill")
    print("5. So sánh hai thuật toán")
    print("6. Chạy toàn bộ chương trình")
    print("0. Thoát")

    print("=" * 65)


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

            print(
                "\nĐANG CHẠY TOÀN BỘ CHƯƠNG TRÌNH..."
            )

            simulate_leaky_bucket()

            simulate_token_bucket()

            test_burst_traffic()

            test_token_refill()

            compare_algorithms()

        elif choice == "0":

            print(
                "\nChương trình kết thúc."
            )

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