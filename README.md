# 🎟️ Virtual Waiting Room cho Hệ Thống Bán Vé Concert (K26 UTH)

> **Môn học:** Phân tích và Thiết kế Giải thuật (PTTKGT)  
> **Trường:** Trường Đại học Giao thông Vận tải TP.HCM (UTH)  
> **Đề tài:** Xây dựng hệ thống Phòng chờ ảo (Virtual Waiting Room) chống nghẽn và kiểm soát tranh chấp vé concert quy mô lớn.

---

## 📌 1. Giới thiệu tổng quan đề tài
Khi mở bán vé các sự kiện âm nhạc quy mô lớn (Concert), hàng chục nghìn đến hàng triệu người dùng truy cập cùng một lúc tạo ra lưu lượng đột biến (Traffic Spike), gây quá tải cơ sở dữ liệu và sập hệ thống (Crash).

Hệ thống **Virtual Waiting Room** hoạt động như một tầng đệm thông minh (Smart Buffer Layer) đứng trước Backend/Database để:
1. **Điều tiết lưu lượng truy cập (Traffic Shaping / Rate Limiting)** theo năng lực phục vụ của hệ thống.
2. **Xếp hàng công bằng và linh hoạt** (FIFO hoặc Ưu tiên theo điểm xếp hạng/thời gian chờ).
3. **Quản lý thời hạn giữ vé tạm thời (TTL Seat Holding)** để tránh chiếm giữ ghế ảo.
4. **Kiểm soát tranh chấp đồng thời (Concurrency Control)** chống bán trùng 1 ghế cho nhiều người (Double Booking).
5. **Mô phỏng sự kiện rời rạc (Discrete-Event Simulation)** và trực quan hóa luồng xử lý qua giao diện tương tác.

---

## 🏗️ 2. Kiến trúc luồng xử lý toàn hệ thống (System Architecture)

```
[ User Requests (Hàng ngàn yêu cầu) ]
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 1. HÀNG ĐỢI XẾP LƯỢT (FIFO Queue / Priority Queue + Aging)│
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. ĐIỀU TIẾT LƯU LƯỢNG (Leaky Bucket / Token Bucket)    │ ─── (Cấp lượt vé)
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. QUẢN LÝ THỜI HẠN GIỮ GHẾ (TTL 300s / Min-Heap)       │ ─── (Hết hạn -> Thu hồi)
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. XỬ LÝ TRANH CHẤP MUA GHẾ (Concurrency Lock / Atomic) │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 5. QUẢN LÝ TRẠNG THÁI GHẾ (Finite State Machine - FSM)  │
│    AVAILABLE ──> HOLD ──> SOLD / EXPIRED                │
└─────────────────────────────────────────────────────────┘
```

---

## 👥 3. Bảng phân công nhiệm vụ chi tiết (8 Thành viên)

| STT | Thành viên phụ trách | Thuật toán / Kỹ thuật | Công việc code cụ thể | Sản phẩm bàn giao |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Hàng đợi FIFO** | `Queue`, `FIFO`, mô hình `M/M/c` để phân tích lý thuyết | Cài đặt thêm người vào hàng đợi, lấy người đầu tiên, xem vị trí, tính thời gian chờ. Viết chương trình mô phỏng FIFO với nhiều request. | Module FIFO, bộ test, mã giả, phân tích $O(1)$ cho enqueue/dequeue với cấu trúc phù hợp, kết quả thời gian chờ. |
| **2** | **Hàng đợi ưu tiên** | `Max-Heap`, `Priority Queue`, `Aging` | Cài đặt Heap, thêm/lấy request ưu tiên, tính điểm ưu tiên theo thời gian chờ, xử lý cập nhật Aging. So sánh thứ tự phục vụ với FIFO. | Module Priority Queue + Aging, bộ test, mã giả, phân tích độ phức tạp, kết quả so sánh FIFO/Priority. |
| **3** | **Điều tiết lưu lượng** | `Leaky Bucket` và `Token Bucket` | Cài đặt hai thuật toán giới hạn tốc độ cấp lượt. Cho phép cấu hình tốc độ xử lý, dung lượng bucket, mô phỏng request đến dồn dập và ghi nhận request được cấp lượt/chờ/từ chối. | Module Traffic Control, bộ test, mã giả, phân tích độ phức tạp, bảng so sánh Leaky Bucket và Token Bucket. |
| **4** | **Quản lý thời hạn giữ vé** | `Min-Heap`, `TTL` (Time To Live) | Cài đặt tạo lượt giữ ghế 300 giây, lưu thời điểm hết hạn, tìm lượt hết hạn sớm nhất, tự động giải phóng ghế, xử lý hủy hoặc gia hạn nếu nhóm có hỗ trợ. | Module Hold Manager, bộ test, mã giả, phân tích $O(\log h)$ cho thao tác Heap, demo ghế tự nhả khi hết hạn. |
| **5** | **Xử lý tranh chấp mua ghế** | `Concurrency Lock`, `Greedy`, `Dynamic Programming`, `Deadlock Prevention` | Cài đặt nhiều luồng cùng mua một ghế, kiểm tra và cập nhật ghế trong vùng khóa, thuật toán chọn ghế tham lam, thuật toán DP tìm cụm ghế, demo không bán trùng ghế. | Module Concurrency, bộ test tranh chấp, mã giả, phân tích cơ chế khóa và độ phức tạp giải thuật. |
| **6** | **Quản lý trạng thái ghế** | `FSM` (Finite State Machine), `State Transition Validation` | Cài đặt `AVAILABLE` $\rightarrow$ `HOLD` $\rightarrow$ `SOLD`, xử lý `HOLD` $\rightarrow$ `AVAILABLE` khi hủy/hết hạn, kiểm tra chuyển trạng thái hợp lệ, xử lý thanh toán thành công/thất bại giả lập. | Module Seat FSM, sơ đồ trạng thái, bộ test, mã giả, bảng các chuyển trạng thái hợp lệ và không hợp lệ. |
| **7** | **Sinh dữ liệu và Benchmark** | `Data Generation`, `Benchmarking`, phân tích độ phức tạp thực nghiệm | Sinh các bộ request giả lập, chạy benchmark cho FIFO, Priority Queue, Traffic Control và các module khác; đo execution time, bộ nhớ, throughput, thời gian chờ; xuất CSV và biểu đồ PNG. | Script sinh dữ liệu, Benchmark Framework, bộ dữ liệu mẫu, bảng kết quả, biểu đồ và báo cáo so sánh. |
| **8** | **Bộ mô phỏng và giao diện** | `Discrete-Event Simulation`, `Event Queue (Min-Heap)` | Cài đặt bộ điều phối sự kiện, kết nối các module, mô phỏng người vào hàng đợi $\rightarrow$ được cấp lượt $\rightarrow$ giữ ghế $\rightarrow$ thanh toán/hết hạn. Dựng Streamlit để chạy demo và xem kết quả. | Simulation Engine, giao diện Streamlit, kịch bản demo, bộ test tích hợp, chương trình chạy hoàn chỉnh. |

---

## ⚡ 4. Chi tiết các thuật toán PTTKGT trong Module 5 (Xử lý tranh chấp & Phân bổ ghế)

Module 5 cài đặt đầy đủ các thuật toán thuộc giáo trình **Phân tích và Thiết kế Giải thuật**:

### 4.1. Thuật toán Tham lam (Greedy Best-Fit Allocation - Chương 6)
* **Mục tiêu:** Tự động đề xuất ghế đơn tối ưu nhất còn trống cho người dùng VIP/Standard.
* **Hàm mục tiêu tham lam:** $f(s) = \sqrt{\Delta \text{Row}^2 + \Delta \text{Col}^2}$ (Khoảng cách Euclid tới tâm sân khấu).
* **Độ phức tạp:** $\mathcal{O}(S)$ với $S$ là tổng số ghế.

### 4.2. Thuật toán Quy hoạch động / Cửa sổ trượt (DP / Sliding Window - Chương 5 & 2)
* **Mục tiêu:** Tìm cụm $k$ ghế trống liền kề nhau trong cùng 1 hàng có vị trí cân đối gần tâm sân khấu nhất cho nhóm bạn.
* **Độ phức tạp:** $\mathcal{O}(M)$ với $M$ là số ghế trong hàng.

### 4.3. Giải thuật Sắp xếp chống Bế tắc (Deadlock Prevention via Sorting - Chương 2 & 4)
* **Mục tiêu:** Khi mua đồng thời cụm $k$ ghế, giải thuật sắp xếp danh sách mã ghế theo thứ tự từ điển $\mathcal{O}(k \log k)$ trước khi Acquire Lock.
* **Ý nghĩa lý thuyết:** Phá vỡ điều kiện *Circular Wait* (Chờ đợi vòng tròn) trong bài toán Deadlock kinh điển.

### 4.4. Giải thuật Khóa phân rã (Fine-Grained Mutex Lock & Critical Section - Chia để trị Chương 4)
* Phân rã không gian phòng vé thành từng chiếc ghế độc lập. Mỗi ghế có 1 Lock riêng, giúp các luồng mua ghế khác nhau chạy song song với thời gian $\mathcal{O}(1)$.

---

## 💻 5. Cấu trúc thư mục dự án

```
PTTKGT_Virtual-Waiting-Room_K26/
│
├── README.md                          # Tài liệu tổng quan dự án & phân công
├── hàng đợi ưu tiên-1.py              # Module 2: Priority Queue + Aging (Max-Heap)
├── quản lý thời hạn giữ vé.py        # Module 4: Quản lý TTL giữ vé (Min-Heap)
├── xử lý tranh chấp mua ghế.py       # Module 5: Concurrency Control & Thuật toán PTTKGT
│
└── ... (Các module FIFO, Rate Limiter, FSM, Benchmark, Streamlit UI tiếp tục cập nhật)
```

---

## 🚀 6. Hướng dẫn chạy thử nghiệm

### Chạy kiểm thử Module 5 (Xử lý tranh chấp & Thuật toán phân bổ ghế):
```bash
python "xử lý tranh chấp mua ghế.py"
```

### Chạy kiểm thử Module 4 (Quản lý thời hạn giữ vé - TTL):
```bash
python "quản lý thời hạn giữ vé.py"
```

### Chạy kiểm thử Module 2 (Hàng đợi ưu tiên - Priority Queue):
```bash
python "hàng đợi ưu tiên-1.py"
```

---
*Bản quyền thuộc về Nhóm đồ án Phân tích Thiết kế Giải thuật - Khóa K26 UTH.*