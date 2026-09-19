---
name: vwr-algorithm-contracts
description: Interface contracts và ranh giới trách nhiệm giữa 7 module thuật toán. Kích hoạt khi cần kiểm tra tính tương thích giữa các module, xác minh input/output, hoặc khi tích hợp pipeline.
---

# SKILL: VWR Algorithm Contracts — Interface giữa 7 Module

## MỤC ĐÍCH
Đảm bảo 7 module giao tiếp đúng interface, không xâm phạm ranh giới trách nhiệm của nhau.

---

## 1. INTERFACE CONTRACT CHÍNH THỨC

### M1 → M2: Sắp xếp user theo thời gian đến

```python
# File: thuat_toan_1_merge_sort.py
def chia_de_tri_sap_xep_thoi_gian(users: list[User]) -> list[User]:
    """Sắp xếp mảng User theo arrival_time tăng dần.
    Time: O(N log N), Space: O(N)."""
```

- **Input:** Danh sách `User` thô (chưa sắp xếp)
- **Output:** Danh sách `User` đã sắp xếp theo `arrival_time` tăng dần
- **Ràng buộc:** CHỈ đọc và sắp xếp theo `arrival_time`. KHÔNG can thiệp `loyalty_score`

---

### M2: Trích xuất top-k user ưu tiên

```python
# File: thuat_toan_2_max_heap.py
def trich_xuat_top_k_uu_tien(users: list[User], k: int) -> list[User]:
    """Build Max-Heap theo loyalty_score và pop đúng k User.
    Time: O(N + k log N), Space: O(N)."""
```

- **Input:** Danh sách `User` đã sắp xếp + số lượng k
- **Output:** k User có `loyalty_score` cao nhất
- **Ràng buộc:** KHÔNG tự tính k. k nhận từ M3 hoặc M4. CẤM dùng `heapq`

---

### M6 → M3: Cung cấp tỷ lệ rớt realtime

```python
# File: thuat_toan_6_sliding_window.py
def cap_nhat_va_lay_ti_le_rot_o1(new_status: int) -> float:
    """Cập nhật trạng thái vé vào cửa sổ 100 giao dịch, trả về tỷ lệ rớt O(1)."""

def thu_hoi_ve_het_han(current_time: int) -> list[Ticket]:
    """Thu hồi vé có expire_time < current_time từ Min-Heap.
    Time: O(m log N) với m là số vé hết hạn."""
```

---

### M3 → M4: Chốt quota bán lố M*

```python
# File: thuat_toan_3_binary_search.py
def tim_kiem_nhi_phan_nguong_ban_lo(
    capacity_C: int,
    tau_0: float,
    drop_rate_p: float
) -> int:
    """Tìm M* an toàn bằng Binary Search + Binomial CDF thủ công.
    Time: O(C * log(Max_M)), Space: O(1)."""
```

- **Input:** Sức chứa C, ngưỡng rủi ro τ₀, tỷ lệ bùng p
- **Output:** `int` M_star — số vé tối đa được phép bán
- **Ràng buộc:** Chỉ chốt TỔNG số lượng M*. KHÔNG chia theo loại vé

---

### M4 → M5: Phân bổ vé theo hạng

```python
# File: thuat_toan_4_bounded_knapsack.py
def quy_hoach_dong_phan_bo_ve(
    m_star: int,
    demands: dict[str, int],
    prices: dict[str, float]
) -> dict[str, int]:
    """Phân bổ M* thành số vé VIP và STANDARD.
    Time: O(Types * M* * Demand), Space: O(Types * M*)."""
```

- **Input:** M_star, nhu cầu tối đa từng loại, giá từng loại
- **Output:** `{"VIP": x, "STANDARD": y}` sao cho x + y ≤ M*
- **Ràng buộc:** Nhận M* làm cận trên cố định. KHÔNG tự tính lại M*

---

### M5: Xử lý xung đột check-in

```python
# File: thuat_toan_5_greedy_conflict.py
def xu_ly_xung_dot_tham_lam(
    checked_in_users: list[User],
    physical_seats: dict[str, int]
) -> tuple[float, list[dict]]:
    """Chữa cháy overbooking bằng Greedy.
    Trả về (Doanh thu thực tế, Nhật ký bồi thường/nâng hạng)."""
```

- **Ràng buộc:** Chỉ can thiệp ở khâu Check-in. KHÔNG chỉnh sửa bảng phân bổ trước đó

---

### M7: Điều phối pipeline

```python
# File: thuat_toan_7_saa_benchmark.py
def chay_danh_gia_saa(
    num_scenarios: int = 100,
    capacity_C: int = 100
) -> dict:
    """Mô phỏng N kịch bản, gọi tuần tự M1→M6→M5, so sánh Proposed vs Baseline."""
```

- **Ràng buộc:** Chỉ import và gọi hàm public từ M1-M6. CẤM copy code thuật toán vào file này

---

## 2. BẢNG RANH GIỚI TRÁCH NHIỆM

| Module | CÓ QUYỀN | KHÔNG CÓ QUYỀN |
|:---:|:---|:---|
| M1 | Sắp xếp theo `arrival_time` | Quản lý priority, quyết định quota |
| M2 | Xếp hạng theo `loyalty_score`, trả top-k | Tính M_star, phân bổ loại vé |
| M3 | Chốt tổng M* bằng Binary Search | Quản lý waiting room, chia VIP/Standard |
| M4 | Phân bổ M* thành allocation theo hạng | Tự quyết định lại M*, thay đổi priority |
| M5 | Xử lý conflict bằng Greedy tại check-in | Tính lại DP, tìm nghiệm tối ưu toàn cục |
| M6 | Thu hồi vé timeout, cung cấp p(t) | Xử lý bồi thường, quyết định phân bổ vé |
| M7 | Điều phối pipeline, chạy SAA/Benchmark | Copy thuật toán M1-M6, làm thay M5 |

---

## 3. LUỒNG DỮ LIỆU PIPELINE

```
[1000 User thô] ──► M1: Merge Sort ──► Sorted Users
                                          │
                                          ▼
                    M6: Sliding Window ──► p(t) realtime
                          │                    │
                          │                    ▼
                          │              M3: Binary Search ──► M_star
                          │                    │
                          │                    ▼
                          │              M4: Knapsack DP ──► {VIP: x, STD: y}
                          │                    │
                          ▼                    ▼
                    M2: Max-Heap ◄─────────────┘ (top-k = M_star users)
                          │
                          ▼
                    M6: Min-Heap ──► Hold / Release TTL
                          │
                          ▼
                    M5: Greedy ──► Nâng hạng VIP hoặc Đền bù
                          │
                          ▼
                    M7: SAA ──► Benchmark 100 vòng
```

---

## 4. CHECKLIST TÍCH HỢP

Trước khi tích hợp 2 module, kiểm tra:

- [ ] Tên hàm public khớp chính xác giữa caller và callee?
- [ ] Kiểu dữ liệu input/output nhất quán (dùng `User`/`Ticket`)?
- [ ] Module downstream không truy cập trường dữ liệu ngoài phạm vi?
- [ ] Không có circular dependency?
- [ ] Edge case đã được xử lý ở cả 2 phía (ví dụ: list rỗng)?
