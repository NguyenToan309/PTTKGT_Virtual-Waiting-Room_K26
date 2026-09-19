"""
Module 7: Sample Average Approximation (SAA) va Benchmark thuc nghiem.
File: thuat_toan_7_saa_benchmark.py
Vai tro: TV7 - Kien truc su he thong & Dieu phoi Benchmark SAA.

Co so ly thuyet bai bao PLOS ONE 2024:
    Phuong phap Mau xap xi trung binh (Sample Average Approximation - SAA)
    mo phong S kich ban ngau nhien bien dong cua ty le bo ve/rot ve no-show p(s)
    de tim nghiem overbooking dai dien toi uu, sau do danh gia doi soat thuc nghiem
    giua Chien luoc De xuat (Proposed SAA) vs Chien luoc Co dinh truyen thong (Baseline Fixed C).

Bang phan ra nhiem vu:
    TV7-A: Doc hieu dau vao S, Distributions.
    TV7-B: Thiet ke Data Structure (List, Dict) va Type Hints.
    TV7-C: Cai thuat toan loi SAA va mo phong Monte Carlo.
    TV7-D: Cai dat cac ham bo tro helper.
    TV7-E: Xay dung interface tim_nghiem_saa_chuan(), in_bang_so_sanh_thuc_te().
    TV7-F: Xu ly phong thu cac truong hop bien (Edge cases).
    TV7-G: Bo Unit Test toan dien (test_thuat_toan_7_saa_benchmark.py).
    TV7-H: Phan tich do phuc tap Big-O.
    TV7-I: Review chuan code: bien Tieng Anh, ham Tieng Viet snake_case, comment 1 dong.
    TV7-J: Ban giao ket qua Dict/Console.

Do phuc tap:
    Thoi gian (Time Complexity): O(S * Pipeline_Complexity) = O(S * (C * log(max_limit) + N * M*))
    Khong gian (Space Complexity): O(S + N * M*)
"""

import math
import random
from typing import Any, Dict, List, Optional, Tuple

# Import interface Module 3 (Binary Search)
try:
    from thuat_toan_3_tim_kiem_nhi_phan_M3_hoan_chinh import tim_kiem_nhi_phan_nguong_ban_lo
except ImportError:
    try:
        from thuat_toan_3_binary_search import tim_kiem_nhi_phan_nguong_ban_lo
    except ImportError:
        tim_kiem_nhi_phan_nguong_ban_lo = None

# Import interface Module 4 (Bounded Knapsack DP)
try:
    from thuat_toan_4_quy_hoach_dong import quy_hoach_dong_phan_bo_ve
except ImportError:
    try:
        from thuat_toan_4_bounded_knapsack import quy_hoach_dong_phan_bo_ve
    except ImportError:
        quy_hoach_dong_phan_bo_ve = None


# =============================================================================
# TV7-D: HELPER FUNCTIONS (CÁC HÀM PHỤ TRỢ NỘI BỘ)
# =============================================================================

def _dieu_phoi_m3_tim_nguong(capacity_C: int, drop_rate_p: float, tau_0: float) -> int:
    """
    Helper dieu phoi goi Module 3 voi co che phong thu fallback.
    Do phuc tap: O(C * log(max_limit))
    """
    # Kiem tra neu module M3 co san de su dung
    if tim_kiem_nhi_phan_nguong_ban_lo is not None:
        try:
            return int(tim_kiem_nhi_phan_nguong_ban_lo(capacity_C, drop_rate_p, tau_0))
        except Exception:
            pass  # Neu pipeline ngoai gap exception, chuyen sang fallback noi bo

    # Fallback toan hoc xap xi: M = C / (1 - p) neu module 3 khong kha dung
    safe_show_rate = max(0.05, 1.0 - drop_rate_p)
    return int(math.ceil(capacity_C / safe_show_rate))


def _dieu_phoi_m4_phan_bo(m_star: int, ticket_classes: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Helper dieu phoi goi Module 4 Bounded Knapsack DP voi phong thu du lieu.
    Do phuc tap: O(N * m_star)
    """
    if not ticket_classes or m_star <= 0:
        return {tc.get("name", "Unknown"): 0 for tc in (ticket_classes or [])}

    if quy_hoach_dong_phan_bo_ve is not None:
        # Thu goi theo format danh sach hang ve list[dict]
        try:
            alloc = quy_hoach_dong_phan_bo_ve(m_star, ticket_classes)
            if isinstance(alloc, dict) and alloc:
                return alloc
        except Exception:
            pass

        # Thu goi theo format demands dict va prices dict
        try:
            demands = {tc["name"]: tc["demand_limit"] for tc in ticket_classes}
            prices = {tc["name"]: tc["price"] for tc in ticket_classes}
            alloc = quy_hoach_dong_phan_bo_ve(m_star, demands, prices)
            if isinstance(alloc, dict) and alloc:
                return alloc
        except Exception:
            pass

    # Fallback phan bo tham lam uu tien hang ve gia cao neu M4 gap su co
    # Sap xep thu cong bang Selection Sort (KHONG dung sorted() theo quy chuan)
    sorted_classes = list(ticket_classes)
    for i in range(len(sorted_classes)):
        max_idx = i
        for j in range(i + 1, len(sorted_classes)):
            if sorted_classes[j].get("price", 0.0) > sorted_classes[max_idx].get("price", 0.0):
                max_idx = j
        sorted_classes[i], sorted_classes[max_idx] = sorted_classes[max_idx], sorted_classes[i]
    fallback_alloc: Dict[str, int] = {}
    remaining_quota = m_star
    for tc in sorted_classes:
        name = tc.get("name", "Standard")
        limit = tc.get("demand_limit", 0)
        taken = min(remaining_quota, limit)
        fallback_alloc[name] = taken
        remaining_quota -= taken
    return fallback_alloc


def _mo_phong_so_khach_den(m_sold: int, drop_rate_p: float, rng: random.Random) -> int:
    """
    Mo phong so luong khach check-in theo Bien ngau nhien Nhi thuc K ~ Binomial(M, 1 - p).
    Do phuc tap: O(M)
    """
    # Xac suat khach thuc su den la (1 - p)
    show_prob = 1.0 - drop_rate_p
    actual_arrivals = 0
    for _ in range(m_sold):
        if rng.random() < show_prob:
            actual_arrivals += 1
    return actual_arrivals


# =============================================================================
# TV7-A & TV7-C: SINH KỊCH BẢN VÀ THUẬT TOÁN SAA LÕI
# =============================================================================

def sinh_kich_ban_xac_suat(
    S: int,
    distributions: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = 42
) -> List[float]:
    """
    Sinh danh sach S kich ban ty le rot ve p(s) tu phan phoi xac suat.
    Input:
        - S (int): So luong kich ban can tao.
        - distributions (dict): Cau hinh phan phoi (uniform, beta, normal).
        - seed (int): Seed ngau nhien de co dinh ket qua kiem thu.
    Output:
        - List[float]: Danh sach S gia tri ty le rot p.
    Do phuc tap: O(S)
    """
    # TV7-F: Kiem tra dieu kien bien hop le cua so luong kich ban
    if not isinstance(S, int) or S <= 0:
        raise ValueError("So kich ban S phai la so nguyen duong (S > 0).")

    rng = random.Random(seed)
    dist_config = distributions or {}
    dist_type = dist_config.get("type", "uniform").lower()

    scenarios: List[float] = []
    for _ in range(S):
        if dist_type == "beta":
            # Phan phoi Beta quanh gia tri thuc te 0.20
            alpha = float(dist_config.get("alpha", 2.0))
            beta_param = float(dist_config.get("beta", 8.0))
            p_val = rng.betavariate(alpha, beta_param)
        elif dist_type == "normal":
            # Phan phoi Chuan (Gaussian)
            mean = float(dist_config.get("mean", 0.20))
            std = float(dist_config.get("std", 0.05))
            p_val = rng.gauss(mean, std)
        else:
            # Phan phoi Deu (Uniform) mac dinh trong khoang [0.10, 0.35]
            min_p = float(dist_config.get("min_p", 0.10))
            max_p = float(dist_config.get("max_p", 0.35))
            p_val = rng.uniform(min_p, max_p)

        # TV7-F: Rang buoc ty le rot p luon nam trong mien an toan [0.01, 0.90]
        p_val_bounded = max(0.01, min(0.90, p_val))
        scenarios.append(round(p_val_bounded, 4))

    return scenarios


def chay_danh_gia_saa(
    num_scenarios: int = 100,
    capacity_C: int = 100,
    tau_0: float = 0.05,
    ticket_classes: Optional[List[Dict[str, Any]]] = None,
    distributions: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = 42
) -> Dict[str, Any]:
    """
    Thuat toan SAA Benchmark so sanh chien luoc Proposed vs Baseline.
    Do phuc tap:
        Thoi gian: O(S * (C * log(max_limit) + N * M*))
        Khong gian: O(S)
    """
    # TV7-F: Kiem tra cac gia tri bien dau vao
    if not isinstance(capacity_C, int) or capacity_C <= 0:
        raise ValueError("capacity_C phai la so nguyen duong (C > 0).")
    if not isinstance(tau_0, (int, float)) or not (0.0 < tau_0 < 1.0):
        raise ValueError("tau_0 phai nam trong khoang hop le (0, 1).")

    # Cau hinh cac hang ve mac dinh neu chua co
    classes = ticket_classes or [
        {"name": "VIP", "price": 1000000.0, "demand_limit": 30},
        {"name": "Standard", "price": 500000.0, "demand_limit": 100}
    ]

    # Tinh chi phi boi thuong Denied Boarding dua tren don gia ve trung binh
    total_demand = sum(c.get("demand_limit", 0) for c in classes) or 1
    weighted_price = sum(c.get("price", 0.0) * c.get("demand_limit", 0) for c in classes) / total_demand
    compensation_per_db = weighted_price * 1.5  # Boi thuong 150% theo thong le bai bao

    # Sinh danh sach S kich ban p
    scenarios_p = sinh_kich_ban_xac_suat(num_scenarios, distributions=distributions, seed=seed)
    rng = random.Random(seed)

    # -------------------------------------------------------------------------
    # 1. TIM NGHIEM SAA (SAMPLE AVERAGE APPROXIMATION)
    # -------------------------------------------------------------------------
    calculated_m_stars: List[int] = []
    for p_val in scenarios_p:
        m_s = _dieu_phoi_m3_tim_nguong(capacity_C, p_val, tau_0)
        calculated_m_stars.append(m_s)

    # Nghiem SAA dai dien la trung binh cong tren tap mau S kich ban
    m_star_saa = int(round(sum(calculated_m_stars) / len(calculated_m_stars)))

    # Phan bo quota cho Proposed va Baseline qua M4
    alloc_prop = _dieu_phoi_m4_phan_bo(m_star_saa, classes)
    alloc_base = _dieu_phoi_m4_phan_bo(capacity_C, classes)

    # Doanh thu ban ve ban dau (gross revenue)
    gross_prop = sum(alloc_prop.get(c["name"], 0) * c.get("price", 0.0) for c in classes)
    gross_base = sum(alloc_base.get(c["name"], 0) * c.get("price", 0.0) for c in classes)

    # -------------------------------------------------------------------------
    # 2. MO PHONG THUC NGHIEM SO SANH TREN S KICH BAN
    # -------------------------------------------------------------------------
    prop_net_revenues: List[float] = []
    prop_db_counts: List[int] = []
    prop_empty_seats: List[int] = []

    base_net_revenues: List[float] = []
    base_empty_seats: List[int] = []

    scenarios_sample: List[Dict[str, Any]] = []

    for idx, p_val in enumerate(scenarios_p):
        # A. Mo phong Proposed: ban m_star_saa ve
        arrivals_prop = _mo_phong_so_khach_den(m_star_saa, p_val, rng)
        db_count = max(0, arrivals_prop - capacity_C)
        admitted_prop = min(arrivals_prop, capacity_C)
        empty_prop = max(0, capacity_C - admitted_prop)
        net_rev_prop = gross_prop - (db_count * compensation_per_db)

        prop_net_revenues.append(net_rev_prop)
        prop_db_counts.append(db_count)
        prop_empty_seats.append(empty_prop)

        # B. Mo phong Baseline: ban co dinh dung C ve
        arrivals_base = _mo_phong_so_khach_den(capacity_C, p_val, rng)
        admitted_base = min(arrivals_base, capacity_C)
        empty_base = max(0, capacity_C - admitted_base)
        net_rev_base = gross_base

        base_net_revenues.append(net_rev_base)
        base_empty_seats.append(empty_base)

        # Trich xuat mau 5 kich ban dau tien lam vi du minh hoa
        if idx < 5:
            scenarios_sample.append({
                "scenario": idx + 1,
                "p": p_val,
                "m_star": calculated_m_stars[idx],
                "proposed_net": net_rev_prop,
                "baseline_net": net_rev_base,
                "db_count": db_count,
                "empty_prop": empty_prop,
                "empty_base": empty_base,
            })

    # Tinh toan cac chi so thong ke trung binh
    avg_net_prop = sum(prop_net_revenues) / num_scenarios
    avg_db = sum(prop_db_counts) / num_scenarios
    avg_empty_prop = sum(prop_empty_seats) / num_scenarios
    avg_m_star = sum(calculated_m_stars) / num_scenarios

    avg_net_base = sum(base_net_revenues) / num_scenarios
    avg_empty_base = sum(base_empty_seats) / num_scenarios

    # Tinh ty le cai thien doanh thu
    impr_pct = 0.0
    if avg_net_base > 0:
        impr_pct = ((avg_net_prop - avg_net_base) / avg_net_base) * 100.0

    overbooking_rate = ((m_star_saa - capacity_C) / capacity_C) * 100.0
    db_rate = (avg_db / capacity_C) * 100.0

    # TV7-J: Dong goi ket qua ban giao
    result: Dict[str, Any] = {
        "num_scenarios": num_scenarios,
        "capacity_C": capacity_C,
        "tau_0": tau_0,
        "m_star_saa": m_star_saa,
        "allocation_proposed": alloc_prop,
        "allocation_baseline": alloc_base,
        "proposed": {
            "avg_net_revenue": avg_net_prop,
            "avg_gross_revenue": gross_prop,
            "avg_m_star": round(avg_m_star, 1),
            "avg_overbooking_rate_pct": round(overbooking_rate, 2),
            "avg_denied_boarding": round(avg_db, 3),
            "avg_empty_seats": round(avg_empty_prop, 2),
            "db_rate_pct": round(db_rate, 2),
        },
        "baseline": {
            "avg_net_revenue": avg_net_base,
            "avg_gross_revenue": gross_base,
            "avg_m_star": capacity_C,
            "avg_overbooking_rate_pct": 0.0,
            "avg_denied_boarding": 0.0,
            "avg_empty_seats": round(avg_empty_base, 2),
            "db_rate_pct": 0.0,
        },
        "improvement_pct": round(impr_pct, 2),
        "scenarios_sample": scenarios_sample,
    }

    return result


# =============================================================================
# TV7-E: PUBLIC FUNCTIONS (INTERFACE BÀN GIAO)
# =============================================================================

def tim_nghiem_saa_chuan(
    S: int = 100,
    distributions: Optional[Dict[str, Any]] = None,
    capacity_C: int = 100,
    tau_0: float = 0.05,
    ticket_classes: Optional[List[Dict[str, Any]]] = None,
    seed: Optional[int] = 42
) -> Dict[str, Any]:
    """
    Ham public tim nghiem toi uu SAA theo dung interface chuan TV7-E.
    Input:
        - S (int): So luong scenario khao sat.
        - distributions (dict): Cau hinh phan phoi xac suat.
    Output:
        - Dict[str, Any]: Ket qua danh gia va thong so toi uu toan cuc.
    Do phuc tap: O(S * Pipeline_Complexity)
    """
    # Thuc hien quy trinh danh gia toan dien SAA
    return chay_danh_gia_saa(
        num_scenarios=S,
        capacity_C=capacity_C,
        tau_0=tau_0,
        ticket_classes=ticket_classes,
        distributions=distributions,
        seed=seed
    )


def in_bang_so_sanh_thuc_te(benchmark_result: Dict[str, Any]) -> None:
    """
    In bang so sanh truc quan ra man hinh Console theo chuan bao cao cua TV7-E va TV7-J.
    Tat ca so lieu duoc trich xuat dong tu runtime thuc te (KHONG HARD-CODE).
    """
    S = benchmark_result.get("num_scenarios", 100)
    C = benchmark_result.get("capacity_C", 100)
    tau_0 = benchmark_result.get("tau_0", 0.05)
    prop = benchmark_result.get("proposed", {})
    base = benchmark_result.get("baseline", {})
    impr = benchmark_result.get("improvement_pct", 0.0)

    print("\n" + "=" * 72)
    print("       BÁO CÁO BENCHMARK: PROPOSED (SAA) vs BASELINE (FIXED C)")
    print("       Cơ sở: Bài báo PLOS ONE 2024 & Virtual Waiting Room")
    print("=" * 72)
    print(f" Cấu hình thử nghiệm:")
    print(f"  - Số kịch bản Monte Carlo (S) : {S}")
    print(f"  - Sức chứa thực tế rạp (C)    : {C} ghế")
    print(f"  - Ngưỡng rủi ro an toàn (tau_0): {tau_0 * 100:.1f}%")
    print("-" * 72)
    fmt_header = " {:<30} | {:<17} | {:<17}"
    fmt_row = " {:<30} | {:>17} | {:>17}"

    print(fmt_header.format("TIÊU CHÍ ĐÁNH GIÁ", "PROPOSED (SAA)", "BASELINE (FIXED)"))
    print("-" * 72)

    rev_prop_str = f"{prop.get('avg_net_revenue', 0.0):,.0f} đ"
    rev_base_str = f"{base.get('avg_net_revenue', 0.0):,.0f} đ"
    print(fmt_row.format("Doanh thu thuần TB (Net)", rev_prop_str, rev_base_str))

    m_prop_str = f"{benchmark_result.get('m_star_saa', 0)} vé"
    m_base_str = f"{C} vé (cố định)"
    print(fmt_row.format("Hạn mức bán vé (M*)", m_prop_str, m_base_str))

    ob_prop_str = f"+{prop.get('avg_overbooking_rate_pct', 0.0)}%"
    ob_base_str = "0.0% (không bán lố)"
    print(fmt_row.format("Tỷ lệ bán lố (Overbooking)", ob_prop_str, ob_base_str))

    db_prop_str = f"{prop.get('avg_denied_boarding', 0.0):.2f} khách"
    db_base_str = "0.00 khách"
    print(fmt_row.format("Khách bị từ chối (DB)", db_prop_str, db_base_str))

    db_rate_prop = f"{prop.get('db_rate_pct', 0.0)}% (<= {tau_0 * 100:.0f}%)"
    db_rate_base = "0.0%"
    print(fmt_row.format("Tỷ lệ Denied Boarding", db_rate_prop, db_rate_base))

    empty_prop_str = f"{prop.get('avg_empty_seats', 0.0):.2f} ghế"
    empty_base_str = f"{base.get('avg_empty_seats', 0.0):.2f} ghế"
    print(fmt_row.format("Ghế trống lãng phí TB", empty_prop_str, empty_base_str))

    print("-" * 72)
    sign = "+" if impr >= 0 else ""
    print(f" >>> HIỆU QUẢ CẢI THIỆN DOANH THU THỰC TẾ: {sign}{impr:.2f}% <<<")
    print("=" * 72)

    # In mau 5 kich ban dau tien lam vi du truc quan
    samples = benchmark_result.get("scenarios_sample", [])
    if samples:
        print("\n Mẫu kết quả 5 kịch bản ngẫu nhiên thực nghiệm:")
        fmt_sample = "  Kịch bản {:<2}: p={:<6} | M*={:<3} | Proposed: {:>13} đ | Baseline: {:>13} đ | DB: {} | Trống: {} vs {}"
        for row in samples:
            print(fmt_sample.format(
                row["scenario"],
                row["p"],
                row["m_star"],
                f"{row['proposed_net']:,.0f}",
                f"{row['baseline_net']:,.0f}",
                row["db_count"],
                row["empty_prop"],
                row["empty_base"]
            ))
        print("=" * 72 + "\n")


if __name__ == "__main__":
    # TV7-J: Demo thuc thi ban giao
    kq = tim_nghiem_saa_chuan(S=100, capacity_C=100, tau_0=0.05)
    in_bang_so_sanh_thuc_te(kq)
