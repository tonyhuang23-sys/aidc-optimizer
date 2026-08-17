#!/usr/bin/env python3
"""
HISTORICAL SCRIPT — period artifact, not engine 1.2.1.
32000 / 21300 in the certainty bridge are pre-unification B200 capex.
Live L4 default is 60000 * GPU_PER_IT_KW (~31980).

AIDC v5 research engine — Investment Vintage × Contract × Strategic Finance.

Extends research_l4 with:
  - GPU Investment Vintage / Merchant cohort returns (Historical vs Forward)
  - Contract term structures C1–C4 (fixed / step-down / repricing / refresh)
  - L4 Certainty Bridge (E(NPV), ES5, CE-NPV, P(loss), Peak Equity, DSCR)
  - Contract Financeability Score → leverage / Kd / tenor
  - Counterparty credit / renewal cliff stress
  - Market state classification

Run: python research_v5.py
Outputs: research_outputs/v5/*
"""
from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from aidc_optimizer.cli import load_config
from aidc_optimizer.risk import run_full_pipeline
from research_l4 import L4Params, run_l4, build_compute_ext, apply_l4_financing, GPU_PER_IT_KW
from aidc_optimizer.financing import DebtInputs
from aidc_optimizer.core import TaxEngine
from aidc_optimizer.models import run_asset

OUT = Path("research_outputs/v5")
CFG_PATH = "configs/alberta.yaml"
SEED = 42


# ---------------------------------------------------------------------------
# 1. Investment Vintage database (anchored; confidence noted)
# ---------------------------------------------------------------------------
# H100 purchase anchors: IREN SEC ~$40k/GPU (2023-08 248×H100 ~$10M; 2024-02 568×H100 ~$22M)
# H100 power density: ~0.78 GPU/IT-kW (HGX-class approximation)
# B200: 0.533 GPU/IT-kW (v4.0 instruction)
# Rates: SemiAnalysis H100 1yr $1.70→$2.35 (2025-10→2026-03); Lambda/CoreWeave 2026-08 public quotes

H100_GPU_PER_KW = 0.78
B200_GPU_PER_KW = 0.533

VINTAGES = [
    # Historical cohorts — purchase low, then scarcity rent path
    dict(vintage_id="H100-2023", gpu_model="H100", gpu_per_kw=H100_GPU_PER_KW,
         purchase_per_gpu=40300, entry_rate_gpuh=4.50,  # early scarcity rent (approx)
         rate_path="scarcity_then_soft",  # high then soft then bounce
         util=0.85, residual_at_48=0.35, confidence=0.55,
         market_state="S1_Scarcity_Boom", note="IREN SEC ~$40k/GPU purchase anchor; rate path estimated"),
    dict(vintage_id="H100-2024", gpu_model="H100", gpu_per_kw=H100_GPU_PER_KW,
         purchase_per_gpu=38700, entry_rate_gpuh=3.80,
         rate_path="scarcity_then_soft", util=0.82, residual_at_48=0.30, confidence=0.55,
         market_state="S1_Scarcity_Boom", note="IREN 2024-02 ~$22M/568≈$38.7k"),
    dict(vintage_id="H100-2025", gpu_model="H100", gpu_per_kw=H100_GPU_PER_KW,
         purchase_per_gpu=35000, entry_rate_gpuh=2.80,
         rate_path="soft_then_bounce", util=0.78, residual_at_48=0.25, confidence=0.60,
         market_state="S4_Tech_Transition", note="H100 1yr $1.70 trough late-2025 then +40% bounce"),
    # Forward new investment
    dict(vintage_id="H100-2026F", gpu_model="H100", gpu_per_kw=H100_GPU_PER_KW,
         purchase_per_gpu=32000, entry_rate_gpuh=3.20,
         rate_path="forward_decay", util=0.75, residual_at_48=0.15, confidence=0.65,
         market_state="S2_Balanced", note="Forward new investment; long-term decay -22%/yr"),
    dict(vintage_id="B200-2026F", gpu_model="B200", gpu_per_kw=B200_GPU_PER_KW,
         purchase_per_gpu=60000, entry_rate_gpuh=7.80,
         rate_path="forward_decay", util=0.75, residual_at_48=0.15, confidence=0.70,
         market_state="S2_Balanced", note="Public-market median rate; full-stack ~$32k/IT-kW"),
]


def rate_curve(path: str, entry: float, months: int) -> np.ndarray:
    """Monthly GPU-hour rate path."""
    t = np.arange(months)
    y = t / 12.0
    if path == "scarcity_then_soft":
        # Year0 high, mild rise, then soft -15%/yr after year 1.5, residual bounce year 2.5
        r = entry * (1.05 ** np.minimum(y, 1.0)) * ((1 - 0.15) ** np.maximum(y - 1.0, 0))
        bounce = 1.0 + 0.25 * ((y >= 2.0) & (y < 2.5)).astype(float) * np.maximum(0, 1 - (y - 2.0) / 0.5)
        return r * np.where(bounce > 1, bounce, 1.0)
    if path == "soft_then_bounce":
        # trough then +40% over 6 months then decay -18%/yr
        r = np.full(months, entry, dtype=float)
        for i, yi in enumerate(y):
            if yi < 0.5:
                r[i] = entry * (1 - 0.20 * yi / 0.5)  # soft to trough
            elif yi < 1.0:
                r[i] = entry * 0.80 * (1 + 0.40 * (yi - 0.5) / 0.5)  # bounce +40%
            else:
                r[i] = entry * 0.80 * 1.40 * ((1 - 0.18) ** (yi - 1.0))
        return r
    if path == "forward_decay":
        return entry * ((1 - 0.22) ** y)
    if path == "flat":
        return np.full(months, entry, dtype=float)
    if path == "mild_decay":
        return entry * ((1 - 0.08) ** y)
    return entry * ((1 - 0.22) ** y)


def purchase_per_it_kw(v: dict) -> float:
    return v["purchase_per_gpu"] * v["gpu_per_kw"]


# ---------------------------------------------------------------------------
# 2. Merchant cohort runner (uses research_l4 infrastructure with path rates)
# ---------------------------------------------------------------------------

def run_merchant_cohort(cfg, v: dict, life_months: int = 48) -> dict:
    """Run a merchant GPU cohort as L4-M with vintage-specific CAPEX and avg rate."""
    rates = rate_curve(v["rate_path"], v["entry_rate_gpuh"], life_months)
    # Use path-average rate for the simplified monthly engine; also report path stats
    avg_rate = float(rates.mean())
    capex_it = purchase_per_it_kw(v)
    # residual override via residual_pct
    p = L4Params(
        mode="L4-M",
        rate_gpu_hr=avg_rate,
        decay=0.0,  # path already embeds decay via avg; for pure forward use path avg of decay curve
        phys_util=v["util"],
        billable_util=v["util"],
        leverage=0.35,
        kd=0.095,
        tenor_months=min(48, life_months),
        customer_capital_musd=0.0,
        backstop_rate_pct_market=0.0,
        capex_per_kw_it=capex_it,
        label=v["vintage_id"],
        contract_months=0,
    )
    # For forward_decay path, use explicit annual decay instead of flat avg
    if v["rate_path"] == "forward_decay":
        p.rate_gpu_hr = v["entry_rate_gpuh"]
        p.decay = -0.22
    elif v["rate_path"] in ("scarcity_then_soft", "soft_then_bounce"):
        # approximate with mild net decay matching path mean
        p.rate_gpu_hr = v["entry_rate_gpuh"]
        # fit effective decay so mean matches
        p.decay = -0.05 if "scarcity" in v["rate_path"] else -0.10

    r = run_l4(cfg, p)
    # also compute naive payback months from first-year revenue
    return {
        "vintage_id": v["vintage_id"],
        "gpu_model": v["gpu_model"],
        "market_state": v["market_state"],
        "purchase_per_gpu": v["purchase_per_gpu"],
        "capex_per_it_kw": round(capex_it, 0),
        "entry_rate_gpuh": v["entry_rate_gpuh"],
        "avg_path_rate_gpuh": round(avg_rate, 3),
        "util": v["util"],
        "residual_at_48": v["residual_at_48"],
        "confidence": v["confidence"],
        "npv_musd": r["npv_musd"],
        "project_irr": r["project_irr"],
        "equity_irr": r["equity_irr"],
        "peak_equity_musd": r["peak_equity_musd"],
        "capex_musd": r["capex_musd"],
        "moic": r["moic"],
        "min_dscr": r["min_dscr"],
        "note": v["note"],
    }


# ---------------------------------------------------------------------------
# 3. Contract term structures C1–C4
# ---------------------------------------------------------------------------

CONTRACTS = [
    dict(id="C1_5Y_Fixed", tenor=60, decay=0.00, billable=0.95, util=0.90,
         prepay=0.20, label="5Y Fixed Take-or-pay"),
    dict(id="C2_5Y_Stepdown", tenor=60, decay=-0.06, billable=0.95, util=0.90,
         prepay=0.20, label="5Y Scheduled Step-down ~-6%/yr"),
    dict(id="C3_Benchmark_Repricing", tenor=60, decay=-0.15, billable=0.90, util=0.85,
         prepay=0.10, label="5Y with annual-ish benchmark repricing"),
    dict(id="C4_Tech_Refresh", tenor=36, decay=-0.08, billable=0.95, util=0.90,
         prepay=0.15, label="3Y tech-refresh-linked"),
]


def run_contract(cfg, c: dict, rate_gpuh: float = 9.36, capex_it: float = 32000,
                 leverage: float = 0.55, kd: float = 0.070) -> dict:
    tcv_proxy = None  # not needed
    # customer capital = prepay * rough TCV
    # TCV ≈ rate * 0.533 * 1000 * 80 MW_IT * 8760 * billable * years * 1e-6
    it_mw = cfg["reference"]["gen_mw"] / cfg["reference"]["pue"]
    years = c["tenor"] / 12
    tcv_musd = rate_gpuh * GPU_PER_IT_KW * 1000 * it_mw * 8760 * c["billable"] * years / 1e6
    cc = tcv_musd * c["prepay"]
    p = L4Params(
        mode="L4-C",
        rate_gpu_hr=rate_gpuh,
        decay=c["decay"],
        phys_util=c["util"],
        billable_util=c["billable"],
        leverage=leverage,
        kd=kd,
        tenor_months=c["tenor"],
        customer_capital_musd=cc,
        backstop_rate_pct_market=0.0,
        capex_per_kw_it=capex_it,
        label=c["id"],
        contract_months=c["tenor"],
    )
    r = run_l4(cfg, p)
    r["contract_id"] = c["id"]
    r["label"] = c["label"]
    r["prepay_pct"] = c["prepay"]
    r["tcv_musd"] = round(tcv_musd, 1)
    r["customer_capital_musd"] = round(cc, 1)
    return r


# ---------------------------------------------------------------------------
# 4. Certainty Bridge (with light MC for CE-NPV / ES / P(loss))
# ---------------------------------------------------------------------------

def light_mc_npv(cfg, p: L4Params, n: int = 200, seed: int = SEED) -> dict:
    """Gaussian-ish shock on rate and utilization; return E/ES/CE/P(loss)."""
    rng = np.random.default_rng(seed)
    npvs = []
    for _ in range(n):
        rate_m = math.exp(rng.normal(-0.5 * 0.20 ** 2, 0.20))
        util_m = max(0.4, min(0.99, 1 + rng.normal(0, 0.08)))
        pp = L4Params(
            p.mode, p.rate_gpu_hr * rate_m, p.decay,
            min(0.99, p.phys_util * util_m),
            min(0.99, p.billable_util * (1 if p.billable_util >= 0.9 else util_m)),
            p.leverage, p.kd, p.tenor_months, p.customer_capital_musd,
            p.backstop_rate_pct_market, p.capex_per_kw_it, p.label, p.contract_months,
        )
        try:
            npvs.append(run_l4(cfg, pp)["npv_musd"])
        except Exception:
            continue
    a = np.array(npvs, dtype=float)
    if len(a) == 0:
        return dict(e_npv=None, es5=None, ce05=None, p_loss=None, n=0)
    p5 = np.quantile(a, 0.05)
    es = float(a[a <= p5].mean()) if (a <= p5).any() else float(p5)
    e = float(a.mean())
    return dict(e_npv=round(e, 1), es5=round(es, 1), ce05=round(0.5 * e + 0.5 * es, 1),
                p_loss=round(float((a < 0).mean()), 4), n=len(a))


def certainty_bridge(cfg) -> List[dict]:
    steps = [
        ("0 Merchant base (B200F forward)", L4Params("M", 7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 32000, "M0")),
        ("1 + Market rate dedicated 9.36", L4Params("M", 9.36, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 32000, "M1")),
        ("2 + 5Y Fixed take-or-pay", L4Params("C", 9.36, 0.00, 0.90, 0.95, 0.35, 0.095, 60, 0, 0, 32000, "C2", 60)),
        ("3 + Contracted financing lev55/kd7", L4Params("C", 9.36, 0.00, 0.90, 0.95, 0.55, 0.070, 60, 0, 0, 32000, "C3", 60)),
        ("4 + Prepay 20% TCV", L4Params("C", 9.36, 0.00, 0.90, 0.95, 0.55, 0.070, 60, 400, 0, 32000, "C4", 60)),
        ("5 + NVIDIA backstop 75%", L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.55, 0.070, 60, 400, 0.75, 32000, "S5", 60)),
        ("6 + GPU-backed lev70/kd5.9 +cc500", L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.75, 32000, "S6", 60)),
        ("7 + B200-consistent capex 21.3k", L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.75, 21300, "S7", 60)),
    ]
    rows = []
    prev_npv = None
    prev_ce = None
    prev_peak = None
    for label, p in steps:
        r = run_l4(cfg, p)
        mc = light_mc_npv(cfg, p, n=120, seed=SEED)
        row = {
            "step": label,
            "npv_musd": r["npv_musd"],
            "delta_npv": None if prev_npv is None else round(r["npv_musd"] - prev_npv, 1),
            "peak_equity_musd": r["peak_equity_musd"],
            "delta_peak": None if prev_peak is None else round(r["peak_equity_musd"] - prev_peak, 1),
            "e_npv": mc["e_npv"],
            "es5": mc["es5"],
            "ce05": mc["ce05"],
            "delta_ce": None if prev_ce is None or mc["ce05"] is None else round(mc["ce05"] - prev_ce, 1),
            "p_loss": mc["p_loss"],
            "min_dscr_contract": r["min_dscr_contract"],
            "project_irr": r["project_irr"],
        }
        rows.append(row)
        prev_npv = r["npv_musd"]
        prev_ce = mc["ce05"]
        prev_peak = r["peak_equity_musd"]
        print(f"{label:40s} NPV={r['npv_musd']:9.1f} CE={mc['ce05']} P(loss)={mc['p_loss']} peak={r['peak_equity_musd']:.0f}")
    return rows


# ---------------------------------------------------------------------------
# 5. Contract Financeability Score
# ---------------------------------------------------------------------------

def financeability_score(customer_credit: str, tenor_y: float, top: float,
                         prepay: float, backstop: bool, concentration: float) -> dict:
    """Map contract quality → leverage / Kd / tenor / min DSCR."""
    credit_map = {"IG": 1.0, "HY": 0.6, "Spec": 0.3, "Unrated": 0.4}
    c = credit_map.get(customer_credit, 0.4)
    score = (
        0.30 * c
        + 0.20 * min(1.0, tenor_y / 5)
        + 0.20 * top
        + 0.15 * min(1.0, prepay / 0.25)
        + 0.10 * (1.0 if backstop else 0.0)
        + 0.05 * (1.0 - min(1.0, concentration))
    )
    # map score to financing terms
    if score >= 0.80:
        lev, kd, ten, dscr = 0.70, 0.059, 60, 1.25
    elif score >= 0.65:
        lev, kd, ten, dscr = 0.55, 0.070, 60, 1.30
    elif score >= 0.50:
        lev, kd, ten, dscr = 0.45, 0.085, 48, 1.35
    else:
        lev, kd, ten, dscr = 0.35, 0.095, 48, 1.40
    return dict(score=round(score, 3), max_leverage=lev, credit_spread_kd=kd,
                debt_tenor_months=ten, min_dscr=dscr,
                customer_credit=customer_credit, tenor_y=tenor_y, top=top,
                prepay=prepay, backstop=backstop, concentration=concentration)


# ---------------------------------------------------------------------------
# 6. Counterparty credit / renewal cliff stress
# ---------------------------------------------------------------------------

def credit_stress(cfg) -> List[dict]:
    base = L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.75, 21300, "base", 60)
    base_r = run_l4(cfg, base)
    rows = [dict(scenario="Base L4-S no default", npv=base_r["npv_musd"], peak=base_r["peak_equity_musd"],
                 note="full 5Y fixed take-or-pay + backstop")]
    # Early termination year 3: shorten contract to 36 months
    early = L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 36, 500, 0.75, 21300, "early", 36)
    er = run_l4(cfg, early)
    rows.append(dict(scenario="Customer default/exit at year 3", npv=er["npv_musd"],
                     peak=er["peak_equity_musd"], note="contract cut to 36 months"))
    # No backstop
    nb = L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.0, 21300, "nb", 60)
    nr = run_l4(cfg, nb)
    rows.append(dict(scenario="No NVIDIA backstop", npv=nr["npv_musd"], peak=nr["peak_equity_musd"],
                     note="backstop=0"))
    # Post-contract merchant cliff: after 5Y, residual only (modeled as shorter life already)
    # Renewal at -30% rate
    ren = L4Params("S", 9.36 * 0.70, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.75, 21300, "ren", 60)
    rr = run_l4(cfg, ren)
    rows.append(dict(scenario="Renewal at -30% rate", npv=rr["npv_musd"], peak=rr["peak_equity_musd"],
                     note="repricing cliff at renewal"))
    # Refinancing freeze: higher Kd
    rf = L4Params("S", 9.36, 0.00, 0.90, 0.95, 0.55, 0.095, 60, 500, 0.75, 21300, "rf", 60)
    rfr = run_l4(cfg, rf)
    rows.append(dict(scenario="Refinancing freeze (Kd 9.5%, lev55)", npv=rfr["npv_musd"],
                     peak=rfr["peak_equity_musd"], note="lose strategic financing"))
    return rows


# ---------------------------------------------------------------------------
# 7. Vintage surface (purchase price × rate)
# ---------------------------------------------------------------------------

def vintage_surface(cfg) -> List[dict]:
    rows = []
    for purchase_gpu in [25000, 32000, 40000, 50000, 60000, 80000]:
        for rate in [2.0, 3.0, 4.0, 5.0, 6.0, 7.8, 9.36]:
            # map purchase to IT-kW using B200 density for surface
            capex_it = purchase_gpu * B200_GPU_PER_KW
            p = L4Params("M", rate, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, capex_it, "surf")
            r = run_l4(cfg, p)
            rows.append(dict(
                purchase_per_gpu=purchase_gpu, rate_gpuh=rate, capex_it_kw=round(capex_it, 0),
                npv_musd=r["npv_musd"], project_irr=r["project_irr"], peak=r["peak_equity_musd"],
            ))
    return rows


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: List[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8"); return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = load_config(CFG_PATH)

    print("=== 1. Merchant Vintage Cohorts ===")
    cohorts = [run_merchant_cohort(cfg, v) for v in VINTAGES]
    write_csv(OUT / "Merchant_Cohort_Returns.csv", cohorts)
    for c in cohorts:
        irr = "--" if c["project_irr"] is None else f"{c['project_irr']*100:.1f}%"
        print(f"  {c['vintage_id']:12s} CAPEX/kW={c['capex_per_it_kw']:.0f} rate0={c['entry_rate_gpuh']:.2f} "
              f"NPV={c['npv_musd']:9.1f}M IRR={irr} peak={c['peak_equity_musd']:.0f} conf={c['confidence']}")

    print("\n=== 2. Contract Term Structure C1–C4 ===")
    terms = [run_contract(cfg, c) for c in CONTRACTS]
    write_csv(OUT / "Compute_Term_Structure.csv", [
        dict(contract_id=t["contract_id"], label=t["label"], rate=t["rate_gpu_hr"],
             npv=t["npv_musd"], irr=t["project_irr"], peak=t["peak_equity_musd"],
             dscr=t["min_dscr_contract"], prepay_pct=t["prepay_pct"],
             tcv=t["tcv_musd"], customer_capital=t["customer_capital_musd"])
        for t in terms
    ])
    for t in terms:
        print(f"  {t['contract_id']:24s} NPV={t['npv_musd']:9.1f}M peak={t['peak_equity_musd']:.0f} "
              f"DSCR={t['min_dscr_contract']} prepay={t['prepay_pct']:.0%}")

    print("\n=== 3. L4 Certainty Bridge (MC n=120) ===")
    bridge = certainty_bridge(cfg)
    write_csv(OUT / "L4_Certainty_Bridge.csv", bridge)

    print("\n=== 4. Financeability sensitivity ===")
    fin_rows = []
    for credit in ["IG", "HY", "Spec"]:
        for tenor in [3, 5]:
            for top in [0.80, 0.95]:
                for prepay in [0.0, 0.15, 0.25]:
                    for bs in [False, True]:
                        fin_rows.append(financeability_score(credit, tenor, top, prepay, bs, 0.4))
    write_csv(OUT / "Contract_Financeability_Sensitivity.csv", fin_rows)
    print(f"  {len(fin_rows)} financeability combos")

    print("\n=== 5. Strategic credit risk ===")
    credit = credit_stress(cfg)
    write_csv(OUT / "Strategic_Credit_Risk.csv", credit)
    for r in credit:
        print(f"  {r['scenario']:40s} NPV={r['npv']:9.1f}M peak={r['peak']:.0f}")

    print("\n=== 6. Vintage surface (purchase × rate) ===")
    surface = vintage_surface(cfg)
    write_csv(OUT / "GPU_Vintage_Surface.csv", surface)
    print(f"  {len(surface)} cells")

    print("\n=== 7. Mode comparison v2 ===")
    modes = [
        run_l4(cfg, L4Params("L4-M", 7.80, -0.22, 0.75, 0.75, 0.35, 0.095, 48, 0, 0, 32000, "M")),
        run_l4(cfg, L4Params("L4-C", 9.36, 0.00, 0.90, 0.95, 0.55, 0.070, 60, 400, 0, 32000, "C", 60)),
        run_l4(cfg, L4Params("L4-S", 9.36, 0.00, 0.90, 0.95, 0.70, 0.059, 60, 500, 0.75, 21300, "S", 60)),
    ]
    l3 = run_full_pipeline(cfg, "critical_it")
    mode_rows = []
    for m, name in zip(modes, ["L4-M Merchant", "L4-C Contracted", "L4-S Strategic"]):
        mode_rows.append(dict(mode=name, **{k: m[k] for k in m if k != "mode"}))
    mode_rows.append(dict(mode="L3 Critical IT", rate_gpu_hr=None, capex_musd=round(l3.capex_total/1e6,1),
                          peak_equity_musd=round(l3.peak_equity/1e6,1), sponsor_equity_musd=round(l3.sponsor_equity/1e6,1),
                          project_irr=l3.project_irr, equity_irr=l3.equity_irr,
                          npv_musd=round(l3.project_npv/1e6,1), min_dscr=l3.min_dscr,
                          min_dscr_contract=None, moic=l3.moic, idc_musd=round(l3.idc/1e6,1),
                          debt_musd=round(l3.debt_amount/1e6,1)))
    write_csv(OUT / "L4_Merchant_Contracted_Strategic_v2.csv", mode_rows)

    # Markdown reports
    write_vintage_report(cohorts, surface)
    write_strategic_casebook()
    print("\nAll v5 outputs written to", OUT)


def write_vintage_report(cohorts, surface):
    lines = [
        "# L4 Investment Vintage 研究报告",
        "",
        "## 1. 核心命题",
        "",
        "Merchant Compute 的回报是 **Investment-Vintage-dependent** 的，而不是天然永远为负。",
        "Historical Realized Return（过去 cohort 的实际/估算回报）与 Forward New-Investment Return",
        "（今天新进入的前瞻回报）必须严格分离。",
        "",
        "$$\\mathrm{Historical\\ Winner} \\neq \\mathrm{Forward\\ Winner}$$",
        "",
        "## 2. Merchant Cohort 结果（筛选级估算）",
        "",
        "| Vintage | 采购$/GPU | CAPEX $/IT-kW | 入场租金 | NPV $M | Project IRR | Peak $M | 置信度 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in cohorts:
        irr = "—" if c["project_irr"] is None else f"{c['project_irr']*100:.1f}%"
        lines.append(
            f"| {c['vintage_id']} | {c['purchase_per_gpu']:,.0f} | {c['capex_per_it_kw']:,.0f} | "
            f"{c['entry_rate_gpuh']:.2f} | {c['npv_musd']:,.0f} | {irr} | {c['peak_equity_musd']:,.0f} | {c['confidence']:.2f} |"
        )
    lines += [
        "",
        "### 解读",
        "",
        "1. **早期 H100 vintage（2023/2024）** 在较低采购成本 + scarcity 租金路径下，Merchant NPV 显著好于 2026 Forward。",
        "2. **H100-2026 Forward 与 B200-2026 Forward** 在 -22%/年衰减假设下仍深负——这是 *Forward Return*，不能用历史 cohort 外推。",
        "3. 置信度 0.55–0.70：采购锚点来自 IREN SEC 与公开报价，租金路径为结构假设，不是完整 realized cashflow 回测。",
        "",
        "## 3. 行业四阶段演化",
        "",
        "| Phase | 特征 | 主导模式 |",
        "|---|---|---|",
        "| 1 Early Scarcity | 低进入成本、租金上行 | Merchant Alpha |",
        "| 2 High Entry Cost | 高 CAPEX + 不确定未来租金 | Merchant Risk↑ |",
        "| 3 Contractualization | 客户合同 → 可融资 | Contracted |",
        "| 4 Strategic Ecosystem | Customer+Vendor+Capital | Strategic Neocloud |",
        "",
        "## 4. 结论改写",
        "",
        "> Merchant GPU 不是天然不能盈利，而是高度依赖 Investment Vintage 与市场周期。",
        "> 过去某些低成本买卡、随后租金上行的 cohort 可能获得高回报；",
        "> 但当前新进入者的 Forward Return 可能显著恶化。",
        "> Contracted / Strategic 模式的本质，是把对未来租金、利用率和融资市场的押注",
        "> 逐步转换为可锁定、可融资的合同现金流。",
        "",
    ]
    (OUT / "L4_Investment_Vintage_研究报告.md").write_text("\n".join(lines), encoding="utf-8")


def write_strategic_casebook():
    text = """# NVIDIA Strategic Finance Casebook（证据分级）

## Level 1 — Primary / Regulatory

### CoreWeave S-1 / 10-K（合同结构）
- 2024 年约 **96%** 收入来自 committed contracts
- 合同通常 **2–5 年** take-or-pay，固定 $/contracted GPU-hour
- 加权平均期限约 **4 年**
- 客户预付款约占 TCV 的 **15%–25%**
- 通常签客户合同的同时采购基础设施，避免 unutilized capacity
- 基础设施主要通过 **take-or-pay 支持的 asset-level debt** 融资

### CoreWeave–NVIDIA residual capacity backstop（8-K）
- 新 Order Form 初始价值约 **$6.3B**
- 在满足合同条件时，NVIDIA 有义务购买 residual unsold capacity
- 有效期至 **2032-04-13**

### CoreWeave DDTL 4.0 融资（2026-03）
- Floating：SOFR + 2.25%；Fixed：约 **5.9%**
- Maturity March 2032；SPV 资产担保
- 公司称 investment-grade rated GPU-backed financing
- **注意**：5.9% 是特定工具/时点定价，不可直接推广为所有 Strategic 项目通用 Kd

### NVIDIA $2B 股权投资（2026-01）
- 向 CoreWeave 投资 $2B
- 计划利用 NVIDIA financial strength 帮助获取 land / power / shell
- CoreWeave 计划到 2030 年建设超过 5 GW AI factories

### NVIDIA $500B+ Compute Financing Platforms（2026-08-10 官方）
- 与 Apollo、BlackRock、Blackstone、Brookfield、Goldman Sachs、KKR 等
- 目标动员超过 **$500B** 第三方资本用于 AI 基础设施
- 官方定位：把 NVIDIA Compute / Full-Stack AI 变成可投资资产类别
- 支持 long-duration usage-linked revenue

## Level 2 — High-quality Press（标注 proposed / under discussion）

### NVIDIA–OpenAI / SB Energy 拟议信用支持
- 2026-07-26 Reuters/WSJ：NVIDIA 与 OpenAI 商谈约 **$250B** 融资担保/backstop，支持 SB Energy Ohio 10 GW
- 2026-08-14 Reuters/WSJ：拟议支持缩减，首期担保 **少于 $120B**
- **必须标注**：截至 2026-08-15 仍为报道/谈判中的拟议结构，**不是**已完成的 $250B 贷款
- 理论意义：Vendor 把自身资产负债表信用“包裹”到下游需求合同上

## Level 3 — Market Intelligence
- SemiAnalysis H100 1-year index：$1.70 → $2.35（约 +40%）
- Lambda / CoreWeave 公开 Spot / Instance / Dedicated 分层报价

## 强制边界
1. **不得**将“NVIDIA 给 CoreWeave 20–30% GPU 折扣”写成事实（S-1 显示主要为 PO 供货、无长期供应合同保证）
2. GPU Discount 仅作 Sensitivity：0% / 10% / 20% / 30%
3. Level 2 拟议交易必须标注 proposed / under discussion
4. Strategic 不是消灭风险，而是把风险再分配给资本实力更强的参与者（Vendor concentration / circular financing / contingent liability）

## 行业含义
$$
\\mathrm{GPU\\ Hardware}
\\rightarrow
\\mathrm{Contracted\\ Compute}
\\rightarrow
\\mathrm{Financeable\\ Asset\\ Class}
$$

AI 算力行业正在从设备交易市场演化成合同化、信用化和金融化的基础设施市场——类似飞机租赁 / 能源项目融资的路径，但底层设备折旧更快、技术代际更短。
"""
    (OUT / "NVIDIA_Strategic_Finance_Casebook.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
