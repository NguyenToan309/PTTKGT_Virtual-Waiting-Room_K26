
from collections import deque


class TrangThaiHeThongDong:
    def __init__(self, kich_thuoc_cua_so=5):
  
        self.heap_ve = []

        self.cua_so = deque()

        self.kich_thuoc_cua_so = kich_thuoc_cua_so

        self.so_rot = 0


    def them_ve_tam_giu(self, ve):
        """
        Thêm vé vào danh sách và sắp xếp
        theo expiration_time tăng dần.
        """

        self.heap_ve.append(ve)

        self.heap_ve.sort(
            key=lambda x: x["expiration_time"]
        )


    def thu_hoi_ve_het_han(self, thoi_gian_hien_tai):
        """
        Thu hồi các vé đã hết hạn.
        """

        ve_thu_hoi = []

        while self.heap_ve:
            ve_dau = self.heap_ve[0]

            if ve_dau["expiration_time"] <= thoi_gian_hien_tai:
                ve_thu_hoi.append(
                    self.heap_ve.pop(0)
                )
            else:
                break

        return ve_thu_hoi


    def ghi_nhan_giao_dich(self, bi_rot):
        """
        True = giao dịch bị rớt
        False = giao dịch thành công
        """

        if bi_rot:
            gia_tri = 1
        else:
            gia_tri = 0

        self.cua_so.append(gia_tri)

        if gia_tri == 1:
            self.so_rot += 1

        if len(self.cua_so) > self.kich_thuoc_cua_so:

            gia_tri_cu = self.cua_so.popleft()

            if gia_tri_cu == 1:
                self.so_rot -= 1


    def lay_ti_le_rot_o1(self):
        """
        Tính tỷ lệ rớt p(t).
        """

        if len(self.cua_so) == 0:
            return 0

        return self.so_rot / len(self.cua_so)


if __name__ == "__main__":
    he_thong = TrangThaiHeThongDong(5)

    he_thong.them_ve_tam_giu({
        "id_ve": "V01",
        "expiration_time": 100
    })

    he_thong.them_ve_tam_giu({
        "id_ve": "V02",
        "expiration_time": 150
    })

    he_thong.them_ve_tam_giu({
        "id_ve": "V03",
        "expiration_time": 120
    })

    print("Danh sách vé:")
    print(he_thong.heap_ve)

    ve_het_han = he_thong.thu_hoi_ve_het_han(125)

    print("\nVé hết hạn:")
    print(ve_het_han)

    he_thong.ghi_nhan_giao_dich(False)
    he_thong.ghi_nhan_giao_dich(True)
    he_thong.ghi_nhan_giao_dich(False)
    he_thong.ghi_nhan_giao_dich(True)
    he_thong.ghi_nhan_giao_dich(True)

    print("\nTỷ lệ rớt:")
    print(he_thong.lay_ti_le_rot_o1())

