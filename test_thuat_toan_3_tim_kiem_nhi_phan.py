# -*- coding: utf-8 -*-
"""
Unit Test cho Module 3: Binary Search on Answer Space (Tìm Kiếm Nhị Phân)
File: test_thuat_toan_3_tim_kiem_nhi_phan.py
"""

import unittest
from thuat_toan_3_tim_kiem_nhi_phan_M3_hoan_chinh import (
    tim_kiem_nhi_phan_nguong_ban_lo,
    tinh_rui_ro
)

class TestModule3BinarySearch(unittest.TestCase):
    def test_tim_kiem_nhi_phan_chuan(self):
        C = 1000
        p = 0.2
        tau_0 = 0.05
        m_star = tim_kiem_nhi_phan_nguong_ban_lo(C, p, tau_0, max_limit=2000)
        
        # M* phải lớn hơn C vì p > 0
        self.assertGreater(m_star, C)
        
        # Kiểm tra điều kiện an toàn tại M*: P(K > C) <= tau_0
        risk_at_m_star = tinh_rui_ro(m_star, C, p)
        self.assertLessEqual(risk_at_m_star, tau_0)

    def test_concert_quy_mo_lon(self):
        C = 100000
        p = 0.18
        tau_0 = 0.05
        m_star = tim_kiem_nhi_phan_nguong_ban_lo(C, p, tau_0, max_limit=200000)
        self.assertEqual(m_star, 121683)

if __name__ == "__main__":
    unittest.main()
