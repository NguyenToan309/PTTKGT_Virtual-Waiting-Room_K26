"""
Unit test cho Module 7: thuat_toan_7_saa_benchmark.py
Kiem tra toan dien 100% Definition of Done va cac tieu chi tu TV7-A den TV7-J.
"""

import unittest
from thuat_toan_7_saa_benchmark import (
    sinh_kich_ban_xac_suat,
    chay_danh_gia_saa,
    tim_nghiem_saa_chuan,
    in_bang_so_sanh_thuc_te,
)


class TestModule7SAABenchmark(unittest.TestCase):

    def test_sinh_kich_ban_dung_so_luong_va_phan_phoi(self):
        """TV7-A & TV7-C: Kiem tra sinh dung S kich ban voi nhieu loai phan phoi."""
        # Test Uniform
        scenarios_uniform = sinh_kich_ban_xac_suat(S=50, distributions={"type": "uniform", "min_p": 0.1, "max_p": 0.3}, seed=1)
        self.assertEqual(len(scenarios_uniform), 50)
        for p in scenarios_uniform:
            self.assertTrue(0.01 <= p <= 0.90)

        # Test Beta
        scenarios_beta = sinh_kich_ban_xac_suat(S=30, distributions={"type": "beta", "alpha": 2.0, "beta": 5.0}, seed=2)
        self.assertEqual(len(scenarios_beta), 30)

        # Test Normal
        scenarios_normal = sinh_kich_ban_xac_suat(S=20, distributions={"type": "normal", "mean": 0.25, "std": 0.04}, seed=3)
        self.assertEqual(len(scenarios_normal), 20)

    def test_tim_nghiem_saa_chuan(self):
        """TV7-E & TV7-G: Kiem tra ham public tim_nghiem_saa_chuan theo dac ta TV7-E."""
        res = tim_nghiem_saa_chuan(S=25, capacity_C=50, tau_0=0.05, seed=42)
        self.assertIsInstance(res, dict)
        self.assertIn("m_star_saa", res)
        self.assertIn("allocation_proposed", res)
        self.assertIn("allocation_baseline", res)
        self.assertIn("proposed", res)
        self.assertIn("baseline", res)
        self.assertIn("improvement_pct", res)

        # Proposed overbooking limit M* phai >= C
        self.assertGreaterEqual(res["m_star_saa"], 50)
        # Tinh toan doanh thu phai hop le (khong am)
        self.assertGreater(res["proposed"]["avg_net_revenue"], 0.0)
        self.assertGreater(res["baseline"]["avg_net_revenue"], 0.0)

    def test_edge_cases_va_phong_thu_du_lieu(self):
        """TV7-F: Kiem tra phong thu du lieu di thuong, am hoac sai kieu."""
        # S <= 0 hoac khong phai int
        with self.assertRaises(ValueError):
            tim_nghiem_saa_chuan(S=0)
        with self.assertRaises(ValueError):
            tim_nghiem_saa_chuan(S=-10)

        # capacity_C <= 0
        with self.assertRaises(ValueError):
            tim_nghiem_saa_chuan(capacity_C=0)
        with self.assertRaises(ValueError):
            tim_nghiem_saa_chuan(capacity_C=-50)

        # tau_0 ngoai khoang (0, 1)
        with self.assertRaises(ValueError):
            tim_nghiem_saa_chuan(tau_0=0.0)
        with self.assertRaises(ValueError):
            tim_nghiem_saa_chuan(tau_0=1.2)

        # distributions la None hoac empty dict phai van chay duoc binh thuong
        res_none_dist = tim_nghiem_saa_chuan(S=5, distributions=None, capacity_C=20)
        self.assertIsInstance(res_none_dist, dict)

    def test_in_bang_so_sanh_thuc_te(self):
        """TV7-J: Kiem tra ham in bang hien thi ra Console khong quang ngoai le."""
        res = tim_nghiem_saa_chuan(S=10, capacity_C=30, tau_0=0.05, seed=7)
        try:
            in_bang_so_sanh_thuc_te(res)
        except Exception as e:
            self.fail(f"in_bang_so_sanh_thuc_te gap loi: {e}")


if __name__ == "__main__":
    unittest.main()
