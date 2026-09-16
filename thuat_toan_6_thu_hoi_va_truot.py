 
        self.assertEqual(thu_hoi_1[0]["txn_id"], "T2")
        
        thu_hoi_2 = self.he_thong.thu_hoi_ve_het_han(16.0)
        self.assertEqual(len(thu_hoi_2), 2)
        self.assertEqual(thu_hoi_2[0]["txn_id"], "T1")
        self.assertEqual(thu_hoi_2[1]["txn_id"], "T3")

    def test_sliding_window_ty_le_rot_o1(self):
      
        self.he_thong.ghi_nhan_giao_dich(is_dropped=True) 
        self.assertEqual(self.he_thong.lay_ti_le_rot_o1(), 1.0) 
        
        self.he_thong.ghi_nhan_giao_dich(is_dropped=False)
        self.assertEqual(self.he_thong.lay_ti_le_rot_o1(), 0.5) 
      
        self.he_thong.ghi_nhan_giao_dich(is_dropped=False)
        self.assertAlmostEqual(self.he_thong.lay_ti_le_rot_o1(), 1/3) 
        
        self.he_thong.ghi_nhan_giao_dich(is_dropped=False) 
        self.assertEqual(self.he_thong.lay_ti_le_rot_o1(), 0.0)

if __name__ == '__main__':
    unittest.main()
