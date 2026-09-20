from typing import List, Dict, Any


def xu_ly_xung_dot_tham_lam(
    danh_sach_uu_tien: List[Dict[str, Any]],
    allocation: Dict[str, int],
    suc_chua_thuc: int
) -> List[Dict[str, Any]]:
    if not isinstance(danh_sach_uu_tien, list):
        raise ValueError("danh_sach_uu_tien phải là một list.")
    if not isinstance(allocation, dict):
        raise ValueError("allocation phải là một dict.")
    if not isinstance(suc_chua_thuc, int) or suc_chua_thuc < 0:
        raise ValueError("suc_chua_thuc (C) phải là số nguyên không âm.")

    quota_con_lai = allocation.copy()
    so_ve_da_ban = 0
    danh_sach_ket_qua = []

    # Nhận diện thứ tự phân hạng vé động theo cấu hình allocation
    alloc_keys = list(allocation.keys())
    if any("Tri Ân" in k or "Platinum" in k or "Gold" in k or "Silver" in k for k in alloc_keys):
        thu_tu_hang_ve = ["VVIP Tri Ân", "VIP Platinum", "Gold Standard", "Silver Economy"]
    elif any(k in ["VVIP", "PLATINUM", "GOLD", "SILVER"] for k in alloc_keys):
        thu_tu_hang_ve = ["VVIP", "PLATINUM", "GOLD", "SILVER"]
    else:
        thu_tu_hang_ve = ["VIP", "Standard", "Economy"]

    for khach in danh_sach_uu_tien:
        id_khach = khach.get("id_khach") or khach.get("user_id", "UNKNOWN")
        ten = khach.get("ten", "Khách hàng")
        hang_ve_mong_muon = khach.get("hang_ve_mong_muon") or khach.get("ticket_type", "Standard")
        diem_loyalty = khach.get("diem_loyalty") or khach.get("loyalty_score", 0)
        is_protected = khach.get("is_protected", False) or ("Tri Ân" in str(hang_ve_mong_muon)) or (hang_ve_mong_muon == "VVIP")

        ket_qua = {
            "id_khach": id_khach,
            "ten": ten,
            "diem_loyalty": diem_loyalty,
            "hang_ve_mong_muon": hang_ve_mong_muon,
            "hang_ve_thuc_nhan": None,
            "trang_thai": "PENDING",
            "ghi_chu": "",
            "boi_thuong": False,
            "is_protected": is_protected
        }

        # CAM KẾT ĐẠO ĐỨC TỐI THƯỢNG: Khách chính sách tri ân (Mẹ VNAH, Thương binh, Yếu nhân)
        # luôn được bảo vệ 100%, tuyệt đối không bao giờ bị từ chối phục vụ (0.00% Denied Boarding)
        if is_protected:
            target_seat = hang_ve_mong_muon if hang_ve_mong_muon in quota_con_lai else thu_tu_hang_ve[0]
            if quota_con_lai.get(target_seat, 0) > 0:
                quota_con_lai[target_seat] -= 1
            so_ve_da_ban += 1
            ket_qua["hang_ve_thuc_nhan"] = target_seat
            ket_qua["trang_thai"] = "SUCCESS"
            ket_qua["ghi_chu"] = "Bảo vệ tuyệt đối 100% diện chính sách tri ân (Miễn phí 0 đ)"
            danh_sach_ket_qua.append(ket_qua)
            continue

        if so_ve_da_ban >= suc_chua_thuc:
            ket_qua["trang_thai"] = "REJECTED_FULL"
            ket_qua["ghi_chu"] = f"Hệ thống đã đạt sức chứa thực tế C={suc_chua_thuc}"
            ket_qua["boi_thuong"] = True
            danh_sach_ket_qua.append(ket_qua)
            continue

        if quota_con_lai.get(hang_ve_mong_muon, 0) > 0:
            quota_con_lai[hang_ve_mong_muon] -= 1
            so_ve_da_ban += 1
            ket_qua["hang_ve_thuc_nhan"] = hang_ve_mong_muon
            ket_qua["trang_thai"] = "SUCCESS"
            ket_qua["ghi_chu"] = "Cấp vé thành công đúng hạng yêu cầu"
            danh_sach_ket_qua.append(ket_qua)
            continue

        idx_hien_tai = (
            thu_tu_hang_ve.index(hang_ve_mong_muon) 
            if hang_ve_mong_muon in thu_tu_hang_ve 
            else len(thu_tu_hang_ve)
        )
        da_upgrade = False

        for i in range(idx_hien_tai - 1, -1, -1):
            hang_cao_hon = thu_tu_hang_ve[i]
            # Không tự động nâng khách phổ thông vào khoang VVIP Tri Ân bảo vệ riêng
            if "Tri Ân" in hang_cao_hon or hang_cao_hon == "VVIP":
                continue
            if quota_con_lai.get(hang_cao_hon, 0) > 0:
                quota_con_lai[hang_cao_hon] -= 1
                so_ve_da_ban += 1
                ket_qua["hang_ve_thuc_nhan"] = hang_cao_hon
                ket_qua["trang_thai"] = "UPGRADED"
                ket_qua["ghi_chu"] = f"Hết {hang_ve_mong_muon}, Free Upgrade lên {hang_cao_hon}"
                da_upgrade = True
                break

        if da_upgrade:
            danh_sach_ket_qua.append(ket_qua)
            continue

        ket_qua["trang_thai"] = "REJECTED_NO_QUOTA"
        ket_qua["ghi_chu"] = "Hết quota hạng vé yêu cầu và các hạng cao hơn"
        ket_qua["boi_thuong"] = True
        danh_sach_ket_qua.append(ket_qua)

    return danh_sach_ket_qua


def unit_test_m5():
    danh_sach_uu_tien_from_tv2 = [
        {"id_khach": "KH04", "ten": "Dũng", "diem_loyalty": 95, "arrival_time": 1, "hang_ve_mong_muon": "Standard"},
        {"id_khach": "KH02", "ten": "Bình", "diem_loyalty": 95, "arrival_time": 3, "hang_ve_mong_muon": "Standard"},
        {"id_khach": "KH03", "ten": "Châu", "diem_loyalty": 80, "arrival_time": 2, "hang_ve_mong_muon": "VIP"},
        {"id_khach": "KH01", "ten": "An",   "diem_loyalty": 20, "arrival_time": 1, "hang_ve_mong_muon": "Standard"},
    ]

    allocation_from_tv4 = {"VIP": 2, "Standard": 1, "Economy": 0}
    suc_chua_thuc_C = 2

    ket_qua = xu_ly_xung_dot_tham_lam(
        danh_sach_uu_tien=danh_sach_uu_tien_from_tv2,
        allocation=allocation_from_tv4,
        suc_chua_thuc=suc_chua_thuc_C
    )

    print("\n--- KẾT QUẢ XỬ LÝ GIAO DỊCH (M5 - Baseline Test) ---")
    for item in ket_qua:
        print(f"Khách: {item['ten']} ({item['id_khach']}) | Trạng thái: {item['trang_thai']} | Hạng nhận: {item['hang_ve_thuc_nhan']} | Ghi chú: {item['ghi_chu']}")

    assert ket_qua[0]["trang_thai"] == "SUCCESS"
    assert ket_qua[1]["trang_thai"] == "UPGRADED"
    assert ket_qua[2]["trang_thai"] == "REJECTED_FULL"
    assert ket_qua[3]["trang_thai"] == "REJECTED_FULL"

    print("\n[SUCCESS] Unit test 1 (3 hạng) đã vượt qua toàn bộ assertions thành công!")

    # Test 2: Thử nghiệm với 4 hạng vé có khách chính sách tri ân
    ds_4_hang = [
        {"id_khach": "TRIAN_01", "ten": "Mẹ VNAH Nguyễn Thị Thứ", "diem_loyalty": 100, "hang_ve_mong_muon": "VVIP Tri Ân", "is_protected": True},
        {"id_khach": "COM_01", "ten": "Khách Platinum", "diem_loyalty": 50, "hang_ve_mong_muon": "VIP Platinum"},
        {"id_khach": "COM_02", "ten": "Khách Gold 1", "diem_loyalty": 40, "hang_ve_mong_muon": "Gold Standard"},
        {"id_khach": "COM_03", "ten": "Khách Gold 2", "diem_loyalty": 35, "hang_ve_mong_muon": "Gold Standard"},
        {"id_khach": "COM_04", "ten": "Khách Silver quá tải", "diem_loyalty": 10, "hang_ve_mong_muon": "Silver Economy"},
    ]
    alloc_4 = {"VVIP Tri Ân": 1, "VIP Platinum": 2, "Gold Standard": 1, "Silver Economy": 0}
    C_demo = 3

    kq_4 = xu_ly_xung_dot_tham_lam(ds_4_hang, alloc_4, C_demo)
    print("\n--- KẾT QUẢ XỬ LÝ GIAO DỊCH 4 HẠNG VÉ (M5) ---")
    for item in kq_4:
        print(f"Khách: {item['ten']} | Trạng thái: {item['trang_thai']} | Nhận: {item['hang_ve_thuc_nhan']} | Ghi chú: {item['ghi_chu']}")

    assert kq_4[0]["trang_thai"] == "SUCCESS"  # Mẹ VNAH được bảo vệ 100%
    assert kq_4[1]["trang_thai"] == "SUCCESS"  # Platinum đúng hạng
    assert kq_4[2]["trang_thai"] == "SUCCESS"  # Gold 1 đúng hạng
    assert kq_4[3]["trang_thai"] == "REJECTED_FULL" # Gold 2 chạm trần C=3
    assert kq_4[4]["trang_thai"] == "REJECTED_FULL" # Silver chạm trần C=3
    print("\n[SUCCESS] Unit test 2 (4 hạng chuẩn + Cam kết đạo đức bảo vệ Mẹ VNAH) PASSED 100%!")


if __name__ == "__main__":
    unit_test_m5()
