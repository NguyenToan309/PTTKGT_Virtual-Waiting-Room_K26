
import unittest
from thuat_toan_2_hang_doi_heap import HangDoiUuTienMaxHeap

class TestHangDoiUuTienMaxHeap(unittest.TestCase):
    def test_them_va_trich_xuat_top_k(self):
        hd = HangDoiUuTienMaxHeap()
        data = [
            {"id": 1, "ten": "An", "diem_loyalty": 40, "arrival_time": 10},
            {"id": 2, "ten": "Bình", "diem_loyalty": 90, "arrival_time": 12},
            {"id": 3, "ten": "Chi", "diem_loyalty": 40, "arrival_time": 4} # Trùng loyalty nhưng đến sớm hơn
        ]
        hd.them_khach_hang(data)
        
        top_2 = hd.trich_xuat_top_k(2)
        # Kỳ vọng: ID 2 cao điểm nhất (90), tiếp theo là ID 3 (loyalty 40, đến lúc 4)
        self.assertEqual(top_2[0]["id"], 2)
        self.assertEqual(top_2[1]["id"], 3)

    def test_edge_case_rong(self):
        hd = HangDoiUuTienMaxHeap()
        hd.them_khach_hang([])
        self.assertEqual(hd.trich_xuat_top_k(5), [])

if __name__ == '__main__':
    unittest.main()
    def test_ban_giao_cho_module_5(self):
        """Kiểm tra định dạng và kết quả bàn giao cho Module 5 (Phân bố chỗ ngồi)."""
        hd = HangDoiUuTienMaxHeap()
        danh_sach_phong_cho = [
            {"id_khach": "KH01", "ten": "An", "diem_loyalty": 20, "arrival_time": 1},
            {"id_khach": "KH02", "ten": "Bình", "diem_loyalty": 95, "arrival_time": 3},
            {"id_khach": "KH03", "ten": "Châu", "diem_loyalty": 80, "arrival_time": 2},
            {"id_khach": "KH04", "ten": "Dũng", "diem_loyalty": 95, "arrival_time": 1} # Cùng 95 điểm, đến sớm hơn (1) đứng trước Bình (3)
        ]
        
        hd.them_khach_hang(danh_sach_phong_cho)
        
        # Lấy Top 3 khách hàng ưu tiên cao nhất để phân bổ ghế (Input cho Module 5)
        top_khach_hang_m5 = hd.trich_xuat_top_k(3)
        
        # Kiểm tra tính chính xác thứ tự ưu tiên bàn giao
        self.assertEqual(len(top_khach_hang_m5), 3)
        self.assertEqual(top_khach_hang_m5[0]["id_khach"], "KH04") # 95 điểm, arrival_time 1
        self.assertEqual(top_khach_hang_m5[1]["id_khach"], "KH02") # 95 điểm, arrival_time 3
        self.assertEqual(top_khach_hang_m5[2]["id_khach"], "KH03") # 80 điểm
        
        print("\n[BÀN GIAO M5] Dữ liệu top khách hàng ưu tiên gửi sang Module 5 thành công:")
        for kh in top_khach_hang_m5:
            print(f" - Khách: {kh['ten']} | Loyalty: {kh['diem_loyalty']} | Đến lúc: {kh['arrival_time']}")