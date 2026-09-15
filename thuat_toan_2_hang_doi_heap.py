
"""
Module 2: Hàng đợi ưu tiên (Max-Heap) cho hệ thống Virtual Waiting Room.
File: thuat_toan_2_hang_doi_heap.py
Chức năng: Quản lý phòng chờ ảo, ưu tiên khách hàng có điểm loyalty cao.
"""

from typing import List, Dict, Any

class HangDoiUuTienMaxHeap:
    def __init__(self) -> None:
        """Khởi tạo hàng đợi ưu tiên dưới dạng mảng heap rỗng."""
        self.heap: List[Dict[str, Any]] = []

    def _so_sanh(self, i: int, j: int) -> bool:
        """
        Hàm helper so sánh độ ưu tiên giữa 2 phần tử trong heap.
        Tiêu chí 1: Điểm loyalty cao hơn đứng trước.
        Tiêu chí 2: Nếu trùng điểm loyalty, thời gian đến sớm hơn (arrival_time nhỏ hơn) đứng trước.
        """
        khach_i = self.heap[i]
        khach_j = self.heap[j]
        
        loyalty_i = khach_i.get("diem_loyalty", 0)
        loyalty_j = khach_j.get("diem_loyalty", 0)
        
        if loyalty_i != loyalty_j:
            return loyalty_i > loyalty_j
        else:
            time_i = khach_i.get("arrival_time", float('inf'))
            time_j = khach_j.get("arrival_time", float('inf'))
            return time_i < time_j

    def _sift_up(self, index: int) -> None:
        r"""Đưa phần tử lên trên để duy trì tính chất Max-Heap ($O(\log N)$)."""
        parent = (index - 1) // 2
        while index > 0 and self._so_sanh(index, parent):
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            index = parent
            parent = (index - 1) // 2

    def _sift_down(self, index: int) -> None:
        """Đẩy phần tử xuống dưới để duy trì tính chất Max-Heap ($O(\log N)$)."""
        max_index = index
        length = len(self.heap)
        left_child = 2 * index + 1
        right_child = 2 * index + 2

        if left_child < length and self._so_sanh(left_child, max_index):
            max_index = left_child
        if right_child < length and self._so_sanh(right_child, max_index):
            max_index = right_child

        if max_index != index:
            self.heap[index], self.heap[max_index] = self.heap[max_index], self.heap[index]
            self._sift_down(max_index)

    def them_khach_hang(self, danh_sach_khach: List[Dict[str, Any]]) -> None:
        """
        Public function: Thêm danh sách khách hàng vào hàng đợi Max-Heap.
        Xử lý edge case: Bỏ qua nếu đầu vào không hợp lệ hoặc rỗng.
        """
        if not isinstance(danh_sach_khach, list):
            raise ValueError("Đầu vào phải là một List các Dictionary chứa thông tin khách hàng.")
        
        for khach in danh_sach_khach:
            if isinstance(khach, dict):
                self.heap.append(khach)
                self._sift_up(len(self.heap) - 1)

    def trich_xuat_top_k(self, k: int) -> List[Dict[str, Any]]:
        """
        Public function: Trích xuất K khách hàng có độ ưu tiên cao nhất ra khỏi hàng đợi.
        Độ phức tạp thời gian: O(K log N).
        Xử lý edge case: Nếu k <= 0 hoặc heap rỗng, trả về danh sách rỗng. 
        Nếu k lớn hơn tổng số khách, trả về toàn bộ số khách hiện có.
        """
        if k <= 0 or not self.heap:
            return []
        
        ket_qua = []
        # Sao chép heap tạm để không làm mất dữ liệu gốc của hàng đợi phòng chờ
        hien_tai_heap = list(self.heap)
        
        while k > 0 and self.heap:
            top_element = self.heap[0]
            ket_qua.append(top_element)
            
            last_element = self.heap.pop()
            if self.heap:
                self.heap[0] = last_element
                self._sift_down(0)
            k -= 1
            
        # Khôi phục trạng thái heap gốc
        self.heap = hien_tai_heap
        return ket_qua
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