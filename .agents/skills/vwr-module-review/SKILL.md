---
name: vwr-module-review
description: Checklist kiểm tra Definition of Done cho từng module thuật toán M1-M7. Kích hoạt khi review code, kiểm tra trước bàn giao, hoặc khi thành viên báo hoàn thành module.
---

# SKILL: VWR Module Review — Kiểm tra Definition of Done

## MỤC ĐÍCH
Cung cấp quy trình kiểm tra từng module theo 5 tiêu chuẩn hoàn thành (DoD) bắt buộc.

---

## 1. DEFINITION OF DONE CHUNG (5 ĐIỀU KIỆN)

Mỗi file thuật toán chỉ được xem là hoàn thành khi đáp ứng **đủ 5 điều kiện**:

1. ✅ **Thuật toán tự viết 100%** bằng logic cơ sở — không dùng thư viện built-in (`sort()`, `sorted()`, `heapq`, `bisect`, `scipy`)
2. ✅ **Type Hints đầy đủ** ở tất cả tham số và giá trị trả về (`->`)
3. ✅ **Đã kiểm thử độc lập** với ít nhất 1 test case thông thường và 1 edge case
4. ✅ **Khớp chính xác** tên hàm, tên tham số và kiểu dữ liệu quy định trong Interface
5. ✅ **Có phân tích complexity** O(Time) và O(Space) trong docstring

---

## 2. QUY TRÌNH REVIEW TỪNG MODULE

### Bước 1: Kiểm tra thư viện cấm

```bash
# Tìm import cấm trong tất cả file thuật toán
grep -n "import heapq\|import bisect\|from scipy\|import numpy\|import pandas" thuat_toan_*.py
```

Trong code, kiểm tra:
```bash
# Tìm hàm built-in cấm
grep -n "\.sort(\|sorted(\|heapq\.\|bisect\." thuat_toan_*.py
```

### Bước 2: Kiểm tra Type Hints

Mỗi public function PHẢI có annotation đầy đủ:
```python
# ✅ Đạt
def chia_de_tri_sap_xep_thoi_gian(users: list[User]) -> list[User]:

# ❌ Không đạt
def chia_de_tri_sap_xep_thoi_gian(users):
```

### Bước 3: Kiểm tra test coverage

Mỗi module phải có file test riêng biệt:
- `test_thuat_toan_1_merge_sort.py`
- `test_thuat_toan_2_max_heap.py`
- `test_thuat_toan_3_binary_search.py`
- `test_thuat_toan_4_bounded_knapsack.py`
- `test_thuat_toan_5_greedy_conflict.py`
- `test_thuat_toan_6_sliding_window.py`
- `test_thuat_toan_7_saa_benchmark.py`

Mỗi file test phải có tối thiểu:
- 1 test case **normal** (input hợp lệ, kết quả đúng)
- 1 test case **edge** (input rỗng, giá trị biên, tất cả trùng nhau)

### Bước 4: Kiểm tra interface khớp đặc tả

So sánh chữ ký hàm public trong code với đặc tả contract.

### Bước 5: Kiểm tra docstring complexity

```python
# ✅ Đạt
def chia_de_tri_sap_xep_thoi_gian(users: list[User]) -> list[User]:
    """Sắp xếp mảng User theo arrival_time tăng dần.
    Time: O(N log N), Space: O(N)."""

# ❌ Không đạt — thiếu complexity
def chia_de_tri_sap_xep_thoi_gian(users: list[User]) -> list[User]:
    """Sắp xếp user."""
```

---

## 3. CHECKLIST RIÊNG CHO TỪNG MODULE

### M1 — Merge Sort
- [ ] Thuật toán Merge Sort đệ quy, không dùng `sort()`/`sorted()`
- [ ] Sắp xếp theo `arrival_time` tăng dần (stable sort)
- [ ] Xử lý: list rỗng, 1 phần tử, tất cả trùng `arrival_time`
- [ ] Input/Output dùng `list[User]`
- [ ] Docstring có O(N log N) time, O(N) space

### M2 — Max-Heap
- [ ] Cấu trúc Max-Heap mảng 1D tự viết (index cha `(i-1)//2`, con `2i+1`, `2i+2`)
- [ ] Có `sift_up` và `sift_down` đúng logic
- [ ] So sánh theo `loyalty_score`, tie-break bằng `arrival_time`
- [ ] Không dùng `heapq`
- [ ] Hàm public: `trich_xuat_top_k_uu_tien(users, k)` → `list[User]`

### M3 — Binary Search + Binomial CDF
- [ ] Binary Search trên answer space [C, 3C] tìm M* lớn nhất
- [ ] Hàm tính Binomial CDF viết **bằng tay** (vòng lặp tổ hợp)
- [ ] **KHÔNG dùng `scipy`**
- [ ] Xử lý: p=0, p=1, tau_0=0, tau_0=1
- [ ] Hàm public: `tim_kiem_nhi_phan_nguong_ban_lo(capacity_C, tau_0, drop_rate_p)` → `int`

### M4 — Bounded Knapsack DP
- [ ] Bảng DP 2D `dp[types+1][m_star+1]`
- [ ] Bảng Trace để truy vết nghiệm
- [ ] Tổng allocation ≤ M*
- [ ] Mỗi hạng ≤ demand_limit
- [ ] Type Hints đầy đủ trên public function

### M5 — Greedy Conflict
- [ ] Greedy: Ưu tiên cấp đúng hạng → Nâng hạng VIP → Bồi thường
- [ ] Kiểm soát cứng: tổng vé cấp ≤ C (sức chứa vật lý)
- [ ] Gán status: "Success", "Upgraded", "Rejected", "Compensated"
- [ ] Trả về `(doanh_thu_thuc_te, nhat_ky_xu_ly)`

### M6 — Sliding Window + Min-Heap
- [ ] Sliding Window O(1): biến đếm tích lũy, KHÔNG dùng `sum()` mỗi lần hỏi
- [ ] Min-Heap tự viết: `sift_up`, `sift_down` theo `expire_time`
- [ ] **KHÔNG dùng `.sort()` hay `.pop(0)` để giả lập heap**
- [ ] Thu hồi vé hết hạn: O(m log N)

### M7 — SAA Benchmark
- [ ] Sinh S kịch bản ngẫu nhiên cho p
- [ ] Gọi pipeline M3→M4→M5 qua import, KHÔNG copy code
- [ ] So sánh Proposed (SAA M*) vs Baseline (Fixed M = C)
- [ ] Kết quả in ra bảng CLI, KHÔNG hard-code số liệu

---

## 4. LỖI THƯỜNG GẶP (ANTI-PATTERNS)

| Anti-pattern | Ví dụ | Tại sao sai |
|:---|:---|:---|
| Giả lập Heap bằng sort | `list.sort(key=...)` | Dùng hàm built-in, vi phạm quy chuẩn |
| Dùng scipy cho CDF | `binom.sf()` | Import thư viện giải thuật có sẵn |
| Test nằm trong class chính | `class Heap: def test_*()` | Test phải tách riêng file, kế thừa `unittest.TestCase` |
| Dead code sau `unittest.main()` | Code sau `if __name__ == '__main__': unittest.main()` | Code sau `unittest.main()` không bao giờ chạy |
| Class `KhongYeuCau` | `class KhongYeuCau: pass` | Hiểu nhầm chú thích "Class: KhongYeuCau" trong tài liệu |
| Biến `diem_loyalty` | Dùng tiếng Việt cho biến | Quy chuẩn yêu cầu biến tiếng Anh: `loyalty_score` |

---

## 5. MẪU BÁO CÁO REVIEW

```markdown
## Review Module M[X] — Ngày [DD/MM/YYYY]

### Kết quả
- Thuật toán tự viết 100%: ✅/❌
- Type Hints đầy đủ: ✅/❌
- Test coverage: ✅/❌ (N test cases)
- Interface khớp đặc tả: ✅/❌
- Complexity trong docstring: ✅/❌

### Lỗi phát hiện
1. [File:dòng] Mô tả lỗi
2. ...

### Đề xuất sửa
1. ...

### Trạng thái: ĐẠT / CHƯA ĐẠT
```
