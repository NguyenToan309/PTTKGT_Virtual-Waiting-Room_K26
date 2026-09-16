"""
===========================================================
MODULE M3 - BINARY SEARCH ON ANSWER SPACE
===========================================================

Mục tiêu:
    Tìm M_star lớn nhất sao cho:

        P(K > C) <= tau_0

    với:

        K ~ Binomial(M, 1 - p)

Thành phần:
    - tinh_rui_ro(): tính P(K > C)
    - KhongYeuCau: lớp xử lý thuật toán M3
    - tim_kiem_nhi_phan_nguong_ban_lo(): hàm giao diện chính
    - kiem_tra_M_star(): kiểm tra nghiệm cực đại
    - unit_test(): kiểm thử

Độ phức tạp:
    O(log(M_max) * O(CDF))

Thư viện:
    scipy.stats.binom

Cài đặt:
    python -m pip install scipy
===========================================================
"""

from scipy.stats import binom


def tinh_rui_ro(M, C, p):
    """
    Tính xác suất P(K > C), với:

        K ~ Binomial(M, 1 - p)

    Parameters
    ----------
    M : int
        Tổng số yêu cầu được xét.

    C : int
        Sức chứa hệ thống.

    p : float
        Tỷ lệ rớt, 0 <= p <= 1.

    Returns
    -------
    float
        Xác suất P(K > C).
    """

    if M < 0:
        raise ValueError("M phải là số nguyên không âm.")

    if C < 0:
        raise ValueError("C phải là số nguyên không âm.")

    if not 0 <= p <= 1:
        raise ValueError("p phải nằm trong khoảng [0, 1].")

    # Nếu M <= C thì dù tất cả M yêu cầu đều thành công,
    # số thành công cũng không thể vượt quá C.
    if M <= C:
        return 0.0

    success_probability = 1.0 - p

    # P(K > C) = P(K >= C + 1)
    #
    # sf(C) = 1 - CDF(C), nhưng được tính theo hàm
    # survival function để phù hợp với xác suất phần đuôi.
    return float(
        binom.sf(C, M, success_probability)
    )


class KhongYeuCau:
    """
    Module xử lý bài toán Binary Search on Answer Space.

    Lớp này không dùng cấu trúc dữ liệu đặc biệt.
    Binary Search được thực hiện trực tiếp trên miền số nguyên M.
    """

    def __init__(self, C, p, tau_0, max_limit=10000):
        """
        Khởi tạo tham số bài toán.
        """

        # Kiểm tra C
        if not isinstance(C, int) or isinstance(C, bool):
            raise ValueError("C phải là số nguyên.")

        if C < 0:
            raise ValueError("C phải lớn hơn hoặc bằng 0.")

        # Kiểm tra p
        if not isinstance(p, (int, float)) or isinstance(p, bool):
            raise ValueError("p phải là số.")

        if not 0 <= p <= 1:
            raise ValueError(
                "p phải nằm trong khoảng [0, 1]."
            )

        # Kiểm tra tau_0
        if not isinstance(tau_0, (int, float)) or isinstance(tau_0, bool):
            raise ValueError("tau_0 phải là số.")

        if not 0 <= tau_0 <= 1:
            raise ValueError(
                "tau_0 phải nằm trong khoảng [0, 1]."
            )

        # Kiểm tra giới hạn tìm kiếm
        if not isinstance(max_limit, int) or isinstance(max_limit, bool):
            raise ValueError(
                "max_limit phải là số nguyên."
            )

        if max_limit < C:
            raise ValueError(
                "max_limit phải lớn hơn hoặc bằng C."
            )

        self.C = C
        self.p = float(p)
        self.tau_0 = float(tau_0)
        self.max_limit = max_limit

    def rui_ro(self, M):
        """Tính P(K > C) tại một giá trị M."""
        return tinh_rui_ro(
            M,
            self.C,
            self.p
        )

    def tim_kiem(self):
        """
        Binary Search tìm M_star lớn nhất thỏa:

            P(K > C) <= tau_0
        """

        C = self.C
        p = self.p
        tau_0 = self.tau_0
        max_limit = self.max_limit

        # ---------------------------------------------------
        # Edge case: p = 0
        # ---------------------------------------------------
        #
        # Tất cả yêu cầu đều thành công.
        # Nếu M > C thì P(K > C) = 1.
        if p == 0:
            if tau_0 < 1:
                return C
            return max_limit

        # ---------------------------------------------------
        # Edge case: p = 1
        # ---------------------------------------------------
        #
        # Không có yêu cầu nào thành công.
        # K = 0 => P(K > C) = 0.
        return self._binary_search()

    def _binary_search(self):
        """
        Thực hiện Binary Search trên miền [C, max_limit].
        """

        left = self.C
        right = self.max_limit

        # M = C luôn an toàn vì P(K > C) = 0.
        answer = self.C

        while left <= right:

            mid = left + (right - left) // 2

            risk = self.rui_ro(mid)

            if risk <= self.tau_0:
                # mid hợp lệ.
                # Vì cần M lớn nhất, tìm tiếp bên phải.
                answer = mid
                left = mid + 1

            else:
                # mid không hợp lệ.
                # Tìm về bên trái.
                right = mid - 1

        return answer


def tim_kiem_nhi_phan_nguong_ban_lo(
    C,
    p,
    tau_0,
    max_limit=10000
):
    """
    Hàm chính của module M3.

    Trả về M_star lớn nhất thỏa:
        P(K > C) <= tau_0
    """

    module = KhongYeuCau(
        C=C,
        p=p,
        tau_0=tau_0,
        max_limit=max_limit
    )

    return module.tim_kiem()


def kiem_tra_M_star(C, p, tau_0, M_star):
    """
    Kiểm tra hai điều kiện để xác nhận M_star là nghiệm cực đại:

        P(K > C | M_star) <= tau_0

    và nếu M_star < max_limit:

        P(K > C | M_star + 1) > tau_0

    Returns
    -------
    bool
        True nếu kiểm tra đạt.
    """

    risk_star = tinh_rui_ro(
        M_star,
        C,
        p
    )

    risk_next = tinh_rui_ro(
        M_star + 1,
        C,
        p
    )

    print("\n" + "=" * 60)
    print("KIEM TRA M_STAR")
    print("=" * 60)

    print(f"C                 = {C}")
    print(f"p                 = {p}")
    print(f"tau_0             = {tau_0}")
    print(f"M_star            = {M_star}")
    print(f"P(K > C) tai M*   = {risk_star:.10f}")
    print(f"P(K > C) tai M*+1 = {risk_next:.10f}")

    condition_1 = risk_star <= tau_0

    # Nếu M_star đã chạm max_limit thì không thể kiểm tra
    # "M_star + 1" trong miền tìm kiếm.
    condition_2 = risk_next > tau_0

    if condition_1:
        print("[DAT] M_star thoa dieu kien rui ro.")
    else:
        print("[LOI] M_star khong thoa dieu kien.")

    if condition_2:
        print("[DAT] M_star + 1 vuot muc rui ro cho phep.")
    else:
        print("[CAN KIEM TRA] M_star + 1 van thoa dieu kien.")

    return condition_1 and condition_2


def hien_thi_ket_qua(C, p, tau_0, max_limit=10000):
    """
    Chạy testcase và in kết quả.
    """

    print("\n" + "=" * 60)
    print("MODULE M3 - BINARY SEARCH ON ANSWER SPACE")
    print("=" * 60)

    print(f"C         = {C}")
    print(f"p         = {p}")
    print(f"tau_0     = {tau_0}")
    print(f"max_limit = {max_limit}")

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=C,
        p=p,
        tau_0=tau_0,
        max_limit=max_limit
    )

    print("\nKET QUA:")
    print(f"M_star = {M_star}")

    kiem_tra_M_star(
        C=C,
        p=p,
        tau_0=tau_0,
        M_star=M_star
    )

    return M_star


def unit_test():
    """
    Unit test cho module M3.
    """

    print("\n" + "#" * 60)
    print("UNIT TEST - MODULE M3")
    print("#" * 60)

    # =======================================================
    # TEST 1 - Testcase chính
    # =======================================================

    C = 100
    p = 0.2
    tau_0 = 0.05
    max_limit = 10000

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C, p, tau_0, max_limit
    )

    assert M_star == 116

    risk_116 = tinh_rui_ro(116, C, p)
    risk_117 = tinh_rui_ro(117, C, p)

    assert risk_116 <= tau_0
    assert risk_117 > tau_0

    print("[PASS] Test 1 - C=100, p=0.2, tau_0=0.05")

    # =======================================================
    # TEST 2 - p = 0
    # =======================================================

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=100,
        p=0,
        tau_0=0.05
    )

    assert M_star == 100

    print("[PASS] Test 2 - p=0")

    # =======================================================
    # TEST 3 - p = 1
    # =======================================================

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=100,
        p=1,
        tau_0=0.05
    )

    assert M_star == 10000

    print("[PASS] Test 3 - p=1")

    # =======================================================
    # TEST 4 - tau_0 = 0
    # =======================================================

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=100,
        p=0.2,
        tau_0=0
    )

    assert M_star == 100

    print("[PASS] Test 4 - tau_0=0")

    # =======================================================
    # TEST 5 - C = 0, p = 1
    # =======================================================

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=0,
        p=1,
        tau_0=0.05
    )

    assert M_star == 10000

    print("[PASS] Test 5 - C=0, p=1")

    # =======================================================
    # TEST 6 - tau_0 = 1
    # =======================================================

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=100,
        p=0.2,
        tau_0=1
    )

    assert M_star == 10000

    print("[PASS] Test 6 - tau_0=1")

    # =======================================================
    # TEST 7 - p không hợp lệ
    # =======================================================

    try:
        tim_kiem_nhi_phan_nguong_ban_lo(
            C=100,
            p=1.2,
            tau_0=0.05
        )
        assert False, "Phải phát sinh ValueError."
    except ValueError:
        print("[PASS] Test 7 - p khong hop le")

    # =======================================================
    # TEST 8 - tau_0 không hợp lệ
    # =======================================================

    try:
        tim_kiem_nhi_phan_nguong_ban_lo(
            C=100,
            p=0.2,
            tau_0=1.5
        )
        assert False, "Phải phát sinh ValueError."
    except ValueError:
        print("[PASS] Test 8 - tau_0 khong hop le")

    # =======================================================
    # TEST 9 - max_limit < C
    # =======================================================

    try:
        tim_kiem_nhi_phan_nguong_ban_lo(
            C=100,
            p=0.2,
            tau_0=0.05,
            max_limit=50
        )
        assert False, "Phải phát sinh ValueError."
    except ValueError:
        print("[PASS] Test 9 - max_limit < C")

    print("\n" + "#" * 60)
    print("TAT CA UNIT TEST DA HOAN THANH")
    print("#" * 60)


if __name__ == "__main__":

    # Testcase chính theo yêu cầu
    hien_thi_ket_qua(
        C=100,
        p=0.2,
        tau_0=0.05,
        max_limit=10000
    )

    # Kiểm thử toàn bộ
    unit_test()
