# QUY TẮC CỐT LÕI — DỰ ÁN VIRTUAL WAITING ROOM & OVERBOOKING

> Bất kỳ agent nào thao tác trên codebase này đều **BẮT BUỘC** tuân thủ toàn bộ nội dung bên dưới. Không có ngoại lệ.

---

## R1. CƠ SỞ KHOA HỌC — KHÔNG ĐƯỢC BỊA ĐẶT

### 1.1 Nguồn gốc đề tài

Dự án này dựa trên bài báo:

> **"Joint optimization of overbooking and seat allocation for high-speed railways considering stochastic demand"**
> Nhóm tác giả: Đại học Trung Nam (Trung Quốc)
> Xuất bản: *PLOS ONE*, tháng 11/2024

Nhóm chuyển đổi bối cảnh từ **đường sắt tốc độ cao** sang **hệ thống bán vé Concert** kết hợp kiến trúc **Virtual Waiting Room** (chống sập server, tối ưu luồng vé nhả ra).

### 1.2 Ánh xạ khái niệm bài báo → dự án

| Khái niệm bài báo (HSR) | Ánh xạ dự án (Concert VWR) | Biến / Ký hiệu |
|:---|:---|:---|
| Sức chứa tàu (Capacity) | Sức chứa rạp/sân khấu | `capacity_C` hoặc `C` |
| Tỷ lệ hành khách no-show | Tỷ lệ bùng vé / rớt thanh toán | `drop_rate_p` hoặc `p` |
| Overbooking limit M | Hạn mức bán lố M* | `M_star` hoặc `m_star` |
| Xác suất từ chối lên tàu (DB rate) | Ngưỡng rủi ro chấp nhận được | `tau_0` |
| Phân bổ ghế theo chặng (OD pair) | Phân bổ vé theo hạng (VIP, Standard) | `allocation` |
| Chi phí bồi thường DB | Chi phí đền bù khách bị từ chối | `compensation_cost` |
| Doanh thu kỳ vọng | Doanh thu kỳ vọng từ bán vé concert | `expected_revenue` |
| Nhu cầu ngẫu nhiên (Poisson) | Nhu cầu mua vé dao động theo thời gian | `demand` |
| Sample Average Approximation | Mô phỏng Monte Carlo N kịch bản | `num_scenarios` |

### 1.3 Quy tắc không bịa đặt

- **KHÔNG** tự suy ra số liệu, kết quả benchmark, hoặc thông số mà không có căn cứ từ bài báo hoặc từ kết quả chạy code thực tế.
- **KHÔNG** giả lập kết quả test. Mọi kết quả phải đến từ runtime thực.
- Khi đặt giá trị mặc định cho tham số (ví dụ: `p = 0.2`, `tau_0 = 0.05`), phải ghi chú nguồn gốc hoặc lý do chọn.
- Mọi công thức toán học trong code phải trích dẫn được từ bài báo hoặc lý thuyết xác suất/tối ưu chuẩn.

### 1.4 Công thức cốt lõi từ bài báo

**Mô hình rủi ro overbooking:**

```
K ~ Binomial(M, 1 - p)    (K = số khách thực sự đến)

P(K > C) = 1 - Σ_{k=0}^{C} C(M,k) * (1-p)^k * p^(M-k)

Điều kiện an toàn: P(K > C) ≤ τ₀

Mục tiêu: Tìm M* lớn nhất thỏa mãn điều kiện an toàn
```

**Hàm doanh thu kỳ vọng (đơn giản hóa từ bài báo):**

```
E[Revenue] = Σ (giá vé × số vé bán) - E[chi phí bồi thường DB] - E[chi phí hoàn vé no-show]
```

---

## R2. QUY CHUẨN CODE — BẮT BUỘC 100%

### 2.1 Ngôn ngữ trong code

| Thành phần | Ngôn ngữ | Ví dụ đúng | Ví dụ SAI |
|:---|:---|:---|:---|
| Tên hàm public/private | Tiếng Việt không dấu, `snake_case` | `chia_de_tri_sap_xep_thoi_gian()` | `merge_sort()`, `runSort()` |
| Tên biến | Tiếng Anh kỹ thuật | `arrival_time`, `loyalty_score` | `thoi_gian_den`, `diem_uu_tien` |
| Comment | Tiếng Việt, ngắn gọn, 1 dòng | `# Chia mang thanh hai nua` | `# Đây là hàm chia mảng thành 2 phần bằng nhau rồi...` |
| Docstring | Tiếng Việt, có complexity | `"""Sap xep O(N log N), Space O(N)."""` | (thiếu complexity) |
| Tên class (nếu có) | Tiếng Việt không dấu, PascalCase | `HangDoiUuTienMaxHeap` | `MaxHeapPriorityQueue` |

### 2.2 Type Hints bắt buộc

Mọi hàm (public và private) phải có Type Hints đầy đủ trên tham số VÀ giá trị trả về:

```python
def trich_xuat_top_k_uu_tien(users: list[User], k: int) -> list[User]:
```

### 2.3 Thư viện CẤM sử dụng

```
CẤM TUYỆT ĐỐI (thuật toán phải viết tay):
- sort(), sorted()     → Tự viết Merge Sort
- heapq                → Tự viết Heap (sift-up, sift-down)
- bisect               → Tự viết Binary Search
- scipy                → Tự viết Binomial CDF
- numpy, pandas        → Không cần thiết

ĐƯỢC PHÉP:
- dataclasses          → Cho models.py
- collections.deque    → Cho Sliding Window queue
- random               → Cho mock data & Monte Carlo (M7)
- typing               → Cho Type Hints
- unittest             → Cho testing
- math                 → Cho log, factorial (KHÔNG cho giải thuật lõi)
```

### 2.4 Data Model bắt buộc

Toàn bộ pipeline giao tiếp qua 2 dataclass trong `models.py`:

```python
@dataclass
class User:
    user_id: int
    arrival_time: int
    loyalty_score: int
    ticket_type: str = ""
    status: str = "WAITING"

@dataclass
class Ticket:
    ticket_id: int
    ticket_type: str
    price: float
    expire_time: int
    assigned_user_id: int = -1
```

---

## R3. KIẾN TRÚC 7 MODULE — RANH GIỚI KHÔNG ĐƯỢC VƯỢT

### 3.1 Bảng phân công

| Module | Thuật toán | File | Hàm public bắt buộc |
|:---:|:---|:---|:---|
| M1 | Merge Sort (Divide & Conquer) | `thuat_toan_1_merge_sort.py` | `chia_de_tri_sap_xep_thoi_gian(users) → list[User]` |
| M2 | Max-Heap (Priority Queue) | `thuat_toan_2_max_heap.py` | `trich_xuat_top_k_uu_tien(users, k) → list[User]` |
| M3 | Binary Search + Binomial CDF | `thuat_toan_3_binary_search.py` | `tim_kiem_nhi_phan_nguong_ban_lo(C, tau_0, p) → int` |
| M4 | Bounded Knapsack DP | `thuat_toan_4_bounded_knapsack.py` | `quy_hoach_dong_phan_bo_ve(m_star, demands, prices) → dict` |
| M5 | Greedy Heuristic | `thuat_toan_5_greedy_conflict.py` | `xu_ly_xung_dot_tham_lam(users, seats) → tuple[float, list]` |
| M6 | Sliding Window + Min-Heap | `thuat_toan_6_sliding_window.py` | `cap_nhat_va_lay_ti_le_rot_o1(status) → float` + `thu_hoi_ve_het_han(time) → list[Ticket]` |
| M7 | SAA Monte Carlo | `thuat_toan_7_saa_benchmark.py` | `chay_danh_gia_saa(scenarios, C) → dict` |

### 3.2 Luồng dữ liệu (PHẢI TUÂN THỦ)

```
User thô → M1(Merge Sort) → Sorted Users
                                 ↓
M6(Sliding Window) → p(t) → M3(Binary Search) → M_star
                                                    ↓
                              M4(Knapsack DP) → {VIP: x, STD: y}
                                                    ↓
                   M2(Max-Heap top-k) ←─────────────┘
                         ↓
                   M6(Min-Heap TTL) → Hold/Release vé
                         ↓
                   M5(Greedy check-in) → Nâng hạng / Đền bù
                         ↓
                   M7(SAA) → Benchmark 100 vòng → Bảng so sánh CLI
```

### 3.3 Quy tắc ranh giới

- Mỗi module CHỈ xử lý đúng trách nhiệm được giao, KHÔNG can thiệp module khác.
- M7 CHỈ import và gọi hàm public từ M1-M6, KHÔNG copy thuật toán.
- main.py CHỈ điều phối, KHÔNG chứa thuật toán.

---

## R4. REVIEW BẮT BUỘC — MỖI MODULE PHẢI CÓ FILE MD

Trước khi viết code cho bất kỳ module nào, agent PHẢI:

1. **Đọc file review tương ứng** trong `docs/review_M{X}.md`
2. **Bám theo mục tiêu, input/output, và thuật toán** được mô tả trong file review đó
3. **Không thêm chức năng ngoài phạm vi** được mô tả

Nếu file review chưa tồn tại, agent phải tạo trước khi code.

---

## R5. LIÊN KẾT VỚI BÀI BÁO — MỌI THUẬT TOÁN PHẢI CÓ CĂN CỨ

| Module | Liên kết với bài báo |
|:---:|:---|
| M1 | Tiền xử lý dữ liệu đầu vào — sắp xếp theo thời gian đến (tương tự sắp xếp hành khách theo thời gian đặt vé) |
| M2 | Quản lý hàng đợi ưu tiên — tương tự cơ chế ưu tiên hành khách trung thành trong hệ thống đường sắt |
| M3 | **Cốt lõi bài báo:** Tính toán overbooking limit M* sao cho P(K>C) ≤ τ₀ — đây là ràng buộc DB rate trong mô hình |
| M4 | **Cốt lõi bài báo:** Seat allocation — phân bổ M* vé cho các hạng để tối đa doanh thu kỳ vọng (Bounded Knapsack) |
| M5 | Xử lý tình huống thực tế khi khách đến vượt C — nâng hạng hoặc bồi thường (Denied Boarding handling) |
| M6 | Theo dõi tỷ lệ no-show p(t) realtime — cung cấp dữ liệu đầu vào cho M3 để cập nhật M* |
| M7 | **Cốt lõi bài báo:** Sample Average Approximation — mô phỏng S kịch bản ngẫu nhiên để tìm nghiệm tối ưu trung bình |

---

## R6. DEFINITION OF DONE

Mỗi module chỉ được coi là hoàn thành khi đạt đủ 5 điều kiện:

1. ✅ Thuật toán viết tay 100% — không dùng thư viện cấm
2. ✅ Type Hints đầy đủ trên mọi tham số và return
3. ✅ Có ít nhất 1 test normal + 1 test edge case
4. ✅ Khớp chính xác tên hàm, tham số, kiểu dữ liệu trong bảng R3.1
5. ✅ Docstring có phân tích O(Time) và O(Space)

---

## R7. NGUYÊN TẮC PHÂN BIỆT BA TRẠNG THÁI

Agent phải phân biệt rõ:

- **Khai báo** = code tồn tại trong file nhưng chưa chắc đúng
- **Đường gọi** = có caller trong source code gọi đến hàm
- **Runtime kiểm chứng** = đã chạy test và pass

Không được nói "đã hoàn thành" nếu chỉ mới ở trạng thái "khai báo".
