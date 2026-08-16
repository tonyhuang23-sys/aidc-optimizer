#!/usr/bin/env python3
"""
L4 re-modeling per the research instruction "L4 GPU rental re-calibration and
CoreWeave-style business model" (v4.0 of the working paper).

Splits the ComputeCo layer into three business models:
  L4-M  Merchant GPU rental          (spot/instance; market risk on owner)
  L4-C  Contracted Dedicated Cluster (5-yr fixed-price take-or-pay floor)
  L4-S  Strategic Neocloud           (take-or-pay + NVIDIA capacity backstop
                                      + customer capital + GPU-backed financing
                                      at ~5.9%, B200-consistent capex)

Two model upgrades vs. the base engine:
  1) GPU-aware financing (apply_l4_financing): the base engine only draws debt
     on construction-period capex, so GPU purchases at COD / refresh (operating
     period) are never debt-financed nor charged to equity -- v3.x L4 peak
     equity was systematically understated. Here debt is sized on TOTAL capex
     at the stated leverage and every GPU purchase is debt-drawn with the
     equity share charged to the sponsor.
  2) Take-or-pay revenue floor and NVIDIA-style capacity backstop in the
     asset layer.

Run:  python research_l4.py
"""
from __future__ import annotations
import json
from dataclasses import dataclass

import numpy as np

from aidc_optimizer.cli import load_config
from aidc_optimizer.models import _spread, _ramp_utilization, AssetCase, run_asset
from aidc_optimizer.financing import DebtInputs
from aidc_optimizer.core import TaxEngine, annuity_factor, irr_monthly

GPU_PER_IT_KW = 0.533          # B200 approx (research instruction section 3)
RATES_USD_GPUH = {              # 2026-08 public quotes (Lambda / CoreWeave)
    "S1_spot": 4.25, "S2_instance": 6.90, "S3_public_median": 7.80,
    "S4_dedicated_cluster": 9.36, "S5_high_cluster": 9.86,
}


@dataclass
class L4Params:
    mode: str
    rate_gpu_hr: float
    decay: float
    phys_util: float
    billable_util: float
    leverage: float
    kd: float
    tenor_months: int
    customer_capital_musd: float
    backstop_rate_pct_market: float
    capex_per_kw_it: float
    label: str
    contract_months: int = 0   # 0 = merchant-style 2 refresh cycles; >0 = single take-or-pay contract


L4_CASES = [
    L4Params("L4-M Merchant", 7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0.0, 0.0,
             60000 * GPU_PER_IT_KW, "Merchant GPU rental"),
    L4Params("L4-C Contracted", 9.36, 0.00, 0.90, 0.95, 0.55, 0.070, 60, 150.0, 0.0,
             60000 * GPU_PER_IT_KW, "Contracted dedicated cluster", contract_months=60),
    L4Params("L4-S Strategic", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500.0, 0.75,
             60000 * GPU_PER_IT_KW, "Strategic neocloud (CoreWeave-like)", contract_months=60),
]


def build_compute_ext(cfg: dict, p: L4Params) -> AssetCase:
    """L4 AssetCase with take-or-pay floor and (optionally) NVIDIA capacity backstop."""
    ref = cfg["reference"]; gen_mw = ref["gen_mw"]; pue = ref["pue"]; it_mw = gen_mw / pue
    dc = cfg["dc"]; g = cfg["gpu"]; pw = cfg["power"]
    cm = dc["construction_months"]; cycle = g["refresh_months"]
    cycles = 1 if p.contract_months > 0 else 2
    life = p.contract_months if p.contract_months > 0 else cycles * cycle
    n = cm + life + 1

    infra_ready_kw = dc["ready_capex_per_kw"] + dc["hosting_capex_increment_per_kw"]
    power_capex = gen_mw * 1000 * pw["capex_per_kw"] * pw.get("dc_credit_pct", 1.0)
    infra_capex = it_mw * 1000 * infra_ready_kw
    capex = np.zeros(n)
    if pw.get("dev_capex_musd", 0) > 0 and cm >= 12:
        capex[:cm - 12] += _spread(pw["dev_capex_musd"] * 1e6, 0, cm - 12, n, curve="u")[:cm - 12]
    capex += _spread(power_capex + infra_capex, max(0, cm - 12), min(12, cm), n)
    gpu_unit = it_mw * 1000 * p.capex_per_kw_it
    refresh_factor = g.get("refresh_capex_factor", 0.85)
    residual_sales = []          # (month, amount): old GPU sold at refresh
    for c in range(cycles):
        capex[cm + c * cycle] += gpu_unit * (refresh_factor ** c)
        if c > 0:
            residual_sales.append((cm + c * cycle,
                                   gpu_unit * (refresh_factor ** (c - 1)) * g["residual_pct_at_refresh"]))
    residual = (power_capex + infra_capex) * dc.get("residual_pct", 0.25) + \
               gpu_unit * (refresh_factor ** (cycles - 1)) * g["residual_pct_at_refresh"]

    rate0 = p.rate_gpu_hr * GPU_PER_IT_KW          # $/IT-kW-hr
    power_price = dc.get("power_cost_per_mwh", 0)
    extra = g.get("extra_opex_kw_yr", 0) / 12
    dc_opex = dc["opex_kw_yr"] / 12
    ramp = g.get("ramp_months", 24)
    take_or_pay = p.billable_util > p.phys_util or p.billable_util >= 0.9

    revenue = np.zeros(n); opex = np.zeros(n)
    for m in range(cm, cm + life):
        c, k = divmod(m - cm, cycle) if cycles > 1 else (0, m - cm)
        # p.decay is ANNUAL; k is months → use k/12 (P0-0 frequency fix)
        rate = rate0 * (g.get("refresh_rate_factor", 0.8) ** c) * ((1 + p.decay) ** (k / 12.0))
        u = _ramp_utilization(m, cm, p.phys_util, ramp) if c == 0 else p.phys_util
        # take-or-pay: customer bills the contracted floor from COD (no ramp on billing)
        billable = p.billable_util if take_or_pay else u
        revenue[m] = it_mw * 1000 * 730 * billable * rate
        if p.backstop_rate_pct_market > 0:
            # Residual unsold only. Do not pay backstop on take-or-pay unused (1-u).
            unsold = max(0.0, 1.0 - billable)
            revenue[m] += it_mw * 1000 * 730 * unsold * rate * p.backstop_rate_pct_market
        mwh = it_mw * pue * 730 * u
        opex[m] = mwh * power_price + it_mw * 1000 * (extra + dc_opex)
    for m, amt in residual_sales:
        revenue[m] += amt

    return AssetCase(name=p.label, layer="L4_Compute", gen_mw=gen_mw, it_mw=it_mw,
                     capex=capex, revenue=revenue, opex=opex, residual=residual,
                     notes={"mode": p.mode, "rate_gpu_hr": p.rate_gpu_hr, "decay": p.decay})


def apply_l4_financing(case, debt_in, tax, customer_capital, gpu_purchase_months):
    """GPU-capital-aware financing (fixes the base engine's operating-period capex gap)."""
    n = case.months
    capex = case.capex
    cod = int(np.argmax(case.revenue > 0)) if (case.revenue > 0).any() else 0
    if cod == 0:
        cod = n
    r_m = (1 + debt_in.rate) ** (1 / 12) - 1
    commit = debt_in.leverage * capex.sum()
    upfront = debt_in.upfront_fee * commit

    debt_balance = 0.0; idc = 0.0; drawn = 0.0
    fee_cash = np.zeros(n)
    for m in range(min(cod, n)):
        d = debt_in.leverage * capex[m]
        drawn += d
        interest_m = debt_balance * r_m
        idc += interest_m
        debt_balance += d + interest_m
        fee_cash[m] = (commit - drawn) * debt_in.commitment_fee / 12

    equity_capex = np.zeros(n)
    for m in gpu_purchase_months:
        if cod <= m < n:
            d = debt_in.leverage * capex[m]
            debt_balance += d
            equity_capex[m] = (1 - debt_in.leverage) * capex[m]
    term_debt = debt_balance

    uses = capex.sum() + fee_cash.sum() + upfront
    sources = term_debt + customer_capital
    sponsor_equity_total = uses - sources
    equity_gross = np.zeros(n)
    for m in range(min(cod, n)):
        equity_gross[m] = (1 - debt_in.leverage) * capex[m] + fee_cash[m]
    equity_gross[0] += upfront
    equity_gross += equity_capex
    if customer_capital > 0:
        equity_gross[min(cod, n - 1)] -= customer_capital

    op_months = max(0, n - cod)
    tenor = min(debt_in.tenor_months, op_months)
    principal_sched = np.zeros(n)
    if tenor > 0 and term_debt > 0:
        if debt_in.amort == "mortgage":
            ds = term_debt / annuity_factor(r_m, tenor)
            bal = term_debt
            pay = np.zeros(tenor)
            for k in range(tenor):
                pp = ds - bal * r_m
                pay[k] = pp; bal -= pp
        else:
            pay = np.full(tenor, term_debt / tenor)
        principal_sched[cod:cod + tenor] = pay

    ebitda = case.revenue - case.opex
    dep = tax.build_depreciation(capex)
    principal_arr = principal_sched.copy()
    balance = term_debt; dscr_list = []; levered_cf = np.zeros(n)
    for m in range(n):
        interest = balance * r_m
        principal = principal_arr[m]
        if m >= cod and (case.revenue[m] > 0 or m == n - 1):
            at = tax.after_tax_ebitda(ebitda[m:m + 1], dep[m:m + 1], np.array([interest]))[0]
            ds = interest + principal
            if ds > 0:
                dscr_list.append(at / ds)
            levered_cf[m] = at - interest - principal
            balance -= principal
    equity_cf = -equity_gross.copy()
    equity_cf[cod:] += levered_cf[cod:]
    equity_cf[-1] += case.residual - max(0.0, balance)

    peak_equity = float(-np.min(np.cumsum(equity_cf))) if len(equity_cf) else 0.0
    invested = float(-np.minimum(equity_cf, 0).sum())
    returned = float(np.maximum(equity_cf, 0).sum())
    dscr_arr = np.array(dscr_list) if dscr_list else None
    return type("FR", (), {
        "debt_amount": term_debt, "idc": idc, "fees": float(fee_cash.sum() + upfront),
        "sponsor_equity": sponsor_equity_total, "peak_equity": peak_equity,
        "customer_capital": customer_capital, "equity_cf": equity_cf,
        "equity_irr": irr_monthly(equity_cf), "moic": (returned / invested) if invested > 0 else 0.0,
        "min_dscr": float(np.nanmin(dscr_arr)) if dscr_arr is not None and len(dscr_arr) else None,
        "avg_dscr": float(np.nanmean(dscr_arr)) if dscr_arr is not None and len(dscr_arr) else None,
        "min_dscr_contract": float(np.nanmin(dscr_arr[:60])) if dscr_arr is not None and len(dscr_arr) else None,
        "debt_outstanding_at_end": float(max(0.0, balance)),
    })()


def run_l4(cfg: dict, p: L4Params):
    case = build_compute_ext(cfg, p)
    tax = TaxEngine(rate=cfg["tax"]["rate"], dep_life_months=cfg["tax"]["dep_life_months"],
                    method=cfg["tax"]["method"])
    debt_in = DebtInputs(leverage=p.leverage, rate=p.kd, tenor_months=p.tenor_months,
                         amort="mortgage", min_dscr_covenant=1.10, commitment_fee=0.004,
                         upfront_fee=0.012, cash_sweep=0.75)
    dc_ = cfg["dc"]; g_ = cfg["gpu"]
    cm = dc_["construction_months"]; gpu_cycle = g_["refresh_months"]
    gpu_cycles = 1 if p.contract_months > 0 else 2
    gpu_months = [cm + c * gpu_cycle for c in range(gpu_cycles)]
    fr = apply_l4_financing(case, debt_in, tax,
                            customer_capital=p.customer_capital_musd * 1e6,
                            gpu_purchase_months=gpu_months)
    res = run_asset(case, cfg)
    return {
        "mode": p.mode, "rate_gpu_hr": p.rate_gpu_hr,
        "capex_musd": round(case.capex.sum() / 1e6, 1),
        "peak_equity_musd": round(fr.peak_equity / 1e6, 1),
        "sponsor_equity_musd": round(fr.sponsor_equity / 1e6, 1),
        "project_irr": round(res.project_irr, 4) if res.project_irr is not None else None,
        "equity_irr": round(fr.equity_irr, 4) if fr.equity_irr is not None else None,
        "npv_musd": round(res.project_npv / 1e6, 1),
        "min_dscr": round(fr.min_dscr, 3) if fr.min_dscr is not None else None,
        "min_dscr_contract": round(fr.min_dscr_contract, 3) if fr.min_dscr_contract is not None else None,
        "moic": round(fr.moic, 2),
        "idc_musd": round(fr.idc / 1e6, 1),
        "debt_musd": round(fr.debt_amount / 1e6, 1),
    }


def main():
    cfg = load_config("configs/alberta.yaml")
    rows = [run_l4(cfg, p) for p in L4_CASES]
    for r in rows:
        pirr = "--" if r["project_irr"] is None else "%.1f%%" % (r["project_irr"] * 100)
        eirr = "--" if r["equity_irr"] is None else "%.1f%%" % (r["equity_irr"] * 100)
        print("%-18s NPV=%9.1fM pIRR=%6s eIRR=%7s peak=%7.1fM DSCR_c=%s capex=%.0fM" % (
            r["mode"], r["npv_musd"], pirr, eirr, r["peak_equity_musd"], r["min_dscr_contract"], r["capex_musd"]))
    json.dump(rows, open("/tmp/l4_cases.json", "w"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
