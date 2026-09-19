# MASTER PROMPT v2.0: THIẾT KẾ UI/UX HỆ THỐNG PHÒNG CHỜ ẢO & OVERBOOKING QUY MÔ ĐẠI NHẠC HỘI QUỐC GIA (5,000 – 40,000 GHẾ)

> **Dành cho AI Agent / Kỹ sư Frontend & UI/UX:** Đọc kỹ toàn bộ đặc tả này trước khi thiết kế hoặc lập trình giao diện.
> **Thay đổi so với v1.0:** Đã gỡ toàn bộ số liệu hard-code sai lệch, bổ sung hợp đồng API, phân tách sức chứa vật lý ↔ hạn mức nhu cầu, thêm nguyên tắc miễn trừ Denied Boarding cho nhóm tri ân, sửa 2 mã màu fail WCAG AAA, bổ sung kiến trúc hiệu năng cho tải thật.

---

## 0. NGUYÊN TẮC NỀN TẢNG — BẮT BUỘC ĐỌC TRƯỚC

> ⚠️ **QUY TẮC TỐI THƯỢNG:** Frontend **KHÔNG BAO GIỜ** tự tính lại thuật toán (Merge Sort, Binary Search, Knapsack DP, Monte Carlo...) bằng JavaScript. Toàn bộ 7 module thuật toán chạy 100% trên backend Python (`server.py`), tuân thủ quy chuẩn viết tay không dùng thư viện có sẵn (`sort`, `heapq`, `bisect`, `scipy`, `numpy`). Frontend chỉ gọi API và **render** kết quả runtime thật.

> ⚠️ **KHÔNG HARD-CODE SỐ LIỆU.** Mọi con số trong tài liệu này (M*, doanh thu, tỷ lệ DB, ghế trống...) là **giá trị minh họa** để hình dung giao diện. Giá trị thật phải lấy từ response API tại thời điểm chạy. Nếu code frontend có bất kỳ số nào giống hệt bảng dưới đây mà không đi qua `fetch()`, đó là lỗi.

---

## I. BỐI CẢNH DỰ ÁN & QUY MÔ SÂN VẬN ĐỘNG THỰC TẾ

### 1. Tên đề tài & Định vị sản phẩm
* **Tên hệ thống:** Hệ Thống Phòng Chờ Ảo (Virtual Waiting Room - VWR) & Bán Vé Lố (Stochastic Overbooking) Đại Nhạc Hội Quốc Gia 2026.
* **Bối cảnh sự kiện:** Đêm Đại Nhạc Hội Tri Ân Người Có Công Với Đất Nước.
* **Cơ sở khoa học:** *"Joint optimization of overbooking and seat allocation for high-speed railways considering stochastic demand"*, PLOS ONE, 11/2024.

### 2. Bộ thông số địa điểm thực tế (Venue Presets)

> Các cột **M\*, Overbooking %, Doanh thu** trong bảng dưới đây là **placeholder minh họa cho mục đích thiết kế UI** — không phải số cam kết. Khi người dùng chọn preset, frontend gọi `POST /api/pipeline/run` với `capacity_C` tương ứng và render số thật trả về.

| Địa điểm tổ chức | Sức chứa thực tế ($C$) | Lưu lượng phòng chờ ước tính | Ghi chú |
|:---|:---:|:---:|:---|
| **🏟️ Sân Vận Động Quốc Gia Mỹ Đình** *(Mặc định)* | **40,000 ghế** | **150,000 – 250,000 người** | M*, doanh thu = kết quả runtime |
| **🏛️ Cung Thể Thao / Nhà Thi Đấu Quốc Tế** | **10,000 ghế** | **40,000 – 60,000 người** | M*, doanh thu = kết quả runtime |
| **🎭 Trung Tâm Hội Nghị Quốc Gia** | **3,800 ghế** | **15,000 – 25,000 người** | M*, doanh thu = kết quả runtime |

### 3. Cơ cấu phân bổ 4 phân khu khán đài (Stadium Sector Categories)

> ⚠️ **Điểm sửa quan trọng (GAP-4):** Phải phân biệt rạch ròi hai khái niệm khác nhau, nếu không Module M4 (Bounded Knapsack DP) sẽ không có gì để tối ưu:

| Khái niệm | Ý nghĩa | Vai trò trong hệ thống |
|:---|:---|:---|
| **Sức chứa vật lý (`physical_cap`)** | Số ghế thật sự tồn tại trong kiến trúc sân, cố định | Trần cứng, không đổi |
| **Hạn mức nhu cầu (`demand_limit`)** | Số vé tối đa cho phép bán ra mỗi hạng (bao gồm overbooking), biến động theo cầu thị trường | **Đây là ràng buộc mà M4 DP tối ưu trên đó** |

M4 phân bổ $M^*$ vé sao cho mỗi sector thỏa: `qty_sector ≤ min(physical_cap × overbooking_factor, demand_limit)`, đồng thời tối đa hóa tổng doanh thu. Nếu `demand_limit` bị set bằng đúng tỷ lệ cố định thì DP suy biến — vì vậy hệ thống demo nên cho phép người vận hành **kéo slider `demand_limit`** từng hạng để thấy DP phân bổ thay đổi theo thời gian thực (đây là lúc M4 mới thực sự "diễn").

| Phân khu | Sức chứa vật lý (Mỹ Đình) | Giá vé | Đặc quyền |
|:---|:---:|:---:|:---|
| **VVIP Diamond** *(Ghế Danh Dự & Đại Biểu Tri Ân)* | 4,000 ghế (10%) | 4,500,000 đ | Sofa VIP chính diện, lối đi thảm đỏ, quà tri ân quốc gia |
| **VIP Platinum** *(Khán Đài A1–A2)* | 10,000 ghế (25%) | 2,500,000 đ | Ghế tựa đệm cao cấp, âm thanh vòm |
| **Gold Standard** *(Khán Đài B — Tầng 1)* | 16,000 ghế (40%) | 1,200,000 đ | Tầm nhìn bao quát sân khấu, trình diễn ánh sáng/drone |
| **Silver Economy** *(Khán Đài C & D — Tầng 2–3)* | 10,000 ghế (25%) | 600,000 đ | Vé phổ thông, tiếp cận đông đảo nhân dân |

### 4. ⭐ Nguyên tắc bảo vệ nhóm tri ân (GAP-7 — BẮT BUỘC)

> Đây là sự kiện tri ân người có công. Hệ thống **tuyệt đối không được** để một Bà mẹ Việt Nam Anh hùng, Thương binh, hoặc Cựu chiến binh bị từ chối check-in (Denied Boarding) vì lý do bán lố vé.

**Ràng buộc nghiệp vụ bắt buộc đưa vào M4 và M5:**
1. M4 dành riêng một `protected_pool` = tổng số vé đã bán cho nhóm chính sách (Mẹ VNAH, Thương binh, CCB, Con liệt sĩ) — nhóm này **không nằm trong diện tính overbooking**, luôn được đảm bảo ghế 1:1.
2. M5 (Greedy Heuristic check-in): khi `K > C`, thuật toán **chỉ được xét nâng hạng/từ chối trên nhóm khách phổ thông**, hàng đợi Denied Boarding loại trừ hoàn toàn nhóm chính sách.
3. Giao diện Command Center phải hiển thị công khai chỉ số: **"Tỷ lệ khách chính sách bị ảnh hưởng: 0.00%"** như một cam kết đạo đức của hệ thống — đây cũng là điểm nhấn thuyết trình mạnh.

---

## II. HỆ THỐNG THẨM MỸ & BẢNG MÀU (DESIGN SYSTEM)

* **Phong cách chủ đạo:** **Cyber-National Luxury** — trang trọng quốc gia kết hợp công nghệ tài chính tối tân.
* **Hiệu ứng giao diện:**
  * **Dark Mode Glassmorphism:** `rgba(15, 23, 42, 0.75)` + `backdrop-filter: blur(16px)` + viền `rgba(255, 255, 255, 0.08)`.
  * ⚠️ **Giới hạn hiệu năng:** `backdrop-filter: blur()` là filter tốn GPU nhất trong CSS. **Tối đa 5 bề mặt kính mờ hiển thị đồng thời** trên một màn hình; các thẻ còn lại dùng nền đặc `#0F172A`.
  * **Dynamic Glow & Pulsing:** hiệu ứng viền phát sáng nhịp thở cho TTL Countdown, cảnh báo quá tải. Phải tắt được qua `prefers-reduced-motion` (xem mục V.4).

### Bảng màu chuẩn — đã kiểm chứng WCAG AAA (≥7:1 trên nền `#050814`)

| Vai trò | Mã màu v1.0 | Tỷ lệ tương phản | Trạng thái | Mã màu v2.0 (nếu cần sửa) |
|:---|:---:|:---:|:---:|:---:|
| Deep Canvas (nền) | `#050814` → `#0A1128` | — | — | Giữ nguyên |
| Imperial Gold (CTA, huy hiệu tri ân) | `#D4AF37` | 9.5:1 | ✅ Pass | Giữ nguyên |
| Amber (số tiền tỷ) | `#F59E0B` | 9.3:1 | ✅ Pass | Giữ nguyên |
| Cyber Cyan (biểu đồ, thanh tiến trình) | `#06B6D4` | 8.2:1 | ✅ Pass | Giữ nguyên |
| Emerald Success (check-in thành công) | `#10B981` | 7.8:1 | ✅ Pass | Giữ nguyên |
| Cyber Blue (dòng người phòng chờ) | `#3B82F6` | 5.4:1 | ❌ **Fail** | **`#60A5FA`** (7.9:1) |
| Ruby Danger (cảnh báo quá tải, DB) | `#EF4444` | 5.3:1 | ❌ **Fail** | **`#F87171`** (7.3:1) |

> ⚠️ Trên nền kính mờ `rgba(15,23,42,0.75)`, độ tương phản thực tế **thấp hơn** bảng trên vì nền sáng phía sau hắt qua lớp blur. Với các văn bản quan trọng đặt trên card kính mờ, tăng độ đục lên `rgba(15,23,42,0.88)` hoặc kiểm tra lại bằng công cụ contrast checker trong ngữ cảnh thật.

* **Typography:**
  * Tiêu đề & Banner: `Plus Jakarta Sans` hoặc `Outfit` (Bold).
  * Số liệu kỹ thuật & Tài chính: `JetBrains Mono` hoặc `Inter` (phân cách hàng nghìn: `88.650.000.000 đ`).

---

## III. KIẾN TRÚC GIAO DIỆN HAI GÓC NHÌN (DUAL-VIEW ARCHITECTURE)

Sticky Header với nút chuyển đổi góc nhìn:
```text
[ 🎫 CỔNG KHÁN GIẢ SỐ LƯỢNG LỚN (CITIZEN PORTAL) ]  ⟷  [ 📊 TRUNG TÂM CHỈ HUY ĐIỀU HÀNH (COMMAND CENTER) ]
```

---

### GÓC NHÌN 1: CỔNG KHÁN GIẢ — TRẢI NGHIỆM PHÒNG CHỜ ẢO QUY MÔ KHỦNG

1. **Thanh cảnh báo tải lưu lượng:** Chạy chữ động, nội dung lấy từ `GET /api/queue/status` (số người đang chờ = giá trị runtime, không hard-code).

2. **Thẻ Xếp Hàng Khán Giả (Live Queue Ticket Card):**
   * Số thứ tự hàng đợi + tổng số người chờ — lấy từ polling `GET /api/queue/status/{user_id}`.
   * Nhóm ưu tiên tri ân + điểm ưu tiên (`loyalty_score`).
   * Thanh tiến trình (Animated Progress Stepper).
   * **Tốc độ xả phòng chờ** và **thời gian chờ ước tính**: ETA phải được **tính từ 2 số đã hiển thị** (`vị trí ÷ tốc độ xả`), không được gán một con số độc lập không khớp phép chia — đây là lỗi đã phát hiện ở v1.0 (12,450 ÷ 1,200/phút ≈ 10 phút 22 giây, không phải một số tùy ý).
   * ⚠️ **Minh bạch với người dùng:** hiển thị dòng chú thích nhỏ: *"Vị trí có thể thay đổi theo chính sách ưu tiên người có công."* — vì M2 (Max-Heap theo `loyalty_score`) có thể khiến số thứ tự của một người tụt lùi so với thời điểm họ vào hàng theo `arrival_time` (M1). Không giải thích rõ sẽ tạo cảm giác hệ thống gian lận.

3. **Khu vực Chọn Ghế & Giữ Chỗ (Sector Selection & TTL Countdown):**
   * Khi đến lượt: chuông thông báo (xem lưu ý autoplay ở mục V.1) + chuyển màn hình giữ vé.
   * **Đồng hồ đếm ngược giữ vé:** giá trị khởi tạo lấy từ `expires_at` trả về bởi `POST /api/hold` (không hard-code 10:00). Đổi màu đỏ nhấp nháy khi còn dưới 2 phút.
   * **Sơ đồ khán đài tương tác (SVG Sector Map):** click chọn khu vực để xem ghế còn lại (`physical_cap - sold`) và giá vé.

4. **Vé Điện Tử Đẳng Cấp (Luxury Hologram E-Ticket):**
   * QR động, số ghế chuẩn (`Khán đài A - Cửa 3 - Hàng 12 - Ghế 08`), họ tên, dấu mộc điện tử.

5. **Cơ chế khôi phục phiên (bổ sung mới):** Lưu `queue_token` vào `localStorage`. Khi người dùng F5 hoặc mất kết nối, gọi lại `GET /api/queue/status/{user_id}` bằng token đã lưu để khôi phục đúng vị trí, tránh mất chỗ oan.

---

### GÓC NHÌN 2: TRUNG TÂM CHỈ HUY & ĐIỀU HÀNH THUẬT TOÁN (ADMIN COMMAND CENTER)

#### 1. Thanh chỉ số KPI Quốc Gia — tất cả lấy từ response `POST /api/pipeline/run`

> ⚠️ Sửa lỗi v1.0: tách rõ 2 chỉ số rủi ro khác nhau, không được gộp lẫn.

| KPI | Nguồn dữ liệu | Ghi chú |
|:---|:---|:---|
| Sức chứa Sân vận động ($C$) | `request.capacity_C` | Người dùng chọn |
| Hạn mức phát hành ($M^*$) | `response.m3.m_star` | **Runtime**, không hard-code |
| Tỷ lệ hủy/rớt $p(t)$ realtime | `response.m6.drop_rate` | Từ Sliding Window $\mathcal{O}(1)$ |
| Doanh thu thuần thực tế | `response.m7.proposed.net_revenue` | Runtime |
| Tăng trưởng so với bán cố định | `response.m7.growth_pct` | Runtime |
| **P(K > C)** *(xác suất có ít nhất 1 khách bị DB)* | `response.m3.prob_any_db` | So sánh trực tiếp với $\tau_0$ — đây là đại lượng mà thuật toán M3 thực sự ràng buộc |
| **Tỷ lệ khách bị từ chối kỳ vọng** *(E[(K−C)⁺]/M)* | `response.m7.proposed.db_rate` | Đại lượng khác — KHÔNG gộp chung với P(K>C) |
| Tỷ lệ khách chính sách bị ảnh hưởng | `response.m7.proposed.protected_group_db_rate` | Phải luôn = 0.00% (xem mục I.4) |

#### 2. Thanh điều khiển mô phỏng thực nghiệm (Simulation Controls)
* Dropdown Venue Preset (Mỹ Đình 40k / Arena 10k / NCC 3.8k) → set `capacity_C`.
* Sliders: Sức chứa $C$, Ngưỡng rủi ro $\tau_0$, Tỷ lệ rớt mạng $p$, Số kịch bản Monte Carlo $S$, và **`demand_limit` từng hạng vé** (bổ sung mới — để M4 DP thực sự có gì để tối ưu, xem mục I.3).
* Nút thao tác: `[ 🎲 Sinh N User mẫu ]`, `[ ▶️ Kích hoạt Pipeline M1→M7 ]`, `[ 🔄 Reset ]`. Mỗi nút gọi API tương ứng, hiển thị loading state + thời gian xử lý thật (`response.elapsed_ms`).

#### 3. Bộ 7 Tabs Trực Quan Hóa

* **Tab M1 — Merge Sort $\mathcal{O}(N\log N)$:** Trực quan hóa chia-để-trị theo batch (VD 5,000 user/batch); bảng trước/sau sắp xếp lấy mẫu 20 dòng, không render toàn bộ N dòng.
* **Tab M2 — Max-Heap $\mathcal{O}(K\log N)$:** Cây nhị phân Top-K theo `loyalty_score`; danh sách nhóm chính sách (Mẹ VNAH, Thương binh, Huân chương Lao động).
* **Tab M3 — Binary Search $\mathcal{O}(C\log(\text{limit}))$:** Biểu đồ CDF Nhị thức $K\sim\text{Binomial}(M,1-p)$; animation binary search co hẹp khoảng nghiệm dùng `response.m3.search_trace` (mảng các bước left/right/mid/prob thật, không tự vẽ tay).
* **Tab M4 — Bounded Knapsack DP $\mathcal{O}(N\cdot M^*)$:** Ma trận DP phân bổ $M^*$ cho 4 phân khu trong giới hạn `demand_limit`; hiển thị rõ `protected_pool` tách biệt.
* **Tab M5 — Greedy Heuristic $\mathcal{O}(K)$:** Mô phỏng cổng soát vé; khi $K>C$ → nâng hạng hoặc bồi thường 150%, **loại trừ nhóm chính sách khỏi diện xử lý này**.
* **Tab M6 — Sliding Window $\mathcal{O}(1)$ + Min-Heap TTL:** Line chart realtime $p(t)$ (dùng Canvas, ring buffer 300 điểm — xem mục IV); bảng vé sắp hết hạn dùng virtual scrolling.
* **Tab M7 — SAA Monte Carlo:** Bảng so sánh Proposed vs Baseline (toàn bộ số liệu từ `response.m7`), scatter chart 100 kịch bản.

---

## IV. KIẾN TRÚC HIỆU NĂNG FRONTEND (BẮT BUỘC — PHẦN BỔ SUNG MỚI)

> Sơ đồ SVG Sector (chỉ 4–20 block) **không phải** nút thắt cổ chai. Ba nút thắt thật sự:

| Nút thắt | Nguyên nhân | Giải pháp bắt buộc |
|:---|:---|:---|
| M7 Monte Carlo (100 kịch bản × O(C) mỗi kịch bản) | Hàng chục triệu phép tính CDF | Chạy **trên backend**, frontend chỉ poll trạng thái job + hiển thị progress bar |
| M1 Merge Sort 150,000+ user | Nếu lỡ chạy phía client sẽ block main thread | **Cấm chạy trên frontend** (xem mục 0). Nếu cần mô phỏng trực quan cho mục đích minh họa, giới hạn N mẫu ≤ 500 và chạy trong Web Worker |
| Danh sách hàng đợi 185,000+ dòng | Render full DOM sẽ sập trình duyệt | **Virtual scrolling** — chỉ render ~30 dòng trong viewport |

**Checklist kỹ thuật bắt buộc:**
1. Mọi animation cập nhật đồng bộ qua **một** `requestAnimationFrame` loop duy nhất — cấm nhiều `setInterval` rải rác cho từng widget.
2. Biểu đồ realtime $p(t)$ dùng **Canvas**, không dùng SVG (SVG tạo DOM node mới mỗi điểm dữ liệu).
3. Web Worker cho bất kỳ tính toán mô phỏng nào chạy phía client (nếu có), giữ main thread rảnh để vẽ UI.
4. Debounce 300ms cho mọi slider điều khiển tham số trước khi gọi API.
5. Giới hạn 5 bề mặt `backdrop-filter: blur()` hiển thị đồng thời (đã nêu ở mục II).

---

## V. CÁC KHOẢNG TRỐNG UX ĐÃ BỔ SUNG

1. **Autoplay audio bị chặn:** Trình duyệt chặn phát âm thanh tự động khi chưa có tương tác người dùng. Chuông "đến lượt" phải có nút xác nhận trước: `[🔔 Bật âm báo khi đến lượt]` ngay khi vào phòng chờ.
2. **Minh bạch thứ tự hàng đợi:** đã nêu ở mục III (số thứ tự có thể tụt lùi do ưu tiên chính sách).
3. **Khôi phục phiên khi mất kết nối/F5:** đã nêu ở mục III (dùng `queue_token`).
4. **`prefers-reduced-motion`:** toàn bộ hiệu ứng pulsing/glow phải có phương án tắt qua media query này — yêu cầu accessibility cơ bản.

---

## VI. HỢP ĐỒNG API (BỔ SUNG MỚI — BẮT BUỘC ĐỂ CODE NGAY KHÔNG CẦN HỎI LẠI)

### 1. Chạy toàn bộ pipeline M1→M7

```jsonc
// POST /api/pipeline/run
// Request
{
  "venue_preset": "my_dinh",        // my_dinh | arena | ncc
  "capacity_C": 40000,
  "tau_0": 0.05,
  "drop_rate_p": 0.18,              // null => lấy p(t) động từ M6
  "num_scenarios": 100,
  "num_users": 150000,
  "seed": 42,
  "demand_limits": {                // slider người vận hành chỉnh tay
    "VVIP": 5200, "PLATINUM": 13000, "GOLD": 20000, "SILVER": 12000
  },
  "protect_priority_groups": true   // Bắt buộc true cho sự kiện tri ân
}

// Response
{
  "run_id": "uuid",
  "elapsed_ms": { "m1": 312, "m2": 45, "m3": 84, "m4": 1205, "m5": 96, "m6": 12, "m7": 8940 },
  "m3": {
    "m_star": 48610,                          // giá trị THẬT từ binary search
    "overbooking_pct": 21.53,
    "prob_any_db": 0.0489,                    // P(K > C) — so với tau_0
    "search_trace": [
      { "step": 1, "left": 40000, "right": 80000, "mid": 60000, "prob": 0.9997, "feasible": false },
      { "step": 2, "left": 40000, "right": 60000, "mid": 50000, "prob": 0.31,   "feasible": true  }
    ]
  },
  "m4": {
    "allocation": {
      "VVIP":     { "qty": 4850, "price": 4500000, "physical_cap": 4000,  "demand_limit": 5200,  "protected_pool": 4000 },
      "PLATINUM": { "qty": 12100, "price": 2500000, "physical_cap": 10000, "demand_limit": 13000, "protected_pool": 0 }
    },
    "gross_revenue": 82740000000,
    "dp_table_sample": []                     // trích ~20x20 ô để render ma trận minh họa
  },
  "m7": {
    "proposed": {
      "net_revenue": 82650000000,
      "empty_seats_avg": 230,
      "prob_any_db": 0.0489,
      "db_rate": 0.0002,                      // E[(K-C)+]/M — KHÁC prob_any_db
      "protected_group_db_rate": 0.0           // luôn bằng 0
    },
    "baseline": { "net_revenue": 68200000000, "empty_seats_avg": 7200, "db_rate": 0.0 },
    "growth_pct": 21.19,
    "scenarios": [
      { "s": 1, "p": 0.174, "m_star": 48720, "net_revenue": 82910000000 }
    ]
  }
}
```

### 2. Trạng thái hàng đợi (polling)
```jsonc
// GET /api/queue/status/{user_id}
{
  "position": 12450,
  "total_waiting": 185420,
  "release_rate_per_min": 1200,
  "eta_seconds": 622,               // = position / release_rate_per_min * 60, tính từ backend
  "priority_group": "Thương binh",
  "priority_score": 96,
  "queue_token": "opaque-string"    // lưu vào localStorage để khôi phục phiên
}
```

### 3. Giữ chỗ (TTL Hold)
```jsonc
// POST /api/hold
// Request: { "user_id": "...", "sector": "GOLD", "seat_count": 2 }
// Response
{
  "hold_id": "uuid",
  "expires_at": "2026-06-09T20:15:00Z",   // frontend dùng để khởi tạo countdown, không hard-code 10:00
  "seats": ["B-12-08", "B-12-09"]
}
```

### 4. Check-in tại cổng
```jsonc
// POST /api/checkin
// Response
{
  "status": "SUCCESS",   // SUCCESS | UPGRADED | DENIED_COMPENSATED
  "upgraded_to": null,   // sector mới nếu status = UPGRADED
  "compensation_amount": null  // 150% giá vé nếu DENIED_COMPENSATED
}
```

---

## VII. TIÊU CHUẨN ĐẦU RA (DEFINITION OF DONE — v2.0)

1. Hiển thị đúng tầm vóc Concert Quốc Gia (3,800–40,000 ghế, hàng chục tỷ đồng, hàng trăm nghìn người chờ) — **mọi con số là runtime, không hard-code**.
2. Sơ đồ khán đài Sector/Block mượt, không giật lag; tuân thủ giới hạn hiệu năng ở Mục IV.
3. Đầy đủ 2 góc nhìn: Citizen Portal + Command Center.
4. Trực quan hóa cả 7 module, mỗi tab dùng dữ liệu thật từ `response` API, không tự vẽ số liệu minh họa cố định.
5. Nhóm chính sách tri ân được bảo vệ tuyệt đối khỏi Denied Boarding (Mục I.4), hiển thị công khai như cam kết đạo đức.
6. Toàn bộ mã màu đạt WCAG AAA (Mục II), có phương án `prefers-reduced-motion`.
7. Hợp đồng API đầy đủ (Mục VI) — lập trình viên/AI Agent có thể code ngay không cần hỏi lại.
8. Code sạch, HTML5/CSS3/JS ES6+, tương thích FastAPI `server.py`.
