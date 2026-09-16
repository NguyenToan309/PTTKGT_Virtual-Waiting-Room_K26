import unittest
from thuat_toan_6_thu_hoi_va_truot import TrangThaiHeThongDong


class TestModule6(unittest.TestCase):

    def test_them_ve(self):
        he_thong = TrangThaiHeThongDong()

        he_thong.them_ve_tam_giu({
            "id_ve": "V01",
            "expiration_time": 120
        })

        he_thong.them_ve_tam_giu({
            "id_ve": "V02",
            "expiration_time": 100
        })

        self.assertEqual(
            he_thong.heap_ve[0]["id_ve"],
            "V02"
        )


    def test_thu_hoi_ve_het_han(self):
        he_thong = TrangThaiHeThongDong()

        he_thong.them_ve_tam_giu({
            "id_ve": "V01",
            "expiration_time": 100
        })

        he_thong.them_ve_tam_giu({
            "id_ve": "V02",
            "expiration_time": 150
        })

        ket_qua = he_thong.thu_hoi_ve_het_han(120)

        self.assertEqual(
            len(ket_qua),
            1
        )

        self.assertEqual(
            ket_qua[0]["id_ve"],
            "V01"
        )


    def test_ti_le_rot(self):
        he_thong = TrangThaiHeThongDong(
            kich_thuoc_cua_so=5
        )

        he_thong.ghi_nhan_giao_dich(False)
        he_thong.ghi_nhan_giao_dich(True)
        he_thong.ghi_nhan_giao_dich(False)
        he_thong.ghi_nhan_giao_dich(True)

        self.assertEqual(
            he_thong.lay_ti_le_rot_o1(),
            0.5
        )


if __name__ == "__main__":
    unittest.main()
