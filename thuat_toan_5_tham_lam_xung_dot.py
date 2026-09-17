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
    thu_tu_hang_ve = ["VIP", "Standard", "Economy"]

    for khach in danh_sach_uu_tien:
        id_khach = khach.get("id_khach") or khach.get("user_id", "UNKNOWN")
        ten = khach.get("ten", "Khách hàng")
        hang_ve_mong_muon = khach.get("hang_ve_mong_muon", "Standard")
        diem_loyalty = khach.get("diem_loyalty", 0)

        ket_qua = {
            "id_khach": id_khach,
            "ten": ten,
            "diem_loyalty": diem_loyalty,
            "hang_ve_mong_muon": hang_ve_mong_muon,
            "hang_ve_thuc_nhan": None,
            "trang_thai": "PENDING",
            "ghi_chu": "",
            "boi_thuong": False
        }

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

    print("\n--- KẾT QUẢ XỬ LÝ GIAO DỊCH (M5) ---")
    for item in ket_qua:
        print(f"Khách: {item['ten']} ({item['id_khach']}) | Trạng thái: {item['trang_thai']} | Hạng nhận: {item['hang_ve_thuc_nhan']} | Ghi chú: {item['ghi_chu']}")

    assert ket_qua[0]["trang_thai"] == "SUCCESS"
    assert ket_qua[1]["trang_thai"] == "UPGRADED"
    assert ket_qua[2]["trang_thai"] == "REJECTED_FULL"
    assert ket_qua[3]["trang_thai"] == "REJECTED_FULL"

    print("\n[SUCCESS] Unit test đã vượt qua toàn bộ assertions thành công!")


if __name__ == "__main__":
    unit_test_m5()
