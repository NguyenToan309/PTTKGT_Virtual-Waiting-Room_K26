"""
M3 - Binary Search on Answer Space
Project: Overbooking & Seat Allocation

Mục tiêu:
Tìm mức bán lố an toàn M_star lớn nhất sao cho:

    P(K > C) <= tau_0

Trong đó:
    K ~ Binomial(M, 1-p)

C: sức chứa thực tế
p: tỷ lệ khách không đến
tau_0: mức rủi ro tối đa cho phép
M_star: số vé tối đa có thể bán an toàn

Python 3.10+
"""

import math
from typing import List


def xac_suat_khong_vuot_suc_chua(
    M: int,
    C: int,
    p: float
) -> float:
    """
    Tính P(K <= C), với K ~ Binomial(M, 1-p).
    """

    if M < 0:
        raise ValueError("M phải >= 0")

    if C < 0:
        raise ValueError("C phải >= 0")

    if not 0 <= p <= 1:
        raise ValueError("p phải nằm trong [0, 1]")

    # Nếu số vé bán không vượt sức chứa
    if M <= C:
        return 1.0

    q = 1.0 - p

    # Không có khách nào xuất hiện
    if q == 0:
        return 1.0

    # Tất cả khách đều xuất hiện
    if q == 1:
        return 0.0

    # P(K <= C) = tổng P(K = k), k = 0..C
    log_probabilities: List[float] = []

    upper_k = min(C, M)

    for k in range(upper_k + 1):
        log_combination = (
            math.lgamma(M + 1)
            - math.lgamma(k + 1)
            - math.lgamma(M - k + 1)
        )

        log_probability = (
            log_combination
            + k * math.log(q)
            + (M - k) * math.log(1.0 - q)
        )

        log_probabilities.append(log_probability)

    # Log-Sum-Exp để giảm sai số số thực
    max_log = max(log_probabilities)

    total = sum(
        math.exp(value - max_log)
        for value in log_probabilities
    )

    return math.exp(max_log) * total


def xac_suat_qua_tai(
    M: int,
    C: int,
    p: float
) -> float:
    """
    Tính xác suất quá tải:

        P(K > C) = 1 - P(K <= C)
    """

    probability = 1.0 - xac_suat_khong_vuot_suc_chua(
        M,
        C,
        p
    )

    # Giới hạn kết quả trong [0, 1]
    return max(0.0, min(1.0, probability))


def tim_kiem_nhi_phan_nguong_ban_lo(
    C: int,
    p: float,
    tau_0: float,
    max_limit: int = 10000
) -> int:
    """
    Binary Search on Answer Space.

    Tìm M_star lớn nhất thỏa:

        P(K > C) <= tau_0

    Input:
        C: sức chứa
        p: tỷ lệ khách không đến
        tau_0: mức rủi ro cho phép
        max_limit: giới hạn trên của số vé

    Output:
        M_star: mức bán lố tối đa an toàn
    """

    if C < 0:
        raise ValueError("C phải >= 0")

    if not 0 <= p <= 1:
        raise ValueError("p phải nằm trong [0, 1]")

    if not 0 < tau_0 < 1:
        raise ValueError("tau_0 phải nằm trong (0, 1)")

    if max_limit < C:
        raise ValueError("max_limit phải >= C")

    # p = 0: tất cả khách đều xuất hiện
    # Không thể bán vượt sức chứa.
    if p == 0:
        return C

    # p = 1: không có khách nào xuất hiện
    if p == 1:
        return max_limit

    # Không gian nghiệm
    left = C
    right = max_limit

    # Nghiệm hợp lệ tốt nhất
    M_star = C

    while left <= right:
        # Chia đôi không gian nghiệm
        mid = (left + right) // 2

        # Tính rủi ro quá tải tại mid
        risk = xac_suat_qua_tai(
            M=mid,
            C=C,
            p=p
        )

        if risk <= tau_0:
            # mid hợp lệ -> thử bán nhiều hơn
            M_star = mid
            left = mid + 1
        else:
            # mid không hợp lệ -> giảm số vé
            right = mid - 1

    return M_star


def demo_m3() -> None:
    """
    Testcase theo yêu cầu M3:
        C = 100
        p = 0.2
        tau_0 = 0.05
    """

    C = 100
    p = 0.2
    tau_0 = 0.05

    M_star = tim_kiem_nhi_phan_nguong_ban_lo(
        C=C,
        p=p,
        tau_0=tau_0
    )

    risk_at_m_star = xac_suat_qua_tai(
        M=M_star,
        C=C,
        p=p
    )

    risk_next = xac_suat_qua_tai(
        M=M_star + 1,
        C=C,
        p=p
    )

    print("=" * 60)
    print("M3 - BINARY SEARCH ON ANSWER SPACE")
    print("=" * 60)
    print(f"Sức chứa C              : {C}")
    print(f"Tỷ lệ khách không đến p : {p}")
    print(f"Rủi ro cho phép tau_0   : {tau_0}")
    print("-" * 60)
    print(f"M_star                  : {M_star}")
    print(f"P(K > C) tại M_star     : {risk_at_m_star:.6f}")
    print(f"P(K > C) tại M_star+1   : {risk_next:.6f}")
    print("-" * 60)

    if risk_at_m_star <= tau_0:
        print("M_star thỏa điều kiện rủi ro.")

    if risk_next > tau_0:
        print("M_star + 1 vượt mức rủi ro cho phép.")

    print("=" * 60)


if __name__ == "__main__":
    demo_m3()
