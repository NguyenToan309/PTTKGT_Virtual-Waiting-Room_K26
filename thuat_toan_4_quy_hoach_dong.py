from collections import deque

def quy_hoach_dong_phan_bo_ve(M_star, danh_sach_hang_ve):

    # =====================================================
    # 1. KIỂM TRA INPUT
    # =====================================================
    if not isinstance(M_star, int) or M_star < 0:
        raise ValueError("M_star phai la so nguyen khong am.")

    if not isinstance(danh_sach_hang_ve, list):
        raise ValueError("danh_sach_hang_ve phai la list.")

    if not danh_sach_hang_ve:
        return {}

    for hang_ve in danh_sach_hang_ve:
        if not all(x in hang_ve for x in ["name", "price", "demand_limit"]):
            raise ValueError("Thieu thong tin hang ve.")

        if not isinstance(hang_ve["price"], (int, float)):
            raise ValueError("price phai la so.")

        if not isinstance(hang_ve["demand_limit"], int):
            raise ValueError("demand_limit phai la so nguyen.")

        if hang_ve["price"] < 0 or hang_ve["demand_limit"] < 0:
            raise ValueError("price va demand_limit khong duoc am.")

    # =====================================================
    # 2. XỬ LÝ NHÓM CHÍNH SÁCH TRI ÂN (GIÁ 0 Đ / PROTECTED POOL)
    # =====================================================
    # Các hạng vé chính sách (VVIP Tri Ân cho Mẹ VNAH, Cựu chiến binh, Thương binh, Yếu nhân)
    # được bảo vệ 100% chỉ tiêu trước, không đưa vào Knapsack cạnh tranh giá.
    allocation = {}
    remain_M = M_star

    danh_sach_thuong_mai = []
    for hang_ve in danh_sach_hang_ve:
        name = hang_ve["name"]
        price = hang_ve["price"]
        limit = hang_ve["demand_limit"]
        is_protected = (
            price == 0.0 
            or hang_ve.get("protected_pool", 0) > 0 
            or "Tri Ân" in name 
            or name.startswith("VVIP")
        )
        if is_protected:
            allocated_vvip = min(remain_M, limit)
            allocation[name] = allocated_vvip
            remain_M -= allocated_vvip
        else:
            danh_sach_thuong_mai.append(hang_ve)

    if not danh_sach_thuong_mai or remain_M <= 0:
        for hang_ve in danh_sach_thuong_mai:
            allocation[hang_ve["name"]] = 0
        return {hang_ve["name"]: allocation[hang_ve["name"]] for hang_ve in danh_sach_hang_ve}

    # =====================================================
    # 3. KHỞI TẠO DP VÀ TRACE CHO CÁC HẠNG VÉ THƯƠNG MẠI
    # =====================================================
    N = len(danh_sach_thuong_mai)
    INF = float("-inf")

    dp = [[INF] * (remain_M + 1) for _ in range(N + 1)]
    trace = [[0] * (remain_M + 1) for _ in range(N + 1)]

    dp[0][0] = 0

    # =====================================================
    # 4. BOUNDED KNAPSACK DP (HÀNG ĐỢI ĐƠN ĐIỆU DEQUE)
    # =====================================================
    for i in range(1, N + 1):
        price = danh_sach_thuong_mai[i - 1]["price"]
        limit = danh_sach_thuong_mai[i - 1]["demand_limit"]

        q = deque()

        for j in range(remain_M + 1):

            min_k = max(0, j - limit)

            while q and q[0] < min_k:
                q.popleft()

            if dp[i - 1][j] != INF:
                value = dp[i - 1][j] - j * price

                while q:
                    last = q[-1]
                    last_value = dp[i - 1][last] - last * price

                    if last_value <= value:
                        q.pop()
                    else:
                        break

                q.append(j)

            if q:
                k = q[0]
                dp[i][j] = dp[i - 1][k] + (j - k) * price
                trace[i][j] = j - k

    # =====================================================
    # 5. TÌM DOANH THU TỐI ĐA TRÊN TẬP THƯƠNG MẠI
    # =====================================================
    best_j = 0

    for j in range(1, remain_M + 1):
        if dp[N][j] > dp[N][best_j]:
            best_j = j

    # =====================================================
    # 6. TRACE-BACK VÀ HỢP NHẤT PHÂN BỔ
    # =====================================================
    j = best_j

    for i in range(N, 0, -1):
        name = danh_sach_thuong_mai[i - 1]["name"]
        selected = trace[i][j]

        allocation[name] = selected
        j -= selected

    return {
        hang_ve["name"]: allocation[hang_ve["name"]]
        for hang_ve in danh_sach_hang_ve
    }

# =====================================================
# TÍNH DOANH THU
# =====================================================
def tinh_doanh_thu(allocation, danh_sach_hang_ve):

    gia = {
        hang_ve["name"]: hang_ve["price"]
        for hang_ve in danh_sach_hang_ve
    }

    return sum(
        allocation[name] * gia[name]
        for name in allocation
    )

# =====================================================
# KIỂM TRA ALLOCATION
# =====================================================
def kiem_tra_allocation(allocation, M_star, danh_sach_hang_ve):

    if sum(allocation.values()) > M_star:
        return False
    
    for hang_ve in danh_sach_hang_ve:
        name = hang_ve["name"]
        quantity = allocation.get(name, 0)
        if quantity < 0:
            return False
        
        if quantity > hang_ve["demand_limit"]:
            return False
    return True

# =====================================================
# UNIT TEST
# =====================================================
def unit_test():

    tests = [
        (
            100,
            [
                {"name": "VIP", "price": 1000000, "demand_limit": 30},
                {"name": "Standard", "price": 500000, "demand_limit": 100}
            ],
            {"VIP": 30, "Standard": 70}
        ),

        (
            50,
            [
                {"name": "VIP", "price": 1000000, "demand_limit": 20},
                {"name": "Standard", "price": 500000, "demand_limit": 20}
            ],
            {"VIP": 20, "Standard": 20}
        ),

        (
            10,
            [
                {"name": "VIP", "price": 2000000, "demand_limit": 3},
                {"name": "Standard", "price": 500000, "demand_limit": 10}
            ],
            {"VIP": 3, "Standard": 7}
        ),

        (
            10,
            [
                {"name": "VIP", "price": 1000000, "demand_limit": 2}
            ],
            {"VIP": 2}
        ),

        (
            120,
            [
                {"name": "VVIP Tri Ân", "price": 0, "demand_limit": 15, "protected_pool": 15},
                {"name": "VIP Platinum", "price": 2500000, "demand_limit": 35},
                {"name": "Gold Standard", "price": 1200000, "demand_limit": 50},
                {"name": "Silver Economy", "price": 600000, "demand_limit": 35}
            ],
            {"VVIP Tri Ân": 15, "VIP Platinum": 35, "Gold Standard": 50, "Silver Economy": 20}
        )
    ]

    for i, (M_star, hang_ve, expected) in enumerate(tests, 1):
        result = quy_hoach_dong_phan_bo_ve(M_star, hang_ve)
        assert result == expected
        assert kiem_tra_allocation(
            result, M_star, hang_ve
        )

        print(f"TEST {i} PASSED")

# =====================================================
# DEMO
# =====================================================
if __name__ == "__main__":
    unit_test()
    M_star = 121683
    danh_sach_hang_ve = [
        {"name": "VVIP Tri Ân", "price": 0.0, "demand_limit": 15000, "protected_pool": 15000},
        {"name": "VIP Platinum", "price": 2500000.0, "demand_limit": 35000},
        {"name": "Gold Standard", "price": 1200000.0, "demand_limit": 50000},
        {"name": "Silver Economy", "price": 600000.0, "demand_limit": 35000}
    ]

    allocation = quy_hoach_dong_phan_bo_ve(M_star, danh_sach_hang_ve)
    print("\nM_star (Hạn mức bán lố):", M_star)
    print("Phân bổ 4 hạng vé:", allocation)
    print("Tổng vé phát hành:", sum(allocation.values()))

    doanh_thu = tinh_doanh_thu(allocation, danh_sach_hang_ve)
    print("Doanh thu kỳ vọng:", f"{doanh_thu:,.0f} VND")
    print("Hợp lệ hạn mức:", kiem_tra_allocation(allocation, M_star, danh_sach_hang_ve))