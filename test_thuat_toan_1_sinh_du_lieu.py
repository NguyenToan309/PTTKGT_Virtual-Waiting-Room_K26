# -*- coding: utf-8 -*-
"""
Unit Test cho Module 1: Merge Sort (Chia Để Trị)
File: test_thuat_toan_1_sinh_du_lieu.py
"""

import unittest
from thuat_toan_1_sinh_du_lieu import chia_de_tri_sap_xep_thoi_gian

class TestModule1MergeSort(unittest.TestCase):
    def test_sap_xep_co_ban(self):
        users = [
            {"user_id": 1, "arrival_time": 105},
            {"user_id": 2, "arrival_time": 42},
            {"user_id": 3, "arrival_time": 88},
            {"user_id": 4, "arrival_time": 15},
        ]
        sorted_users = chia_de_tri_sap_xep_thoi_gian(users)
        times = [u["arrival_time"] for u in sorted_users]
        self.assertEqual(times, [15, 42, 88, 105])

    def test_trung_thoi_gian_on_dinh(self):
        users = [
            {"user_id": 1, "arrival_time": 50},
            {"user_id": 2, "arrival_time": 20},
            {"user_id": 3, "arrival_time": 50},
        ]
        sorted_users = chia_de_tri_sap_xep_thoi_gian(users)
        self.assertEqual(sorted_users[0]["user_id"], 2)
        # Giữ tính ổn định: user 1 trước user 3
        self.assertEqual(sorted_users[1]["user_id"], 1)
        self.assertEqual(sorted_users[2]["user_id"], 3)

    def test_danh_sach_rong(self):
        self.assertEqual(chia_de_tri_sap_xep_thoi_gian([]), [])

    def test_danh_sach_mot_phan_tu(self):
        users = [{"user_id": 99, "arrival_time": 100}]
        self.assertEqual(chia_de_tri_sap_xep_thoi_gian(users), users)

if __name__ == "__main__":
    unittest.main()
