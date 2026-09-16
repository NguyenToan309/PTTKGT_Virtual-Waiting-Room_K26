from typing import List, Dict, Any
import unittest


class KhongYeuCau:
    pass


def xu_ly_xung_dot_tham_lam(
    danh_sach_giao_dich: List[Dict[str, Any]],
    allocation: Dict[str, int],
    suc_chua_C: int
) -> List[Dict[str, Any]]:
    quota_con_lai = allocation.copy()
    
    if 'VIP' not in quota_con_lai:
        quota_con_lai['VIP'] = 0
    if 'Standard' not in quota_con_lai:
        quota_con_lai['Standard'] = 0

    tong_ve_da_cap = 0
    ket_qua_giao_dich: List[Dict[str, Any]] = []

    for user in danh_sach_giao_dich:
        ket_qua = user.copy()
        hang_mong_muon = user.get('hang_ve_mong_muon', 'Standard')

        if tong_ve_da_cap >= suc_chua_C:
            ket_qua['status'] = 'Rejected'
            ket_qua['hang_ve_duoc_cap'] = None
            ket_qua['boi_thuong'] = True
            ket_qua['ly_do'] = 'Vuot suc chua thuc C'
            ket_qua_giao_dich.append(ket_qua)
            continue

        if quota_con_lai.get(hang_mong_muon, 0) > 0:
            quota_con_lai[hang_mong_muon] -= 1
            tong_ve_da_cap += 1
            ket_qua['status'] = 'Success'
            ket_qua['hang_ve_duoc_cap'] = hang_mong_muon
            ket_qua['boi_thuong'] = False
            ket_qua['ly_do'] = 'Cap dung hang ve'

        elif hang_mong_muon == 'Standard' and quota_con_lai.get('VIP', 0) > 0:
            quota_con_lai['VIP'] -= 1
            tong_ve_da_cap += 1
            ket_qua['status'] = 'Upgraded'
            ket_qua['hang_ve_duoc_cap'] = 'VIP'
            ket_qua['boi_thuong'] = False
            ket_qua['ly_do'] = 'Nang hang len VIP do het Standard'

        else:
            ket_qua['status'] = 'Rejected'
            ket_qua['hang_ve_duoc_cap'] = None
            ket_qua['boi_thuong'] = True
            ket_qua['ly_do'] = 'Het quota va khong the nang hang'

        ket_qua_giao_dich.append(ket_qua)

    return ket_qua_giao_dich


def in_ket_qua_trinh_chieu(danh_sach_ket_qua: List[Dict[str, Any]], suc_chua_C: int, allocation: Dict[str, int]):
    print("=" * 75)
    print(" BÁO CÁO KẾT QUẢ XỬ LÝ XUNG ĐỘT")
    print("=" * 75)
    print(f"Cấu hình đầu vào:")
    print(f" - Sức chứa thực tế (C): {suc_chua_C}")
    print(f" - Quota phân bổ ban đầu: VIP = {allocation.get('VIP', 0)} | Standard = {allocation.get('Standard', 0)}")
    print("-" * 75)
    
    fmt = "{:<10} {:<10} {:<10} {:<15} {:<15} {:<12}"
    print(fmt.format("ID KHÁCH", "TÊN", "LOI TRUYÊN", "HẠNG YÊU CẦU", "TRẠNG THÁI", "HẠNG ĐƯỢC CẤP"))
    print("-" * 75)
    
    so_ve_cap = 0
    so_upgrade = 0
    so_reject = 0
    
    for item in danh_sach_ket_qua:
        id_k = str(item.get("id_khach", "N/A"))
        ten = str(item.get("ten", "N/A"))
        diem = str(item.get("diem_loyalty", 0))
        hang_req = str(item.get("hang_ve_mong_muon", "Standard"))
        status = str(item.get("status", "N/A"))
        hang_cap = str(item.get("hang_ve_duoc_cap") or "Không")
        
        if status in ['Success', 'Upgraded']:
            so_ve_cap += 1
            if status == 'Upgraded':
                so_upgrade += 1
        else:
            so_reject += 1

        print(fmt.format(id_k, ten, diem, hang_req, status, hang_cap))

    print("-" * 75)
    print(f"TỔNG KẾT GIAO DỊCH:")
    print(f" - Số vé cấp thành công: {so_ve_cap}/{len(danh_sach_ket_qua)} (Trong đó Nâng hạng: {so_upgrade})")
    print(f" - Số giao dịch bị từ chối/bồi thường: {so_reject}")
    print(f" - Kiểm soát sức chứa C: {'ĐẠT (<= C)' if so_ve_cap <= suc_chua_C else 'VI PHẠM'}")
    print("=" * 75)


class TestModuleM5Greedy(unittest.TestCase):

    def setUp(self):
        self.danh_sach_m2 = [
            {"id_khach": "KH04", "ten": "Dũng", "diem_loyalty": 95, "arrival_time": 1, "hang_ve_mong_muon": "VIP"},
            {"id_khach": "KH02", "ten": "Bình", "diem_loyalty": 95, "arrival_time": 3, "hang_ve_mong_muon": "Standard"},
            {"id_khach": "KH03", "ten": "Châu", "diem_loyalty": 80, "arrival_time": 2, "hang_ve_mong_muon": "Standard"},
            {"id_khach": "KH01", "ten": "An",   "diem_loyalty": 20, "arrival_time": 1, "hang_ve_mong_muon": "Standard"}
        ]

    def test_trinh_chieu_mo_phong(self):
        allocation = {"VIP": 2, "Standard": 1}
        suc_chua_C = 10
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_m2, allocation, suc_chua_C)
        in_ket_qua_trinh_chieu(ket_qua, suc_chua_C, allocation)

    def test_luong_thanh_cong_hoan_hao(self):
        allocation = {"VIP": 2, "Standard": 5}
        suc_chua_C = 10
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_m2, allocation, suc_chua_C)
        self.assertEqual(len(ket_qua), 4)

    def test_kiem_soat_suc_chua_cung_C(self):
        allocation = {"VIP": 10, "Standard": 10}
        suc_chua_C = 2
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_m2, allocation, suc_chua_C)
        so_ve_cap_thanh_cong = sum(1 for k in ket_qua if k['status'] in ['Success', 'Upgraded'])
        self.assertEqual(so_ve_cap_thanh_cong, 2)


if __name__ == '__main__':
    unittest.main()