---
name: vwr-algorithm-guide
description: Hướng dẫn chi tiết cách cài đặt 7 thuật toán lõi bằng tay cho dự án Virtual Waiting Room. Kích hoạt khi thành viên cần trợ giúp viết thuật toán cụ thể (Merge Sort, Max-Heap, Binary Search, Bounded Knapsack DP, Greedy, Min-Heap, Sliding Window, SAA Monte Carlo).
---

# SKILL: VWR Algorithm Implementation Guide

## MỤC ĐÍCH
Hướng dẫn từng bước cài đặt thủ công 7 thuật toán lõi, không dùng thư viện có sẵn.

---

## 1. MERGE SORT (M1) — Chia để trị

### Ý tưởng
- Chia mảng thành 2 nửa bằng nhau (Divide)
- Đệ quy sắp xếp từng nửa
- Trộn 2 nửa đã sắp xếp thành 1 mảng có thứ tự (Conquer)

### Pseudo-code
```
function merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

function merge(left, right):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if left[i].arrival_time <= right[j].arrival_time:  # <= để stable sort
            result.append(left[i]); i++
        else:
            result.append(right[j]); j++
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### Complexity: O(N log N) time, O(N) space
### Lưu ý: Dùng `<=` (không phải `<`) để đảm bảo stable sort

---

## 2. MAX-HEAP (M2) — Hàng đợi ưu tiên

### Ý tưởng
- Biểu diễn cây nhị phân hoàn chỉnh bằng mảng 1D
- Node cha ở index `(i-1)//2`, con trái `2i+1`, con phải `2i+2`
- Max-Heap: giá trị cha luôn >= con

### Thao tác cốt lõi

```
function sift_up(heap, index):
    parent = (index - 1) // 2
    while index > 0 and heap[index].loyalty_score > heap[parent].loyalty_score:
        swap(heap[index], heap[parent])
        index = parent
        parent = (index - 1) // 2

function sift_down(heap, index):
    n = len(heap)
    largest = index
    left = 2 * index + 1
    right = 2 * index + 2
    if left < n and heap[left] > heap[largest]: largest = left
    if right < n and heap[right] > heap[largest]: largest = right
    if largest != index:
        swap(heap[index], heap[largest])
        sift_down(heap, largest)

function build_max_heap(arr):
    # Heapify từ dưới lên — O(N)
    for i from (len(arr)//2 - 1) down to 0:
        sift_down(arr, i)

function extract_top_k(heap, k):
    result = []
    for _ in range(min(k, len(heap))):
        # Swap root với phần tử cuối, pop cuối, sift_down root
        swap(heap[0], heap[-1])
        result.append(heap.pop())
        sift_down(heap, 0)
    return result
```

### Complexity: Build O(N), Extract-top-k O(k log N) → Tổng O(N + k log N)

---

## 3. BINARY SEARCH + BINOMIAL CDF (M3) — Tìm M* an toàn

### Ý tưởng
- Tìm M* lớn nhất trong [C, 3C] sao cho P(K > C) ≤ τ₀
- K ~ Binomial(M, 1-p): số khách thực sự đến
- Dùng Binary Search trên answer space

### Tính Binomial CDF bằng tay (KHÔNG dùng scipy)

```
function binomial_cdf(M, C, p):
    """P(K <= C) = Σ_{k=0}^{C} C(M,k) * (1-p)^k * p^(M-k)"""
    q = 1 - p  # xác suất đến
    # Dùng công thức quy nạp tỷ số để tránh overflow
    # P(K=0) = p^M
    term = p ** M
    cumulative = term
    for k in range(1, C + 1):
        # P(K=k) / P(K=k-1) = (M-k+1)/k * q/p
        term *= (M - k + 1) / k * q / p
        cumulative += term
        if cumulative >= 1.0:
            return 1.0
    return cumulative

function risk(M, C, p):
    return 1.0 - binomial_cdf(M, C, p)

function binary_search_m_star(C, tau_0, p):
    left, right = C, 3 * C
    answer = C
    while left <= right:
        mid = (left + right) // 2
        if risk(mid, C, p) <= tau_0:
            answer = mid
            left = mid + 1
        else:
            right = mid - 1
    return answer
```

### Complexity: O(C × log(2C)) time, O(1) space
### Lưu ý: Dùng quy nạp tỷ số term *= ratio để tránh tính tổ hợp lớn gây overflow

---

## 4. BOUNDED KNAPSACK DP (M4) — Phân bổ vé tối ưu

### Ý tưởng
- Capacity = M*
- Items: các hạng vé (VIP, Standard, ...), mỗi hạng có price và demand_limit
- Tìm phân bổ tối đa hóa doanh thu

### Cấu trúc bảng DP

```
dp[i][j] = doanh thu tối đa khi xét i loại vé đầu tiên với j quota
trace[i][j] = số vé loại i được chọn tại trạng thái (i, j)

Khởi tạo: dp[0][0] = 0, dp[0][j!=0] = -∞

Chuyển trạng thái:
for i = 1 to N:            # N loại vé
    for j = 0 to M*:       # quota hiện tại
        for x = 0 to min(j, demand_limit[i]):  # số vé loại i
            if dp[i-1][j-x] + x * price[i] > dp[i][j]:
                dp[i][j] = dp[i-1][j-x] + x * price[i]
                trace[i][j] = x

Truy vết:
j = argmax(dp[N][j])
for i = N down to 1:
    allocation[i] = trace[i][j]
    j -= trace[i][j]
```

### Complexity: O(Types × M* × max_demand) time, O(Types × M*) space
### Tối ưu: Có thể dùng monotonic deque (deque từ collections) để giảm xuống O(Types × M*)

---

## 5. GREEDY HEURISTIC (M5) — Xử lý xung đột

### Ý tưởng
- Duyệt tuần tự danh sách khách check-in
- Ưu tiên 1: Cấp đúng hạng vé mong muốn nếu còn quota
- Ưu tiên 2: Nếu hết hạng Standard, nâng lên VIP nếu còn ghế VIP trống
- Ưu tiên 3: Nếu hết sạch tất cả, đền bù tiền mặt
- Ràng buộc cứng: tổng vé cấp ≤ C (sức chứa vật lý)

### Pseudo-code
```
function greedy_resolve(users, seats):
    total_issued = 0
    revenue = 0
    log = []
    for user in users:
        if total_issued >= C:
            log.append({user, status="COMPENSATED", compensation=...})
            continue
        if seats[user.ticket_type] > 0:
            seats[user.ticket_type] -= 1
            total_issued += 1
            revenue += price[user.ticket_type]
            log.append({user, status="CHECKED_IN"})
        elif user.ticket_type == "STANDARD" and seats["VIP"] > 0:
            seats["VIP"] -= 1
            total_issued += 1
            revenue += price["VIP"]
            log.append({user, status="UPGRADED"})
        else:
            log.append({user, status="COMPENSATED"})
    return revenue, log
```

---

## 6. MIN-HEAP + SLIDING WINDOW (M6)

### Min-Heap (quản lý vé timeout)

Giống Max-Heap nhưng đảo chiều so sánh: node cha ≤ con.
```
function sift_up_min(heap, index):
    parent = (index - 1) // 2
    while index > 0 and heap[index].expire_time < heap[parent].expire_time:
        swap(heap[index], heap[parent])
        index = parent
        parent = (index - 1) // 2
```

### Sliding Window O(1) (tính tỷ lệ rớt)

```
class SlidingWindow:
    window = deque()      # Lưu trạng thái (0/1) của W giao dịch gần nhất
    drop_count = 0        # Biến tích lũy đếm số giao dịch rớt
    W = 100               # Kích thước cửa sổ

    function update(is_dropped: bool):
        window.append(1 if is_dropped else 0)
        if is_dropped: drop_count += 1
        if len(window) > W:
            old = window.popleft()
            if old == 1: drop_count -= 1

    function get_rate() -> float:
        if len(window) == 0: return 0.0
        return drop_count / len(window)    # O(1), KHÔNG dùng sum()
```

---

## 7. SAA MONTE CARLO (M7) — Sample Average Approximation

### Ý tưởng
1. Sinh S kịch bản: p₁, p₂, ..., pₛ từ phân phối ngẫu nhiên (ví dụ: Uniform[0.1, 0.3])
2. Với mỗi pᵢ: gọi M3 → M4 → M5 để tính doanh thu Rᵢ
3. Nghiệm SAA: M* = argmax Σ Rᵢ / S
4. So sánh với Baseline (Fixed M = C)

### Pseudo-code
```
function saa_evaluate(S, C, tau_0):
    proposed_revenues = []
    baseline_revenues = []
    for i in range(S):
        p_i = random_uniform(0.1, 0.3)
        # Proposed: dùng M3 + M4 + M5
        m_star = binary_search(C, tau_0, p_i)
        allocation = knapsack(m_star, ...)
        revenue_proposed = simulate_checkin(allocation, p_i, C)
        # Baseline: bán đúng C vé
        revenue_baseline = simulate_checkin({C vé}, p_i, C)
        proposed_revenues.append(revenue_proposed)
        baseline_revenues.append(revenue_baseline)
    return {
        "proposed_avg": sum(proposed_revenues) / S,
        "baseline_avg": sum(baseline_revenues) / S,
        "improvement": ...
    }
```
