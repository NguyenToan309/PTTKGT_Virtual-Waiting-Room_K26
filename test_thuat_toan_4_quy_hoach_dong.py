# -*- coding: utf-8 -*-
"""
Unit Test cho Module 4: Bounded Knapsack DP (Quy Hoạch Động Phân Bổ Vé)
File: test_thuat_toan_4_quy_hoach_dong.py
"""

import unittest
from thuat_toan_4_quy_hoach_dong import quy_hoach_dong_phan_bo_ve

class TestModule4Knapsack(unittest.TestCase):
    def test_phan_bo_4_hang_ve(self):
        m_star = 121683
        classes = [
            {"name": "VVIP Tri Ân", "price": 0.0, "demand_limit": 15000, "protected_pool": 15000},
            {"name": "VIP Platinum", "price": 2500000.0, "demand_limit": 35000},
            {"name": "Gold Standard", "price": 1200000.0, "demand_limit": 50000},
            {"name": "Silver Economy", "price": 600000.0, "demand_limit": 30000},
        ]
        res = quy_hoach_dong_phan_bo_ve(m_star, classes)
        
        # Kiểm tra cấp đủ 100% VVIP Tri Ân
        self.assertEqual(res["VVIP Tri Ân"], 15000)
        # Kiểm tra ưu tiên giá cao
        self.assertEqual(res["VIP Platinum"], 35000)
        self.assertEqual(res["Gold Standard"], 50000)
        self.assertEqual(res["Silver Economy"], 21683)
        self.assertEqual(sum(res.values()), m_star)

    def test_edge_case_m_star_0(self):
        classes = [
            {"name": "VIP", "price": 1000.0, "demand_limit": 10}
        ]
        res = quy_hoach_dong_phan_bo_ve(0, classes)
        self.assertEqual(res["VIP"], 0)

if __name__ == "__main__":
    unittest.main()
