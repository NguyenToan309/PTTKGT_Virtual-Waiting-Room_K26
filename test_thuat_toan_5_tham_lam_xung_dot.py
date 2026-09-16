import unittest
from thuat_toan_5_tham_lam_xung_dot import xu_ly_xung_dot_tham_lam


class TestModuleM5GreedyComprehensive(unittest.TestCase):

    def setUp(self):
        """Khởi tạo dữ liệu mẫu chuẩn từ M2 cho các testcase."""
        self.danh_sach_chuan_m2 = [
            {"id_khach": "KH04", "ten": "Dũng", "diem_loyalty": 95, "arrival_time": 1, "hang_ve_mong_muon": "VIP"},
            {"id_khach": "KH02", "ten": "Bình", "diem_loyalty": 95, "arrival_time": 3, "hang_ve_mong_muon": "Standard"},
            {"id_khach": "KH03", "ten": "Châu", "diem_loyalty": 80, "arrival_time": 2, "hang_ve_mong_muon": "Standard"},
            {"id_khach": "KH01", "ten": "An",   "diem_loyalty": 20, "arrival_time": 1, "hang_ve_mong_muon": "Standard"}
        ]

    def test_cap_dung_hang_ve_thanh_cong(self):
        """Kiểm tra trường hợp Quota dư dả, tất cả khách được cấp đúng hạng mong muốn."""
        allocation = {"VIP": 2, "Standard": 5}
        suc_chua_C = 10
        
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_chuan_m2, allocation, suc_chua_C)
        
        self.assertEqual(len(ket_qua), 4)
        self.assertEqual(ket_qua[0]['status'], 'Success')
        self.assertEqual(ket_qua[0]['hang_ve_duoc_cap'], 'VIP')
        self.assertEqual(ket_qua[1]['status'], 'Success')
        self.assertEqual(ket_qua[1]['hang_ve_duoc_cap'], 'Standard')

    def test_nang_hang_tham_lam_len_vip(self):
        """Kiểm tra trường hợp hết Standard nhưng còn VIP -> Tự động nâng hạng (Upgraded)."""
        allocation = {"VIP": 2, "Standard": 1}
        suc_chua_C = 10
        
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_chuan_m2, allocation, suc_chua_C)
        
        self.assertEqual(ket_qua[0]['status'], 'Success')
        self.assertEqual(ket_qua[0]['hang_ve_duoc_cap'], 'VIP')
        
        self.assertEqual(ket_qua[1]['status'], 'Success')
        self.assertEqual(ket_qua[1]['hang_ve_duoc_cap'], 'Standard')
        
        self.assertEqual(ket_qua[2]['status'], 'Upgraded')
        self.assertEqual(ket_qua[2]['hang_ve_duoc_cap'], 'VIP')
        self.assertFalse(ket_qua[2]['boi_thuong'])

    def test_tu_choi_do_het_quota_va_khong_the_nang_hang(self):
        """Kiểm tra trường hợp hết cả Standard lẫn VIP -> Rejected và đánh dấu bồi thường."""
        allocation = {"VIP": 1, "Standard": 1}
        suc_chua_C = 10
        
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_chuan_m2, allocation, suc_chua_C)
        
        self.assertEqual(ket_qua[3]['status'], 'Rejected')
        self.assertIsNone(ket_qua[3]['hang_ve_duoc_cap'])
        self.assertTrue(ket_qua[3]['boi_thuong'])
        self.assertEqual(ket_qua[3]['ly_do'], 'Het quota va khong the nang hang')

    def test_tu_choi_do_cham_ranh_gioi_suc_chua_c(self):
        """Kiểm tra trường hợp Quota allocation lớn nhưng bị chặn cứng bởi Sức chứa thực C."""
        allocation = {"VIP": 10, "Standard": 10}
        suc_chua_C = 2 
        
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_chuan_m2, allocation, suc_chua_C)
        
        so_ve_da_cap = sum(1 for k in ket_qua if k['status'] in ['Success', 'Upgraded'])
        self.assertEqual(so_ve_da_cap, 2)
        
        self.assertEqual(ket_qua[2]['status'], 'Rejected')
        self.assertEqual(ket_qua[2]['ly_do'], 'Vuot suc chua thuc C')
        self.assertEqual(ket_qua[3]['status'], 'Rejected')
        self.assertEqual(ket_qua[3]['ly_do'], 'Vuot suc chua thuc C')

    def test_ngoai_le_allocation_rong_hoac_thieu_key(self):
        """Kiểm tra tính an toàn khi dict allocation bị thiếu key hoặc rỗng."""
        allocation_thieu = {} 
        suc_chua_C = 5
        
        ket_qua = xu_ly_xung_dot_tham_lam(self.danh_sach_chuan_m2, allocation_thieu, suc_chua_C)
        
        for item in ket_qua:
            self.assertEqual(item['status'], 'Rejected')

    def test_danh_sach_giao_dich_rong(self):
        """Kiểm tra trường hợp không có giao dịch nào đầu vào."""
        allocation = {"VIP": 5, "Standard": 5}
        suc_chua_C = 10
        
        ket_qua = xu_ly_xung_dot_tham_lam([], allocation, suc_chua_C)
        self.assertEqual(len(ket_qua), 0)


if __name__ == '__main__':
    unittest.main()