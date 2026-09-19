# MASTER PROMPT: ĐẶC TẢ KIẾN TRÚC HỆ THỐNG & GIẢI THUẬT DỰ ÁN VIRTUAL WAITING ROOM (VWR)

> **Dành cho AI Agent / Kỹ sư phần mềm:** Đọc kỹ toàn bộ tài liệu này trước khi lập trình, tái cấu trúc hoặc kiểm thử bất kỳ module nào trong dự án. Bạn phải tuân thủ tuyệt đối các ràng buộc toán học, quy chuẩn code và ranh giới trách nhiệm giữa các module.

---

## I. TỔNG QUAN ĐỀ TÀI & CƠ SỞ KHOA HỌC

### 1. Nguồn gốc đề tài
Dự án được xây dựng dựa trên nền tảng bài báo khoa học quốc tế:
* **Tên bài báo:** *"Joint optimization of overbooking and seat allocation for high-speed railways considering stochastic demand"*
* **Tác giả:** Nhóm nghiên cứu Đại học Trung Nam (Central South University, Trung Quốc).
* **Xuất bản:** Tạp chí *PLOS ONE*, tháng 11/2024.

### 2. Ánh xạ thực tiễn: Đường sắt cao tốc ➔ Hệ thống bán vé Concert
Nhóm nghiên cứu chuyển đổi bài toán từ lĩnh vực **đường sắt tốc độ cao (High-Speed Railway)** sang bài toán **Phòng chờ ảo bán vé Concert (Concert Virtual Waiting Room - VWR)**:

| Khái niệm bài báo gốc (Đường sắt) | Ánh xạ sang hệ thống Concert VWR | Ký hiệu / Biến |
|:---|:---|:---:|
| Sức chứa đoàn tàu (Train Capacity) | Sức chứa khán phòng / sân vận động | `capacity_C` hoặc $C$ |
| Tỷ lệ hành khách no-show (bỏ vé) | Tỷ lệ rớt mạng, hủy thanh toán, bùng vé | `drop_rate_p` hoặc $p$ |
| Hạn mức bán vé vượt (Overbooking limit) | Hạn mức phát hành vé tối ưu | `m_star` hoặc $M^*$ |
| Ngưỡng từ chối phục vụ (DB rate threshold) | Ngưỡng rủi ro khách bị từ chối check-in | `tau_0` hoặc $\tau_0$ |
| Phân bổ chỗ theo chặng (OD seat allocation) | Phân bổ hạn mức vé theo hạng (VIP, Standard) | `allocation` |
| Bồi thường từ chối lên tàu (DB compensation) | Đền bù khi khách đến check-in vượt sức chứa $C$ | `compensation_cost` |
| Doanh thu kỳ vọng tối ưu | Doanh thu thuần = Doanh thu bán - Đền bù DB | `expected_revenue` |
| SAA (Sample Average Approximation) | Mô phỏng Monte Carlo trên $S$ kịch bản $p$ | `num_scenarios` hoặc $S$ |

### 3. Mô hình toán học cốt lõi
1. **Xác suất có mặt thực tế:** 
   Giả sử bán ra $M$ vé với xác suất khách hủy vé là $p$. Số lượng khách thực tế đến sự kiện $K$ tuân theo Phân phối Nhị thức:
   $$K \sim \text{Binomial}(M, 1 - p)$$
2. **Ràng buộc an toàn Denied Boarding (DB):**
   Xác suất số khách đến vượt quá sức chứa thực tế $C$ không được vượt quá ngưỡng rủi ro $\tau_0$ (thường là $5\%$):
   $$P(K > C) = 1 - \sum_{k=0}^{C} \binom{M}{k} (1 - p)^k p^{M - k} \le \tau_0$$
3. **Mục tiêu tối ưu:**
   * Tìm hạn mức bán vé lớn nhất $M^*$ thỏa mãn điều kiện an toàn trên (Module M3).
   * Phân bổ $M^*$ vé cho các hạng vé VIP, Standard để tối đa hóa doanh thu bằng Quy hoạch động (Module M4).
   * Đánh giá kỳ vọng doanh thu thực tế qua $S$ kịch bản Monte Carlo (Module M7).

---

## II. QUY CHUẨN LẬP TRÌNH BẮT BUỘC (CODE CONVENTION)

> **CẢNH BÁO:** Bất kỳ dòng code nào vi phạm các nguyên tắc dưới đây đều bị coi là KHÔNG HỢP LỆ.

1. **CẤM TUYỆT ĐỐI THƯ VIỆN CÓ SẴN CHO GIẢI THUẬT LÕI:**
   * ❌ CẤM `sort()`, `sorted()` ➔ **Bắt buộc tự viết tay** Merge Sort (M1) hoặc Selection Sort.
   * ❌ CẤM `heapq` ➔ **Bắt buộc tự viết tay** cấu trúc Heap (mảng 1 chiều, thao tác `sift-up`, `sift-down`).
   * ❌ CẤM `bisect` ➔ **Bắt buộc tự viết tay** thuật toán Binary Search.
   * ❌ CẤM `scipy`, `numpy`, `pandas` ➔ **Tự viết tay** tích lũy phân phối nhị thức CDF và mô phỏng Monte Carlo.
   * ✅ **ĐƯỢC PHÉP DÙNG:** `dataclasses`, `typing`, `collections.deque` (cho sliding window), `random` (chỉ để sinh số ngẫu nhiên mô phỏng), `math` (cho `log`, `ceil`, `comb`).

2. **QUY TẮC ĐẶT TÊN & NGÔN NGỮ:**
   * **Tên hàm:** Tiếng Việt không dấu, chuẩn `snake_case` (ví dụ: `chia_de_tri_sap_xep_thoi_gian()`, `tim_kiem_nhi_phan_nguong_ban_lo()`, `tim_nghiem_saa_chuan()`).
   * **Tên biến & thuộc tính:** 100% Tiếng Anh kỹ thuật (`arrival_time`, `loyalty_score`, `capacity_C`, `ticket_classes`).
   * **Comment:** Tiếng Việt, ngắn gọn 1 dòng, mô tả bản chất toán học/giải thuật.
   * **Docstring:** Tiếng Việt, **bắt buộc ghi rõ** độ phức tạp thời gian $\mathcal{O}(\text{Time})$ và không gian $\mathcal{O}(\text{Space})$.
   * **Type Hints:** Bắt buộc 100% trên tất cả tham số đầu vào và kiểu trả về.

3. **NGUYÊN TẮC BẰNG CHỨNG (KHÔNG BỊA ĐẶT):**
   * Phân biệt rõ: **Khai báo** $\ne$ **Đường gọi (caller)** $\ne$ **Runtime thực tế**.
   * Mọi số liệu đo lường, benchmark phải chạy ra từ code thực tế, không được hard-code số liệu giả định.

---

## III. BẢN ĐỒ KIẾN TRÚC 7 MODULE & PHÂN CHIA TRÁCH NHIỆM

### 1. Bảng phân công 7 thành viên (TV1 ➔ TV7)

| Module | Thành viên | Thuật toán lõi | Tên file code | Hàm public bắt buộc | Độ phức tạp |
|:---:|:---:|:---|:---|:---|:---:|
| **M1** | TV1 | **Merge Sort** (Chia để trị) | `thuat_toan_1_sinh_du_lieu.py` | `chia_de_tri_sap_xep_thoi_gian(users)` | $\mathcal{O}(N \log N)$ |
| **M2** | TV2 | **Max-Heap** (Hàng đợi ưu tiên) | `thuat_toan_2_hang_doi_heap.py` | `them_khach_hang()`, `trich_xuat_top_k(k)` | $\mathcal{O}(K \log N)$ |
| **M3** | TV3 | **Binary Search** + Binomial CDF | `thuat_toan_3_tim_kiem_nhi_phan_M3_hoan_chinh.py` | `tim_kiem_nhi_phan_nguong_ban_lo(C, p, tau_0)` | $\mathcal{O}(C \log(\text{limit}))$ |
| **M4** | TV4 | **Bounded Knapsack DP** (Quy hoạch động) | `thuat_toan_4_quy_hoach_dong.py` | `quy_hoach_dong_phan_bo_ve(m_star, classes)` | $\mathcal{O}(N \cdot M^*)$ |
| **M5** | TV5 | **Greedy Heuristic** (Xử lý xung đột) | `thuat_toan_5_tham_lam_xung_dot.py` | `xu_ly_xung_dot_tham_lam(txs, alloc, C)` | $\mathcal{O}(K)$ |
| **M6** | TV6 | **Min-Heap** (TTL) + **Sliding Window** | `thuat_toan_6_thu_hoi_va_truot.py` | `thu_hoi_ve_het_han(t)`, `lay_ti_le_rot_o1()` | Heap: $\mathcal{O}(\log N)$, Window: $\mathcal{O}(1)$ |
| **M7** | TV7 | **SAA + Monte Carlo Benchmark** | `thuat_toan_7_saa_benchmark.py` | `tim_nghiem_saa_chuan()`, `in_bang_so_sanh_thuc_te()` | $\mathcal{O}(S \cdot \text{Pipeline})$ |

---

### 2. Luồng luân chuyển dữ liệu (System Pipeline Flow)

```text
               DỮ LIỆU KHÁCH HÀNG THÔ (User Arrival Stream)
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Module 1: CHIA ĐỂ TRỊ - MERGE SORT (thuat_toan_1_sinh_du_lieu.py)     │
│ Sắp xếp danh sách User theo arrival_time tăng dần: O(N log N)         │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ Sorted Users
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Module 2: MAX-HEAP PRIORITY QUEUE (thuat_toan_2_hang_doi_heap.py)     │
│ Trích xuất Top K khách hàng có loyalty_score cao nhất vào phòng mua vé│
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ Top-K Eligible Users
                                    │
┌───────────────────────────────────┴───────────────────────────────────┐
│ Module 6: SLIDING WINDOW (thuat_toan_6_thu_hoi_va_truot.py)           │
│ Theo dõi tỷ lệ hủy vé p(t) trong cửa sổ thời gian trượt: O(1)         │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ Real-time drop rate p(t)
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Module 3: TÌM KIẾM NHỊ PHÂN - BINARY SEARCH (thuat_toan_3_...)        │
│ Tìm hạn mức bán lố tối ưu M* sao cho P(K > C) <= tau_0                │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ Optimal limit M*
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Module 4: QUY HOẠCH ĐỘNG - BOUNDED KNAPSACK (thuat_toan_4_...)        │
│ Phân bổ M* vé cho các hạng VIP, Standard để tối đa hóa doanh thu      │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │ Seat Allocation Dict {VIP: x, STD: y}
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Module 5: THAM LAM - GREEDY HEURISTIC (thuat_toan_5_...)              │
│ Check-in thực tế: Nâng hạng ghế hoặc đền bù 150% nếu K > C            │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Module 7: ĐIỀU PHỐI BENCHMARK SAA (thuat_toan_7_saa_benchmark.py)     │
│ Chạy Monte Carlo S kịch bản -> Xuất bảng đối soát Proposed vs Baseline│
└───────────────────────────────────────────────────────────────────────┘
```

---

### 3. Ranh giới trách nhiệm (Strict Ownership Boundaries)
* **TV1 (M1):** Chỉ chuẩn hóa và sắp xếp thời gian đến. Tuyệt đối không can thiệp vào điểm ưu tiên hay phân bổ vé.
* **TV2 (M2):** Chỉ duy trì cấu trúc Max-Heap để chọn khách hàng ưu tiên. Không tính toán hạn mức $M^*$ hay chia hạng vé.
* **TV3 (M3):** Chỉ giải bài toán xác suất nhị thức tìm $M^*$. Không quản lý hàng đợi, không quyết định số lượng ghế từng hạng.
* **TV4 (M4):** Nhận $M^*$ từ M3 để lập bảng DP cái túi phân bổ vé. Không tự ý thay đổi $M^*$ hay điểm ưu tiên của khách.
* **TV5 (M5):** Chỉ xử lý tình huống xung đột tại thời điểm check-in (nâng hạng / đền bù). Không chạy thuật toán tìm nghiệm toàn cục.
* **TV6 (M6):** Quản lý Min-Heap thời gian giữ chỗ (TTL) và trả về tỷ lệ rớt $p(t)$ trong $\mathcal{O}(1)$. Không xử lý bồi thường tranh chấp.
* **TV7 (TV7/Orchestrator):** Chỉ đóng vai trò điều phối pipeline, sinh kịch bản ngẫu nhiên và đo lường benchmark. **Cấm sao chép code lõi** của M1-M6 vào M7.

---

## IV. MA TRẬN 10 ĐẦU VIỆC CHUẨN TỪNG MODULE (TASK A ➔ J)

Mỗi module khi hoàn thành bắt buộc phải đạt đủ 10 bước:
* **Task A (Chuẩn bị):** Phân tích đặc tả đầu vào, đọc hiểu cấu trúc dữ liệu.
* **Task B (Thiết kế dữ liệu):** Khai báo Data Structure (List, Dict, Heap array, DP table) và Type Hints đầy đủ.
* **Task C (Cài thuật toán lõi):** Lập trình logic thuật toán thuần túy 100% viết tay (không dùng thư viện ngoài).
* **Task D (Cài helper):** Tách bạch các hàm bổ trợ (sift-up, sift-down, partition, merge, v.v.).
* **Task E (Cài public function):** Xây dựng hàm giao tiếp chính theo đúng tên gọi chuẩn trong hợp đồng.
* **Task F (Xử lý edge cases):** Bẫy lỗi dữ liệu rỗng (`None`), số âm, danh sách 0 phần tử, quá tải sức chứa.
* **Task G (Unit test):** Viết file test độc lập (`test_thuat_toan_*.py`) kiểm thử ít nhất 1 test case chuẩn và 1 test case cực đoan.
* **Task H (Kiểm tra complexity):** Đo đạc runtime và giải trình độ phức tạp thời gian/không gian trong docstring.
* **Task I (Review & Refactor):** Rà soát naming convention (hàm tiếng Việt snake_case, biến tiếng Anh), comment ngắn 1 dòng.
* **Task J (Bàn giao):** Đóng gói interface trả về dữ liệu chuẩn xác cho module kế tiếp hoặc CLI report.

---

## V. ĐẶC TẢ CHI TIẾT MODULE 7 (SAA & BENCHMARK)

### 1. Nhiệm vụ chính của TV7
* **File thực thi:** `thuat_toan_7_saa_benchmark.py`
* **File kiểm thử:** `test_thuat_toan_7_saa_benchmark.py`
* **Hàm public bắt buộc:**
  ```python
  def tim_nghiem_saa_chuan(
      S: int = 100,
      distributions: Optional[Dict[str, Any]] = None,
      capacity_C: int = 100,
      tau_0: float = 0.05,
      ticket_classes: Optional[List[Dict[str, Any]]] = None,
      seed: Optional[int] = 42
  ) -> Dict[str, Any]: ...

  def in_bang_so_sanh_thuc_te(benchmark_result: Dict[str, Any]) -> None: ...
  ```

### 2. Logic vận hành của SAA Benchmark
1. **Sinh mẫu ngẫu nhiên (Sampling):** Sinh danh sách $S$ kịch bản tỷ lệ bỏ vé $p(s)$ theo phân phối Uniform, Beta, hoặc Normal.
2. **Tìm nghiệm SAA:** Với mỗi kịch bản $p(s)$, tính $M_s^*$ qua M3, sau đó lấy nghiệm đại diện kỳ vọng:
   $$M^*_{\text{SAA}} = \text{round}\left(\frac{1}{S} \sum_{s=1}^S M_s^*\right)$$
3. **Mô phỏng đối soát thực nghiệm (Proposed vs Baseline):**
   * **Proposed (Đề xuất có SAA Overbooking):** Phát hành $M^*_{\text{SAA}}$ vé. Số khách thực tế đến $K \sim \text{Binomial}(M^*_{\text{SAA}}, 1 - p)$. Nếu $K > C$, số khách bị Denied Boarding là $K - C$ và chịu bồi thường $150\%$ giá vé. Doanh thu thuần = Doanh thu bán vé - Chi phí đền bù.
   * **Baseline (Cố định truyền thống):** Chỉ bán đúng $C$ vé ($M = C$, không overbooking). Không bao giờ có khách bị DB nhưng phải chịu lãng phí ghế trống do khách hủy vé.
4. **Bảng so sánh đầu ra:** In bảng trực quan ra Console thể hiện: Doanh thu thuần, Hạn mức $M^*$, Tỷ lệ Overbooking, Số khách DB, Ghế trống lãng phí và % Tăng trưởng doanh thu thực tế.

---

## VI. HƯỚNG DẪN DÀNH CHO AGENT TIẾP QUẢN

Khi nhận bất kỳ yêu cầu nào liên quan đến codebase này:
1. **Kiểm tra trạng thái Git hiện tại:** Luôn kiểm tra `git status` và `git branch` để biết đang làm việc trên nhánh nào.
2. **Bảo toàn tính toàn vẹn giải thuật:** Không bao giờ import các hàm `sorted`, `heapq`, `bisect`, `scipy`.
3. **Không phá vỡ Type Hints:** Mọi hàm mới thêm vào phải có type hints đầy đủ.
4. **Bảo vệ các file không commit:** Tuyệt đối không commit các file tài liệu cá nhân, `.docx`, `.xlsx` hoặc `.agents/` lên remote nếu người dùng không yêu cầu.
5. **Kiểm chứng runtime trước khi kết luận:** Chạy lệnh unit test và kiểm tra terminal trước khi thông báo hoàn thành nhiệm vụ.
