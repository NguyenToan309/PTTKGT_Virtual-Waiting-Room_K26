from thuat_toan_5_tham_lam_xung_dot import xu_ly_xung_dot_tham_lam


def test_case_1_luong_chuan_va_free_upgrade():
    print("--- TEST CASE 1: Luồng chuẩn, Free Upgrade & Chạm trần C ---")
    ds_khach = [
        {"id_khach": "KH01", "ten": "Dũng", "hang_ve_mong_muon": "Standard"},
        {"id_khach": "KH02", "ten": "Bình", "hang_ve_mong_muon": "Standard"},
        {"id_khach": "KH03", "ten": "Châu", "hang_ve_mong_muon": "VIP"},
    ]
    allocation = {"VIP": 2, "Standard": 1, "Economy": 0}
    C = 2

    kq = xu_ly_xung_dot_tham_lam(ds_khach, allocation, C)

    assert kq[0]["trang_thai"] == "SUCCESS"
    assert kq[1]["trang_thai"] == "UPGRADED"
    assert kq[1]["hang_ve_thuc_nhan"] == "VIP"
    assert kq[2]["trang_thai"] == "REJECTED_FULL"
    print("[PASS] Test case 1 thành công!\n")


def test_case_2_het_quota_khong_the_upgrade():
    print("--- TEST CASE 2: Hết Quota VIP & Không thể Upgrade cho VIP ---")
    ds_khach = [
        {"id_khach": "KH01", "ten": "An", "hang_ve_mong_muon": "VIP"},
        {"id_khach": "KH02", "ten": "Bảo", "hang_ve_mong_muon": "VIP"},
    ]
    allocation = {"VIP": 1, "Standard": 5, "Economy": 5}
    C = 10

    kq = xu_ly_xung_dot_tham_lam(ds_khach, allocation, C)

    assert kq[0]["trang_thai"] == "SUCCESS"
    assert kq[1]["trang_thai"] == "REJECTED_NO_QUOTA"
    assert kq[1]["boi_thuong"] is True
    print("[PASS] Test case 2 thành công!\n")


def test_case_3_suc_chua_bang_khong():
    print("--- TEST CASE 3: Sức chứa C = 0 (Hệ thống quá tải) ---")
    ds_khach = [
        {"id_khach": "KH01", "ten": "Cường", "hang_ve_mong_muon": "Economy"},
    ]
    allocation = {"VIP": 5, "Standard": 5, "Economy": 5}
    C = 0

    kq = xu_ly_xung_dot_tham_lam(ds_khach, allocation, C)

    assert len(kq) == 1
    assert kq[0]["trang_thai"] == "REJECTED_FULL"
    assert kq[0]["boi_thuong"] is True
    print("[PASS] Test case 3 thành công!\n")


def test_case_4_danh_sach_khach_rong():
    print("--- TEST CASE 4: Danh sách đầu vào rỗng ---")
    ds_khach = []
    allocation = {"VIP": 10, "Standard": 10, "Economy": 10}
    C = 50

    kq = xu_ly_xung_dot_tham_lam(ds_khach, allocation, C)

    assert len(kq) == 0
    print("[PASS] Test case 4 thành công!\n")


def test_case_5_upgrade_nhieu_cap():
    print("--- TEST CASE 5: Upgrade từ Economy lên thẳng VIP ---")
    ds_khach = [
        {"id_khach": "KH01", "ten": "Đạt", "hang_ve_mong_muon": "Economy"},
    ]
    allocation = {"VIP": 1, "Standard": 0, "Economy": 0}
    C = 5

    kq = xu_ly_xung_dot_tham_lam(ds_khach, allocation, C)

    assert kq[0]["trang_thai"] == "UPGRADED"
    assert kq[0]["hang_ve_thuc_nhan"] == "VIP"
    print("[PASS] Test case 5 thành công!\n")


def test_case_6_bon_hang_ghe_va_khach_chinh_sach():
    print("--- TEST CASE 6: Cơ cấu 4 hạng ghế và bảo vệ 100% khách chính sách tri ân ---")
    ds_khach = [
        {"id_khach": "KH_VNAH", "ten": "Mẹ VNAH Nguyễn Thị Thứ", "hang_ve_mong_muon": "VVIP Tri Ân", "is_protected": True},
        {"id_khach": "KH_PLAT", "ten": "Khách Platinum", "hang_ve_mong_muon": "VIP Platinum"},
        {"id_khach": "KH_GOLD", "ten": "Khách Gold", "hang_ve_mong_muon": "Gold Standard"},
        {"id_khach": "KH_SILV", "ten": "Khách Silver nâng hạng", "hang_ve_mong_muon": "Silver Economy"},
        {"id_khach": "KH_OVER", "ten": "Khách Silver quá tải", "hang_ve_mong_muon": "Silver Economy"},
    ]
    # Khoang Gold còn trống 1 chỗ, Silver hết, Platinum còn 1 chỗ, VVIP còn 1 chỗ
    allocation = {"VVIP Tri Ân": 1, "VIP Platinum": 1, "Gold Standard": 1, "Silver Economy": 0}
    C = 3  # Sức chứa thực tế C = 3 ghế

    kq = xu_ly_xung_dot_tham_lam(ds_khach, allocation, C)

    # 1. Khách chính sách Mẹ VNAH được bảo vệ 100%
    assert kq[0]["trang_thai"] == "SUCCESS"
    assert kq[0]["hang_ve_thuc_nhan"] == "VVIP Tri Ân"

    # 2. Khách Platinum nhận đúng vé
    assert kq[1]["trang_thai"] == "SUCCESS"
    assert kq[1]["hang_ve_thuc_nhan"] == "VIP Platinum"

    # 3. Khách Gold nhận đúng vé
    assert kq[2]["trang_thai"] == "SUCCESS"
    assert kq[2]["hang_ve_thuc_nhan"] == "Gold Standard"

    # 4. Đến khách thứ 4, hệ thống đã đạt sức chứa thực C=3 -> chạm trần REJECTED_FULL
    assert kq[3]["trang_thai"] == "REJECTED_FULL"
    assert kq[3]["boi_thuong"] is True

    print("[PASS] Test case 6 thành công!\n")


def run_all_tests():
    test_case_1_luong_chuan_va_free_upgrade()
    test_case_2_het_quota_khong_the_upgrade()
    test_case_3_suc_chua_bang_khong()
    test_case_4_danh_sach_khach_rong()
    test_case_5_upgrade_nhieu_cap()
    test_case_6_bon_hang_ghe_va_khach_chinh_sach()
    print("=======================================================")
    print("[ALL PASS] TOÀN BỘ 6 UNIT TEST CASES ĐÃ VƯỢT QUA!")
    print("=======================================================")


if __name__ == "__main__":
    run_all_tests()
