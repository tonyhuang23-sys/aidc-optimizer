"""L4 ledger invariants: residual-only backstop, annual decay, B200 capex."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aidc_optimizer.cli import load_config
from research_l4 import GPU_PER_IT_KW, L4_CASES, L4Params, build_compute_ext

BASE = os.path.join(os.path.dirname(__file__), "..", "configs", "alberta.yaml")


def _cfg():
    return load_config(BASE)


def test_l4s_default_capex_is_b200_allin():
    s = next(p for p in L4_CASES if p.mode.startswith("L4-S"))
    assert abs(s.capex_per_kw_it - 60000 * GPU_PER_IT_KW) < 1e-6
    assert abs(s.capex_per_kw_it - 31980) < 1.0


def test_backstop_does_not_pay_take_or_pay_unused():
    cfg = _cfg()
    p = L4Params(
        "L4-S Strategic", 9.36, 0.0, 0.90, 0.95, 0.70, 0.059, 60, 500.0, 0.75,
        60000 * GPU_PER_IT_KW, "s", contract_months=60,
    )
    with_bs = build_compute_ext(cfg, p)
    p2 = L4Params(
        "L4-S Strategic", 9.36, 0.0, 0.90, 0.95, 0.70, 0.059, 60, 500.0, 0.0,
        60000 * GPU_PER_IT_KW, "s", contract_months=60,
    )
    no_bs = build_compute_ext(cfg, p2)
    # billable 0.95 < 1, so a 5% residual-unsold backstop remains; paid unused (1-u) must not.
    extra = float((with_bs.revenue - no_bs.revenue).sum())
    it_mw = with_bs.it_mw
    rate0 = p.rate_gpu_hr * GPU_PER_IT_KW
    expected = it_mw * 1000 * 730 * 0.05 * rate0 * 0.75 * 60
    assert extra > 0
    assert abs(extra - expected) / expected < 0.02
    # Old bug billed (1-u)=0.10 instead of unsold=0.05; reject that level.
    old_bug = it_mw * 1000 * 730 * 0.10 * rate0 * 0.75 * 60
    assert extra < 0.7 * old_bug


def test_decay_is_annual_not_monthly():
    cfg = _cfg()
    p = L4Params(
        "L4-M Merchant", 7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0.0, 0.0,
        60000 * GPU_PER_IT_KW, "m", contract_months=0,
    )
    case = build_compute_ext(cfg, p)
    cm = cfg["dc"]["construction_months"]
    cycle = cfg["gpu"]["refresh_months"]
    it_mw = case.it_mw
    rate0 = p.rate_gpu_hr * GPU_PER_IT_KW
    # Second vintage, month 12: no ramp, refresh_rate_factor applied once.
    k = 12
    m = cm + cycle + k
    expected = it_mw * 1000 * 730 * 0.75 * rate0 * 0.8 * ((1 - 0.22) ** (k / 12.0))
    got = float(case.revenue[m])
    assert abs(got - expected) / expected < 0.02
    monthly_wrong = it_mw * 1000 * 730 * 0.75 * rate0 * 0.8 * ((1 - 0.22) ** k)
    assert abs(got - monthly_wrong) / expected > 0.10


def test_recommend_layer_defaults_to_l3():
    from aidc_optimizer.core import LayerResult
    from aidc_optimizer.evaluate import recommend_layer
    l3 = LayerResult(name="L3", layer="L3_CriticalIT", gen_mw=100, it_mw=80, project_npv=3e8)
    l4 = LayerResult(name="L4", layer="L4_Compute", gen_mw=100, it_mw=80, project_npv=1e9)
    rec = recommend_layer([l3, l4], has_financeable_contract=False)
    assert rec["layer"] == "L3_CriticalIT"
    rec2 = recommend_layer([l3, l4], has_financeable_contract=True)
    assert rec2["layer"] == "L4_Compute"

def test_dsra_funded_when_enabled():
    from aidc_optimizer.models import AssetCase
    from aidc_optimizer.financing import DebtInputs, apply_financing
    from aidc_optimizer.core import TaxEngine
    n = 24
    capex = np.zeros(n); capex[0] = 1_000_000.0
    rev = np.zeros(n); rev[6:] = 80_000.0
    opex = np.zeros(n); opex[6:] = 5_000.0
    case = AssetCase("t", "L1_Power", 1.0, 1.0, capex, rev, opex, residual=0.0)
    tax = TaxEngine(rate=0.23, dep_life_months=240, method="straight_line")
    common = dict(leverage=0.50, rate=0.06, tenor_months=12, amort="straight_line",
                  cash_sweep=0.0, commitment_fee=0.0, upfront_fee=0.0)
    r0 = apply_financing(case, DebtInputs(dsra_months=0, **common), tax)
    r1 = apply_financing(case, DebtInputs(dsra_months=6, **common), tax)
    assert r1.peak_equity > r0.peak_equity
    assert r1.equity_cf[-1] > r0.equity_cf[-1]

