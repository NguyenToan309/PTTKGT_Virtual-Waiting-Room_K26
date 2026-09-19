from thuat_toan_4_quy_hoach_dong import (
    quy_hoach_dong_phan_bo_ve,
    tinh_doanh_thu,
    kiem_tra_allocation
)


# =====================================================
# TEST 1: NHẬN M_STAR TỪ M3 VÀ TỐI ƯU DOANH THU
# =====================================================
def test_nhan_m_star_tu_m3():

    # M3 trả về M_star = 116
    M_star = 116

    danh_sach_hang_ve = [
        {"name": "VIP", "price": 1000000, "demand_limit": 30},
        {"name": "Standard", "price": 500000, "demand_limit": 100}
    ]

    allocation = quy_hoach_dong_phan_bo_ve(
        M_star,
        danh_sach_hang_ve
    )

    assert allocation["VIP"] == 30
    assert allocation["Standard"] == 86

    assert sum(allocation.values()) == M_star

    assert tinh_doanh_thu(
        allocation,
        danh_sach_hang_ve
    ) == 73000000


# =====================================================
# TEST 2: TRACE-BACK ĐÚNG
# =====================================================
def test_trace_back():

    M_star = 10

    danh_sach_hang_ve = [
        {"name": "VIP", "price": 2000000, "demand_limit": 3},
        {"name": "Standard", "price": 500000, "demand_limit": 10}
    ]

    allocation = quy_hoach_dong_phan_bo_ve(
        M_star,
        danh_sach_hang_ve
    )

    assert allocation["VIP"] == 3
    assert allocation["Standard"] == 7

    assert sum(allocation.values()) == M_star


# =====================================================
# TEST 3: KHÔNG VƯỢT M_STAR
# =====================================================
def test_khong_vuot_m_star():

    M_star = 50

    danh_sach_hang_ve = [
        {"name": "VIP", "price": 1000000, "demand_limit": 40},
        {"name": "Standard", "price": 500000, "demand_limit": 40}
    ]

    allocation = quy_hoach_dong_phan_bo_ve(
        M_star,
        danh_sach_hang_ve
    )

    assert sum(allocation.values()) <= M_star

    assert kiem_tra_allocation(
        allocation,
        M_star,
        danh_sach_hang_ve
    )


# =====================================================
# TEST 4: KHÔNG VƯỢT NHU CẦU
# =====================================================
def test_khong_vuot_demand():

    M_star = 100

    danh_sach_hang_ve = [
        {"name": "VIP", "price": 1000000, "demand_limit": 20},
        {"name": "Standard", "price": 500000, "demand_limit": 30}
    ]

    allocation = quy_hoach_dong_phan_bo_ve(
        M_star,
        danh_sach_hang_ve
    )

    assert allocation["VIP"] <= 20
    assert allocation["Standard"] <= 30

    assert kiem_tra_allocation(
        allocation,
        M_star,
        danh_sach_hang_ve
    )