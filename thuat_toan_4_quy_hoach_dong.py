
def quy_hoach_dong_phan_bo_ve(M_star, danh_sach_hang_ve):

    # =====================================================
    # 1. KIỂM TRA INPUT
    # =====================================================
    if not isinstance(M_star, int) or isinstance(M_star, bool) or M_star < 0:
        raise ValueError("M_star phai la so nguyen khong am.")

    if not isinstance(danh_sach_hang_ve, list) or not danh_sach_hang_ve:
        raise ValueError("danh_sach_hang_ve phai la list va khong rong.")

    for hang_ve in danh_sach_hang_ve:

        if not isinstance(hang_ve, dict):
            raise ValueError("Moi hang ve phai la dict.")

        if not all(x in hang_ve for x in ["name", "price", "demand_limit"]):
            raise ValueError("Thieu thong tin hang ve.")

        if not isinstance(hang_ve["price"], (int, float)):
            raise ValueError("price phai la so.")

        if isinstance(hang_ve["price"], bool):
            raise ValueError("price phai la so.")

        if not isinstance(hang_ve["demand_limit"], int):
            raise ValueError("demand_limit phai la so nguyen.")

        if isinstance(hang_ve["demand_limit"], bool):
            raise ValueError("demand_limit phai la so nguyen.")

        if hang_ve["price"] < 0 or hang_ve["demand_limit"] < 0:
            raise ValueError(
                "price va demand_limit khong duoc am."
            )

    # =====================================================
    # 2. KHỞI TẠO DP VÀ TRACE
    # =====================================================
    N = len(danh_sach_hang_ve)

    # dp[i][j]:
    # Doanh thu lon nhat khi dung i hang ve
    # voi j ve duoc phan bo.
    dp = [[0] * (M_star + 1) for _ in range(N + 1)]

    # trace[i][j]:
    # So luong hang ve thu i duoc chon tai trang thai (i, j).
    trace = [[0] * (M_star + 1) for _ in range(N + 1)]

    # =====================================================
    # 3. BOUNDED KNAPSACK DP
    # =====================================================
    for i in range(1, N + 1):

        price = danh_sach_hang_ve[i - 1]["price"]
        limit = danh_sach_hang_ve[i - 1]["demand_limit"]

        for j in range(M_star + 1):

            # x = so luong hang ve i duoc chon
            for x in range(min(limit, j) + 1):

                value = dp[i - 1][j - x] + x * price

                if value > dp[i][j]:
                    dp[i][j] = value
                    trace[i][j] = x

    # =====================================================
    # 4. TÌM DOANH THU TỐI ĐA
    # =====================================================
    best_j = 0

    for j in range(1, M_star + 1):

        if dp[N][j] > dp[N][best_j]:
            best_j = j

    # =====================================================
    # 5. TRACE-BACK
    # =====================================================
    allocation = {}
    j = best_j

    for i in range(N, 0, -1):

        name = danh_sach_hang_ve[i - 1]["name"]

        allocation[name] = trace[i][j]

        j -= trace[i][j]

    return allocation


# =====================================================
# TÍNH DOANH THU
# =====================================================
def tinh_doanh_thu(allocation, danh_sach_hang_ve):

    doanh_thu = 0

    for hang_ve in danh_sach_hang_ve:

        name = hang_ve["name"]

        doanh_thu += (
            allocation[name] * hang_ve["price"]
        )

    return doanh_thu


# =====================================================
# KIỂM TRA ALLOCATION
# =====================================================
def kiem_tra_allocation(
    allocation,
    M_star,
    danh_sach_hang_ve
):

    # Không được phân bổ vượt M_star
    if sum(allocation.values()) > M_star:
        return False

    for hang_ve in danh_sach_hang_ve:

        name = hang_ve["name"]

        # Không được phân bổ số lượng âm
        if allocation[name] < 0:
            return False

        # Không được vượt nhu cầu
        if allocation[name] > hang_ve["demand_limit"]:
            return False

    return True


# =====================================================
# CHẠY THỬ MODULE M4
# =====================================================
if __name__ == "__main__":
    M_star = 116
    danh_sach_hang_ve = [
        {
            "name": "VIP",
            "price": 1000000,
            "demand_limit": 30
        },
        {
            "name": "Standard",
            "price": 500000,
            "demand_limit": 100
        }
    ]

    allocation = quy_hoach_dong_phan_bo_ve(
        M_star,
        danh_sach_hang_ve
    )

    doanh_thu = tinh_doanh_thu(
        allocation,
        danh_sach_hang_ve
    )

    print("M_star = 116 nhan tu M3")
    print("VIP =", allocation["VIP"])
    print("Standard =", allocation["Standard"])
    print("Tong =", sum(allocation.values()), ", khong vuot M_star")
    print("Doanh thu toi da =", doanh_thu, "VND")
    print(
        "Allocation hop le =",
        kiem_tra_allocation(allocation, M_star, danh_sach_hang_ve)
    )