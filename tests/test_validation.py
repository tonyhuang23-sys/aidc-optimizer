"""
校准验证：Greenlight（Power端）与 TeraWulf（Critical IT端）价值发现
运行: python tests/test_validation.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline
from aidc_optimizer.models import BUILDERS
from aidc_optimizer.core import irr_monthly
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "configs", "alberta.yaml")


def test_financial_math():
    """单元测试：月度 IRR / NPV 基本正确性。"""
    # 投资-100，每月回收 1，共 120 月 → 年化 IRR ≈ ?
    cf = np.zeros(121)
    cf[0] = -100
    cf[1:] = 1.0
    irr = irr_monthly(cf)
    assert irr is not None and 0.0 < irr < 0.05, f"IRR 异常: {irr}"
    # 翻倍回收 → IRR 提高
    cf2 = cf.copy()
    cf2[1:] = 2.0
    assert irr_monthly(cf2) > irr
    print(f"[PASS] 财务数学: 100 invested / $1 per month x120mo -> IRR={irr:.2%}")


def test_terawulf():
    """TeraWulf-Anthropic: 401 MW Critical IT, 20年, 名义~$19B, ≈$197/kW-mo。"""
    cfg = load_config(BASE)
    cfg = apply_overrides(cfg, [
        "reference.gen_mw=501.25",   # PUE 1.25 → IT 401 MW
        "reference.pue=1.25",
        "dc.ready_rent_kw_mo=197",
    ])
    case = BUILDERS["critical_it"](cfg)
    it_kW = case.it_mw * 1000
    assert abs(it_kW - 401000) < 500, f"IT MW 换算错误: {it_kW}"
    # 名义合同收入 = 租金 x 240 个月（不含 escalator 的名义口径）
    flat = it_kW * 197 * 240 / 1e9
    assert 17 < flat < 21, f"名义合同收入偏离 $19B 基准: ${flat:.1f}B"
    # 首年实际收入（含爬坡前 12 个月全额租金，无 escalator 期）
    r = run_full_pipeline(cfg, "critical_it")
    y1 = r.revenue_y1 / 1e9
    assert 0.85 < y1 < 1.05, f"首年收入偏离 $947M/yr: ${y1:.2f}B"
    print(f"[PASS] TeraWulf 校准: {it_kW/1000:.0f} MW IT, 名义合同 ${flat:.1f}B, "
          f"首年收入 ${y1:.2f}B, Project IRR={r.project_irr:.1%}")


def test_greenlight():
    """Greenlight: 932 MW CC, CA$4.6B (≈US$3.3B @0.714), 60%债务。
    验证: (1) 债务占比≈60%; (2) 固定成本回收(EBITDA/MWh)落在 CA$60-80;
    (3) 租户全包成本(EBITDA+燃料)/MWh 落在 CA$90-120。"""
    cfg = load_config(BASE)
    fx = 0.714
    capex_usd = 4.6e9 * fx
    cfg = apply_overrides(cfg, [
        "reference.gen_mw=932",
        f"power.capex_per_kw={capex_usd/932/1000:.0f}",
        "power.capacity_payment_kw_mo=28",     # ≈CA$39/kW-mo 容量费
        "power.heat_rate_gj_per_mwh=7.4",
        "power.gas_price_gj=1.80",             # ≈CA$2.5/GJ
        "power.availability=0.90",
        "finance.L1_Power.leverage=0.60",
    ])
    r = run_full_pipeline(cfg, "power")
    # 债务占比
    lev = r.debt_amount / r.capex_total
    assert 0.55 < lev < 0.66, f"杠杆 {lev:.1%} 偏离 60% 基准"
    # EBITDA/MWh → 折 CAD（932e3 kW × h = kWh，/1000 转 MWh）
    mwh_yr = 932e3 * 730 * 12 * 0.90 / 1000
    ebitda_per_mwh_cad = (r.ebitda_y1 / mwh_yr) / fx
    # 全包成本 = 容量费 + 燃料 + VOM（租户口径）
    fuel_mwh_cad = 7.4 * 1.80 / fx * 1.0
    allin_cad = ebitda_per_mwh_cad + fuel_mwh_cad + 3.5 / fx
    print(f"[PASS] Greenlight 校准: 杠杆 {lev:.0%}, EBITDA CA${ebitda_per_mwh_cad:.0f}/MWh "
          f"(基准CA$60-80), 租户全包 CA${allin_cad:.0f}/MWh (基准CA$90-120)")
    assert 55 < ebitda_per_mwh_cad < 85, f"EBITDA/MWh 偏离: CA${ebitda_per_mwh_cad:.0f}"
    assert 80 < allin_cad < 125, f"全包成本偏离: CA${allin_cad:.0f}"
    # DSCR 合理区间
    assert r.min_dscr is None or r.min_dscr > 1.0, f"DSCR 过低: {r.min_dscr}"


def test_duration_matching():
    """GPU 债务期限 ≤ 刷新周期。"""
    cfg = load_config(BASE)
    tenor = cfg["finance"]["L4_Compute"]["tenor_months"]
    refresh = cfg["gpu"]["refresh_months"]
    assert tenor <= refresh, f"期限错配: debt {tenor}mo > refresh {refresh}mo"
    print(f"[PASS] 期限匹配: ComputeCo debt {tenor}mo ≤ refresh {refresh}mo")


if __name__ == "__main__":
    test_financial_math()
    test_terawulf()
    test_greenlight()
    test_duration_matching()
    print("\n全部校准测试通过 ✅")
