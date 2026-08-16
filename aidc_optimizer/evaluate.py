"""
五维评价矩阵 + 增量收益分析
"""
from __future__ import annotations
from typing import Dict, List
import numpy as np
from .core import LayerResult
from .risk import MCResult

RISK_MATRIX = {
    "土地":              {"L0_Dev": 2, "L1_Power": 2, "L2_Shell": 1, "L3_CriticalIT": 1, "L35_Hosting": 1, "L4_Compute": 0, "L5_AI": 0},
    "Permitting":        {"L0_Dev": 2, "L1_Power": 2, "L2_Shell": 1, "L3_CriticalIT": 1, "L35_Hosting": 1, "L4_Compute": 0, "L5_AI": 0},
    "天然气价格":         {"L0_Dev": 2, "L1_Power": 1, "L2_Shell": 1, "L3_CriticalIT": 1, "L35_Hosting": 1, "L4_Compute": 1, "L5_AI": 1},
    "电力价格":           {"L0_Dev": 2, "L1_Power": 1, "L2_Shell": 1, "L3_CriticalIT": 1, "L35_Hosting": 1, "L4_Compute": 2, "L5_AI": 2},
    "Construction":      {"L0_Dev": 1, "L1_Power": 2, "L2_Shell": 2, "L3_CriticalIT": 2, "L35_Hosting": 2, "L4_Compute": 1, "L5_AI": 1},
    "COD延误":           {"L0_Dev": 2, "L1_Power": 2, "L2_Shell": 3, "L3_CriticalIT": 3, "L35_Hosting": 3, "L4_Compute": 2, "L5_AI": 2},
    "Tenant/Customer":   {"L0_Dev": 1, "L1_Power": 2, "L2_Shell": 2, "L3_CriticalIT": 2, "L35_Hosting": 2, "L4_Compute": 2, "L5_AI": 2},
    "Utilization":       {"L0_Dev": 0, "L1_Power": 0, "L2_Shell": 0, "L3_CriticalIT": 0, "L35_Hosting": 0, "L4_Compute": 3, "L5_AI": 3},
    "GPU价格":           {"L0_Dev": 0, "L1_Power": 0, "L2_Shell": 0, "L3_CriticalIT": 0, "L35_Hosting": 0, "L4_Compute": 3, "L5_AI": 3},
    "Technology":        {"L0_Dev": 0, "L1_Power": 0, "L2_Shell": 0, "L3_CriticalIT": 1, "L35_Hosting": 1, "L4_Compute": 3, "L5_AI": 3},
    "Residual Value":    {"L0_Dev": 0, "L1_Power": 1, "L2_Shell": 1, "L3_CriticalIT": 1, "L35_Hosting": 1, "L4_Compute": 2, "L5_AI": 2},
    "AI需求":            {"L0_Dev": 0, "L1_Power": 0, "L2_Shell": 1, "L3_CriticalIT": 1, "L35_Hosting": 2, "L4_Compute": 2, "L5_AI": 3},
    "信用/Counterparty":  {"L0_Dev": 1, "L1_Power": 2, "L2_Shell": 2, "L3_CriticalIT": 2, "L35_Hosting": 2, "L4_Compute": 2, "L5_AI": 2},
    "Refinancing":       {"L0_Dev": 1, "L1_Power": 1, "L2_Shell": 2, "L3_CriticalIT": 2, "L35_Hosting": 2, "L4_Compute": 2, "L5_AI": 2},
}

RISK_OWNER = {
    "天然气价格": "Tenant (pass-through) / PowerCo (merchant)",
    "电力价格": "Tenant (tolling) / ComputeCo (spot)",
    "Construction overrun": "EPC (fixed-price) / Developer",
    "GPU utilization": "ComputeCo / AI ServiceCo",
    "Power availability": "PowerCo",
    "Technology obsolescence": "GPU Owner（Hosting模式=客户）",
    "COD延误": "Developer / EPC (LD)",
    "信用风险": "Lender (via DSRA/guarantee) / Sponsor",
}

ASSET_LIFE_MONTHS = {
    "L0_Dev": 30, "L1_Power": 360, "L2_Shell": 240, "L3_CriticalIT": 240,
    "L35_Hosting": 240, "L4_Compute": 48, "L5_AI": 36,
}

ORDER = ["L0_Dev", "L1_Power", "L2_Shell", "L3_CriticalIT", "L35_Hosting", "L4_Compute", "L5_AI"]


def risk_exposure_score(layer: str) -> float:
    vals = [m[layer] for m in RISK_MATRIX.values() if layer in m]
    return float(np.mean(vals)) if vals else 0.0


def five_dimension_table(results: List[LayerResult], mc: Dict[str, MCResult],
                         finance_cfg: Dict) -> List[Dict]:
    rows = []
    for r in results:
        m = mc.get(r.layer)
        fcfg = finance_cfg.get(r.layer, {})
        mw = r.it_mw if r.it_mw > 0 else r.gen_mw
        tenor = fcfg.get("tenor_months", 0)
        asset_life = ASSET_LIFE_MONTHS.get(r.layer, 0)
        covenant = fcfg.get("min_dscr_covenant", 1.2)
        rows.append({
            "Model": r.name,
            "D1 投资强度": {
                "CAPEX $/kW": r.capex_total / (mw * 1000),
                "Sponsor Equity $/kW": r.sponsor_equity / (mw * 1000),
                "Peak Equity $/kW": r.peak_equity / (mw * 1000),
                "资本久期(月)": asset_life,
            },
            "D2 回报": {
                "Rev $/MW-yr": r.revenue_y1 / mw / 1e6,
                "EBITDA $/MW-yr": r.ebitda_y1 / mw / 1e6,
                "NPV $/MW": r.project_npv / mw / 1e6,
                "Project IRR": r.project_irr,
                "Equity IRR": r.equity_irr,
                "NPV/Peak Equity": r.project_npv / r.peak_equity if r.peak_equity > 0 else np.nan,
            },
            "D3 风险": {
                "P(NPV<0)": m.prob_npv_negative if m else np.nan,
                "NPV P10 $M": m.npv_p10 / 1e6 if m else np.nan,
                "P(IRR<hurdle)": m.prob_irr_below_hurdle if m else np.nan,
                "敞口分(0-3)": risk_exposure_score(r.layer),
            },
            "D4 敞口": {
                score: RISK_MATRIX[score][r.layer]
                for score in ["COD延误", "Utilization", "GPU价格", "AI需求", "信用/Counterparty"]
                if r.layer in RISK_MATRIX[score]
            },
            "D5 融资": {
                "杠杆率": r.debt_amount / r.capex_total if r.capex_total > 0 and r.debt_amount else 0,
                "Min DSCR": r.min_dscr,
                "Covenant headroom": (r.min_dscr - covenant) if r.min_dscr is not None and r.min_dscr == r.min_dscr else np.nan,
                "期限匹配": "PASS" if tenor <= asset_life else "WARN 债务期限>资产经济寿命",
                "LLCR": r.llcr,
            },
        })
    return rows


def incremental_analysis(results: List[LayerResult]) -> List[Dict]:
    by_layer = {r.layer: r for r in results}
    seq = [l for l in ORDER if l in by_layer]
    rows = []
    for prev, cur in zip(seq, seq[1:]):
        a, b = by_layer[prev], by_layer[cur]
        d_capex = b.capex_total - a.capex_total
        d_npv = b.project_npv - a.project_npv
        rows.append({
            "From": a.name, "To": b.name,
            "ΔCAPEX $M": d_capex / 1e6,
            "ΔNPV $M": d_npv / 1e6,
            "ΔReturn (ΔNPV/ΔCAPEX)": (d_npv / d_capex) if d_capex > 1e6 else np.nan,
            "ΔEquity IRR": (b.equity_irr - a.equity_irr) if (a.equity_irr is not None and b.equity_irr is not None) else np.nan,
            "边际决策": (
                "筛选通过：增量NPV为正" if (d_npv > 0 and d_capex > 1e6)
                else ("无需增量资本" if d_capex <= 1e6 else "筛选未过：增值不足")
            ),
        })
    return rows


def three_irr_view(results: List[LayerResult]) -> Dict[str, float]:
    by = {r.layer: r for r in results}
    return {
        "Development IRR (Land→Exit)": by["L0_Dev"].project_irr if "L0_Dev" in by else None,
        "Infrastructure IRR (Power+DC)": by["L3_CriticalIT"].equity_irr if "L3_CriticalIT" in by else None,
        "Compute IRR (GPU)": by["L4_Compute"].equity_irr if "L4_Compute" in by else None,
    }


def recommend_layer(results: List[LayerResult], has_financeable_contract: bool = False) -> Dict[str, object]:
    """Screening rule: no financeable compute contract -> stay at L3.

    Merchant is never the fallback. Incremental NPV>0 is only a screen, not
    an underwriting recommendation to extend the stack.
    """
    by = {r.layer: r for r in results}
    l3 = by.get("L3_CriticalIT")
    l4 = by.get("L4_Compute")
    if not has_financeable_contract:
        return {
            "layer": "L3_CriticalIT",
            "reason": "无融资级算力合同，默认停在 L3；不把 Merchant 当回退。",
            "npv_musd": None if l3 is None else l3.project_npv / 1e6,
        }
    if l4 is not None and l3 is not None and l4.project_npv > l3.project_npv:
        return {
            "layer": "L4_Compute",
            "reason": "已有融资级合同，且 L4 相对 L3 的增量NPV为正（仍为筛选口径）。",
            "npv_musd": l4.project_npv / 1e6,
        }
    return {
        "layer": "L3_CriticalIT",
        "reason": "虽有合同线索，但筛选增量NPV未超过 L3。",
        "npv_musd": None if l3 is None else l3.project_npv / 1e6,
    }
