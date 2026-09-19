---
name: vwr-code-convention
description: Quy chuẩn code bắt buộc cho toàn bộ dự án Virtual Waiting Room. Kích hoạt khi viết, sửa, hoặc review bất kỳ file code nào trong dự án (M1-M7, models.py, main.py).
---

# SKILL: VWR Code Convention — Quy chuẩn Code dự án

## MỤC ĐÍCH
Đảm bảo tất cả code trong dự án tuân thủ 100% các quy chuẩn kỹ thuật đã thống nhất.

---

## 1. QUY TẮC ĐẶT TÊN HÀM (FUNCTION NAMES)

**Bắt buộc:** Tiếng Việt KHÔNG DẤU, `snake_case`.

✅ Đúng:
```python
def chia_de_tri_sap_xep_thoi_gian(users: list[User]) -> list[User]:
def trich_xuat_top_k_uu_tien(users: list[User], k: int) -> list[User]:
def tim_kiem_nhi_phan_nguong_ban_lo(capacity_C: int, tau_0: float, drop_rate_p: float) -> int:
def quy_hoach_dong_phan_bo_ve(m_star: int, demands: dict[str, int], prices: dict[str, float]) -> dict[str, int]:
def xu_ly_xung_dot_tham_lam(checked_in_users: list[User], physical_seats: dict[str, int]) -> tuple[float, list[dict]]:
def cap_nhat_va_lay_ti_le_rot_o1(new_status: int) -> float:
def thu_hoi_ve_het_han(current_time: int) -> list[Ticket]:
def chay_danh_gia_saa(num_scenarios: int = 100, capacity_C: int = 100) -> dict:
```

❌ Sai:
```python
def run_merge_sort()      # Tên tiếng Anh
def xửLýXungĐột()        # Tiếng Việt có dấu
def processData()          # camelCase
```

---

## 2. QUY TẮC ĐẶT TÊN BIẾN (VARIABLE NAMES)

**Bắt buộc:** Tiếng Anh kỹ thuật, ngắn gọn, chuẩn xác theo toán học và nghiệp vụ.

✅ Đúng:
```python
arrival_time    # Thời gian đến
loyalty_score   # Điểm ưu tiên
user_id         # Mã người dùng
M_star          # Hạn mức bán lố tối ưu
capacity_C      # Sức chứa rạp
tau_0           # Ngưỡng chấp nhận rủi ro
drop_rate_p     # Tỷ lệ bùng vé
expire_time     # Thời điểm hết hạn thanh toán
```

❌ Sai:
```python
diem_loyalty     # Tiếng Việt có dấu
thoi_gian_den    # Tiếng Việt
x, y, z          # Quá ngắn, không rõ nghĩa (trừ biến vòng lặp)
```

---

## 3. DATA MODEL BẮT BUỘC (`models.py`)

Toàn bộ pipeline giao tiếp qua 2 dataclass:

```python
from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    arrival_time: int        # Timestamp đến hàng đợi (M1 dùng để sort)
    loyalty_score: int       # Điểm ưu tiên (M2 dùng trong Max-Heap)
    ticket_type: str = ""    # "VIP", "STANDARD", hoặc rỗng
    status: str = "WAITING"  # "WAITING", "BOOKED", "CHECKED_IN", "COMPENSATED", "CANCELLED"

@dataclass
class Ticket:
    ticket_id: int
    ticket_type: str         # "VIP" hoặc "STANDARD"
    price: float             # Giá vé niêm yết
    expire_time: int         # Thời điểm hết hạn thanh toán (M6 dùng trong Min-Heap)
    assigned_user_id: int = -1
```

---

## 4. THƯ VIỆN CẤM SỬ DỤNG

Tuyệt đối không dùng:
- `sort()`, `sorted()` — phải tự viết thuật toán sắp xếp
- `heapq` — phải tự viết heap (sift-up, sift-down)
- `bisect` — phải tự viết binary search
- `scipy` — phải tự viết hàm tính xác suất
- `numpy`, `pandas` — không cần thiết, gây xung đột môi trường

Được phép dùng:
- `dataclasses` (cho models)
- `collections.deque` (cho sliding window queue)
- `random` (cho mock data generator và M7 Monte Carlo)
- `typing` (cho Type Hints)
- `unittest` (cho testing)
- `math` (cho các phép toán cơ bản: `math.log`, `math.factorial` — NHƯNG KHÔNG dùng cho giải thuật lõi)

---

## 5. QUY TẮC COMMENT

- Tối đa **1 dòng** mỗi comment
- Tập trung giải thích **bản chất thao tác giải thuật** hoặc **chỉ số toán học**
- Không viết comment hiển nhiên

✅ Đúng:
```python
# Chia mảng thành hai nửa tại điểm giữa
# Trộn hai nửa đã sắp xếp, giữ thứ tự ổn định
# Tính P(K > C) = 1 - CDF(C) theo Binomial(M, 1-p)
# Sift-down: swap node gốc với con lớn nhất
```

❌ Sai:
```python
# Đây là hàm chính của module
# Gọi hàm merge_sort
# Trả về kết quả
```

---

## 6. TYPE HINTS

Bắt buộc trên **tất cả** tham số và giá trị trả về:

```python
def trich_xuat_top_k_uu_tien(users: list[User], k: int) -> list[User]:
    """Build Max-Heap theo loyalty_score và pop đúng k User.
    Time: O(N + k log N), Space: O(N)."""
```

---

## 7. DOCSTRING

Mỗi public function PHẢI có docstring gồm:
- Mô tả ngắn gọn chức năng
- Phân tích **Time complexity** O(...)
- Phân tích **Space complexity** O(...)

---

## 8. CHECKLIST TRƯỚC KHI COMMIT

- [ ] Tên hàm: Tiếng Việt không dấu `snake_case`?
- [ ] Tên biến: Tiếng Anh kỹ thuật?
- [ ] Type Hints đầy đủ trên tham số và return?
- [ ] Docstring có phân tích complexity?
- [ ] Comment ngắn gọn ≤ 1 dòng?
- [ ] Không dùng thư viện cấm?
- [ ] Thuật toán tự viết 100%?
- [ ] Sử dụng `User` và `Ticket` từ `models.py`?
