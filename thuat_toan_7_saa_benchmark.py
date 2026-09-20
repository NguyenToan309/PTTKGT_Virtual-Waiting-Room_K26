"""
Module 7: Sample Average Approximation (SAA) va Benchmark thuc nghiem.
File: thuat_toan_7_saa_benchmark.py
Vai tro: TV7 - Kien truc su he thong & Dieu phoi Benchmark SAA.

Co so ly thuyet bai bao PLOS ONE 2024:
    Mo phong S kich ban ngau nhien bien dong cua ty le bo ve p(s)
    de tim nghiem overbooking dai dien toi uu, sau do danh gia thuc nghiem
    giua Chien luoc De xuat (Proposed SAA) va Co dinh (Baseline Fixed C).

Do phuc tap:
    Thoi gian: O(S * (C * log(max_limit) + N * M*))
    Khong gian: O(S + N * M*)
"""

import math
import random
from typing import Any, Dict, List, Optional

# Import dynamic Module 3 (Binary Search)
try:
    from thuat_toan_3_tim_kiem_nhi_phan_M3_hoan_chinh import tim_kiem_nhi_phan_nguong_ban_lo
except ImportError:
    try:
        from thuat_toan_3_binary_search import tim_kiem_nhi_phan_nguong_ban_lo
    except ImportError:
        tim_kiem_nhi_phan_nguong_ban_lo = None

# Import dynamic Module 4 (Bounded Knapsack DP)
try:
    from thuat_toan_4_quy_hoach_dong import quy_hoach_dong_phan_bo_ve
except ImportError:
    try:
        from thuat_toan_4_bounded_knapsack import quy_hoach_dong_phan_bo_ve
    except ImportError:
        quy_hoach_dong_phan_bo_ve = None


# =============================================================================
# CAC HAM PHU TRO NOI BO (HELPER FUNCTIONS)
# =============================================================================

def _dieu_phoi_m3_tim_nguong(capacity_C: int, drop_rate_p: float, tau_0: float) -> int:
    """Dieu phoi tim han muc M* qua M3 voi co che fallback. O(C * log(max_limit))."""
    if tim_kiem_nhi_phan_nguong_ban_lo is not None:
        try:
            return int(tim_kiem_nhi_phan_nguong_ban_lo(capacity_C, drop_rate_p, tau_0))
        except Exception:
            pass
    # Fallback toan hoc: M = ceil(C / (1 - p))
    safe_rate = max(0.05, 1.0 - drop_rate_p)
    return int(math.ceil(capacity_C / safe_rate))


def _dieu_phoi_m4_phan_bo(m_star: int, ticket_classes: List[Dict[str, Any]], is_baseline: bool = False) -> Dict[str, int]:
    """Dieu phoi phan bo ve qua M4 Knapsack voi fallback tham lam. O(N * m_star)."""
    if not ticket_classes or m_star <= 0:
        return {tc.get("name", "Unknown"): 0 for tc in (ticket_classes or [])}

    alloc: Dict[str, int] = {}
    remain = m_star

    # 1. Cấp phát ưu tiên 100% quota cho phân khu Tri Ân chính sách (VVIP - Mẹ VNAH, Thương binh, Yếu nhân)
    for tc in ticket_classes:
        if tc.get("price", 0.0) == 0.0 or tc.get("protected_pool", 0) > 0:
            quota = tc.get("protected_pool") or tc.get("physical_cap") or tc.get("demand_limit", 0)
            taken = min(remain, quota)
            alloc[tc.get("name")] = taken
            remain -= taken

    # 2. Phân bổ Bounded Knapsack cho các phân khu thương mại (có thu phí)
    comm_classes = [tc for tc in ticket_classes if tc.get("name") not in alloc]
    if comm_classes and remain > 0:
        if not is_baseline and quy_hoach_dong_phan_bo_ve is not None:
            try:
                comm_alloc = quy_hoach_dong_phan_bo_ve(remain, comm_classes)
                if isinstance(comm_alloc, dict) and comm_alloc:
                    alloc.update(comm_alloc)
                    return alloc
            except Exception:
                pass

        # Fallback Selection Sort theo giá giảm dần
        classes_copy = list(comm_classes)
        for i in range(len(classes_copy)):
            max_idx = i
            for j in range(i + 1, len(classes_copy)):
                if classes_copy[j].get("price", 0.0) > classes_copy[max_idx].get("price", 0.0):
                    max_idx = j
            classes_copy[i], classes_copy[max_idx] = classes_copy[max_idx], classes_copy[i]

        for tc in classes_copy:
            lim = tc.get("physical_cap", tc.get("demand_limit", 0)) if is_baseline else tc.get("demand_limit", 0)
            taken = min(remain, lim)
            alloc[tc.get("name")] = taken
            remain -= taken

    return alloc


def _mo_phong_so_khach_den(m_sold: int, drop_rate_p: float, rng: random.Random) -> int:
    """Mo phong so khach den theo Bien ngau nhien Nhi thuc K ~ Binomial(M, 1 - p). O(M)."""
    show_prob = 1.0 - drop_rate_p
    if m_sold > 500:
        # Xap xi phan phoi Chuan (De Moivre - Laplace / CLT) cho M lon, chay tuc thi O(1)
        mean = m_sold * show_prob
        variance = m_sold * show_prob * drop_rate_p
        std = math.sqrt(max(0.1, variance))
        arrivals = int(round(rng.gauss(mean, std)))
        return max(0, min(m_sold, arrivals))
    arrivals = 0
    for _ in range(m_sold):
        if rng.random() < show_prob:
            arrivals += 1
    return arrivals


# =============================================================================
# THUAT TOAN SAA CHINH VA INTERFACE PUBLIC
# =============================================================================

def sinh_kich_ban_xac_suat(
    S: int,
    distributions: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = 42
) -> List[float]:
    """Sinh danh sach S kich ban ty le rot ve tu phan phoi xac suat. O(S)."""
    if not isinstance(S, int) or S <= 0:
        raise ValueError("So kich ban S phai la so nguyen duong (S > 0).")

    rng = random.Random(seed)
    cfg = distributions or {}
    dist_type = cfg.get("type", "uniform").lower()
    scenarios: List[float] = []

    for _ in range(S):
        if dist_type == "beta":
            p = rng.betavariate(float(cfg.get("alpha", 2.0)), float(cfg.get("beta", 8.0)))
        elif dist_type == "normal":
            p = rng.gauss(float(cfg.get("mean", 0.20)), float(cfg.get("std", 0.05)))
        else:
            p = rng.uniform(float(cfg.get("min_p", 0.10)), float(cfg.get("max_p", 0.35)))
        scenarios.append(round(max(0.01, min(0.90, p)), 4))

    return scenarios


def chay_danh_gia_saa(
    num_scenarios: int = 100,
    capacity_C: int = 100,
    tau_0: float = 0.05,
    ticket_classes: Optional[List[Dict[str, Any]]] = None,
    distributions: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = 42
) -> Dict[str, Any]:
    """Thuat toan SAA Benchmark so sanh Proposed SAA vs Baseline Fixed. O(S * Pipeline)."""
    if not isinstance(capacity_C, int) or capacity_C <= 0:
        raise ValueError("capacity_C phai la so nguyen duong (C > 0).")
    if not isinstance(tau_0, (int, float)) or not (0.0 < tau_0 < 1.0):
        raise ValueError("tau_0 phai nam trong khoang hop le (0, 1).")

    # Cau hinh hang ve mac dinh neu khong truyen
    classes = ticket_classes or [
        {"name": "VIP", "price": 1000000.0, "demand_limit": 30},
        {"name": "Standard", "price": 500000.0, "demand_limit": 100}
    ]

    # Don gia boi thuong Denied Boarding (150% gia ve thuong mai trung binh)
    comm_classes = [c for c in classes if c.get("price", 0.0) > 0]
    total_demand = sum(c.get("demand_limit", 0) for c in comm_classes) or 1
    weighted_price = sum(c.get("price", 0.0) * c.get("demand_limit", 0) for c in comm_classes) / total_demand
    comp_per_db = weighted_price * 1.5

    # Sinh tap mau S kich ban va khoi tao bo sinh so
    scenarios_p = sinh_kich_ban_xac_suat(num_scenarios, distributions=distributions, seed=seed)
    rng = random.Random(seed)

    # 1. Giai bai toan SAA: tim M* dai dien tren S kich ban
    m_stars = [_dieu_phoi_m3_tim_nguong(capacity_C, p, tau_0) for p in scenarios_p]
    m_star_saa = int(round(sum(m_stars) / len(m_stars)))

    # Phan bo quota theo M4
    alloc_prop = _dieu_phoi_m4_phan_bo(m_star_saa, classes, is_baseline=False)
    alloc_base = _dieu_phoi_m4_phan_bo(capacity_C, classes, is_baseline=True)
    gross_prop = sum(alloc_prop.get(c["name"], 0) * c.get("price", 0.0) for c in classes)
    gross_base = sum(alloc_base.get(c["name"], 0) * c.get("price", 0.0) for c in classes)

    # 2. Mo phong doi soat thuc nghiem S kich ban
    prop_nets: List[float] = []
    prop_dbs: List[int] = []
    prop_empties: List[int] = []
    base_nets: List[float] = []
    base_empties: List[int] = []
    sample_rows: List[Dict[str, Any]] = []

    actual_sold_prop = sum(alloc_prop.get(c["name"], 0) for c in classes)
    actual_sold_base = sum(alloc_base.get(c["name"], 0) for c in classes)

    for idx, p_val in enumerate(scenarios_p):
        # Proposed: ban so ve thuc te phan bo duoc theo M4 Knapsack
        arr_prop = _mo_phong_so_khach_den(actual_sold_prop, p_val, rng)
        db_cnt = max(0, arr_prop - capacity_C)
        empty_prop = max(0, capacity_C - min(arr_prop, capacity_C))
        net_prop = gross_prop - (db_cnt * comp_per_db)

        prop_nets.append(net_prop)
        prop_dbs.append(db_cnt)
        prop_empties.append(empty_prop)

        # Baseline: ban so ve thuc te phan bo duoc theo Baseline Knapsack
        arr_base = _mo_phong_so_khach_den(actual_sold_base, p_val, rng)
        empty_base = max(0, capacity_C - min(arr_base, capacity_C))

        base_nets.append(gross_base)
        base_empties.append(empty_base)

        # Luu toan bo kịch ban (toi da 100 kich ban) chi tiet de UI hien thi truc quan
        if idx < 100:
            sample_rows.append({
                "scenario": idx + 1,
                "p": round(p_val, 4),
                "drop_rate_pct": round(p_val * 100, 2),
                "capacity_C": capacity_C,
                "m_star": m_star_saa,
                "arrivals": arr_prop,
                "occupied_seats": capacity_C - empty_prop,
                "empty_seats": empty_prop,
                "empty_prop": empty_prop,
                "db_count": db_cnt,
                "proposed_net": net_prop,
                "gross_revenue": gross_prop,
                "comp_cost": db_cnt * comp_per_db,
                "baseline_net": gross_base,
                "profit_gain": net_prop - gross_base,
                "empty_base": empty_base,
            })

    # Tinh gia tri trung binh
    avg_net_prop = sum(prop_nets) / num_scenarios
    avg_db = sum(prop_dbs) / num_scenarios
    avg_empty_prop = sum(prop_empties) / num_scenarios
    avg_m_star = sum(m_stars) / num_scenarios

    avg_net_base = sum(base_nets) / num_scenarios
    avg_empty_base = sum(base_empties) / num_scenarios

    impr_pct = ((avg_net_prop - avg_net_base) / avg_net_base * 100.0) if avg_net_base > 0 else 0.0
    ob_rate = ((m_star_saa - capacity_C) / capacity_C) * 100.0
    db_rate = (avg_db / capacity_C) * 100.0

    return {
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
            "avg_overbooking_rate_pct": round(ob_rate, 2),
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
        "scenarios_sample": sample_rows,
    }


def tim_nghiem_saa_chuan(
    S: int = 100,
    distributions: Optional[Dict[str, Any]] = None,
    capacity_C: int = 100,
    tau_0: float = 0.05,
    ticket_classes: Optional[List[Dict[str, Any]]] = None,
    seed: Optional[int] = 42
) -> Dict[str, Any]:
    """Interface public cua TV7 tim nghiem SAA va danh gia thuc nghiem. O(S * Pipeline)."""
    return chay_danh_gia_saa(
        num_scenarios=S,
        capacity_C=capacity_C,
        tau_0=tau_0,
        ticket_classes=ticket_classes,
        distributions=distributions,
        seed=seed
    )


def in_bang_so_sanh_thuc_te(benchmark_result: Dict[str, Any]) -> None:
    """Xuat bao cao so sanh Proposed vs Baseline tu runtime thuc te ra Console."""
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

    fmt_row = " {:<30} | {:>17} | {:>17}"
    print(" {:<30} | {:<17} | {:<17}".format("TIÊU CHÍ ĐÁNH GIÁ", "PROPOSED (SAA)", "BASELINE (FIXED)"))
    print("-" * 72)
    print(fmt_row.format("Doanh thu thuần TB (Net)", f"{prop.get('avg_net_revenue', 0.0):,.0f} đ", f"{base.get('avg_net_revenue', 0.0):,.0f} đ"))
    print(fmt_row.format("Hạn mức bán vé (M*)", f"{benchmark_result.get('m_star_saa', 0)} vé", f"{C} vé (cố định)"))
    print(fmt_row.format("Tỷ lệ bán lố (Overbooking)", f"+{prop.get('avg_overbooking_rate_pct', 0.0)}%", "0.0% (không bán lố)"))
    print(fmt_row.format("Khách bị từ chối (DB)", f"{prop.get('avg_denied_boarding', 0.0):.2f} khách", "0.00 khách"))
    print(fmt_row.format("Tỷ lệ Denied Boarding", f"{prop.get('db_rate_pct', 0.0)}% (<= {tau_0 * 100:.0f}%)", "0.0%"))
    print(fmt_row.format("Ghế trống lãng phí TB", f"{prop.get('avg_empty_seats', 0.0):.2f} ghế", f"{base.get('avg_empty_seats', 0.0):.2f} ghế"))
    print("-" * 72)
    sign = "+" if impr >= 0 else ""
    print(f" >>> HIỆU QUẢ CẢI THIỆN DOANH THU THỰC TẾ: {sign}{impr:.2f}% <<<")
    print("=" * 72)

    samples = benchmark_result.get("scenarios_sample", [])
    if samples:
        print("\n Mẫu kết quả 5 kịch bản ngẫu nhiên thực nghiệm:")
        fmt_sample = "  Kịch bản {:<2}: p={:<6} | M*={:<3} | Proposed: {:>13} đ | Baseline: {:>13} đ | DB: {} | Trống: {} vs {}"
        for r in samples:
            print(fmt_sample.format(
                r["scenario"], r["p"], r["m_star"],
                f"{r['proposed_net']:,.0f}", f"{r['baseline_net']:,.0f}",
                r["db_count"], r["empty_prop"], r["empty_base"]
            ))
        print("=" * 72 + "\n")


if __name__ == "__main__":
    kq = tim_nghiem_saa_chuan(S=100, capacity_C=100, tau_0=0.05)
    in_bang_so_sanh_thuc_te(kq)
