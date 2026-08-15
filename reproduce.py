#!/usr/bin/env python3
"""
AIDC-Optimizer reproduction runner.

Regenerates every table in the companion working paper
"A Value-Chain Investment Evaluation Model for AI Infrastructure" (v3.x)
from a pinned config, pinned dependency versions and a fixed random seed:

    python reproduce.py run                 # recompute & write expected_outputs/alberta.json
    python reproduce.py check               # compare current outputs against the golden file
    python reproduce.py run --texas         # also write expected_outputs/texas.json (baseline only)

Environment pinning (docs/REPRODUCIBILITY.md):
    numpy==2.2.6  PyYAML==6.0.3  matplotlib==3.10.8  Python>=3.10
All stochastic draws use numpy default_rng with the seeds fixed below. The GPU
layer Monte Carlo uses a Gaussian copula on (rate, residual, capex, utilization)
with rho(rate,residual)=0.6 and 0.25 for all other off-diagonal pairs, matching
section 3.4 of the paper.

Exit codes: 0 = reproduce check passed, 1 = mismatch.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

import numpy as np
import yaml

from aidc_optimizer.cli import load_config, apply_overrides
from aidc_optimizer.risk import run_full_pipeline, monte_carlo

ROOT = pathlib.Path(__file__).resolve().parent
CFG_DIR = ROOT / "configs"
OUT_DIR = ROOT / "expected_outputs"

# Fixed seeds for full determinism (see docs/REPRODUCIBILITY.md)
SEED_L3 = 42
SEED_L4 = 42

# Scenario definitions ---------------------------------------------------------

def base_cfg(jurisdiction: str):
    return load_config(str(CFG_DIR / f"{jurisdiction}.yaml"))

def run_scenario(cfg, case: str, overrides):
    c = apply_overrides(cfg, overrides)
    r = run_full_pipeline(c, case)
    return {
        "capex_musd": round(r.capex_total / 1e6, 2),
        "sponsor_equity_musd": round(r.sponsor_equity / 1e6, 2),
        "peak_equity_musd": round(r.peak_equity / 1e6, 2),
        "project_irr": None if r.project_irr is None else round(r.project_irr, 5),
        "equity_irr": None if r.equity_irr is None else round(r.equity_irr, 5),
        "npv_musd": round(r.project_npv / 1e6, 2),
        "min_dscr": None if r.min_dscr is None else round(r.min_dscr, 4),
        "moic": round(r.moic, 3),
    }

# Power-layer parameter-coherence scenarios (paper Table 3) --------------------
POWER_SCENARIOS = {
    "P1_market_coherent": ["power.capex_per_kw=3500", "power.capacity_payment_kw_mo=28",
                           "finance.L1_Power.rate=0.058"],
    "P2_bridge_contract": ["power.capex_per_kw=1150", "power.capacity_payment_kw_mo=12",
                           "power.availability=0.88", "finance.L1_Power.rate=0.085",
                           "finance.L1_Power.leverage=0.50"],
    "P3_arbitrage": [],   # baseline = used 9E + market tolling (28% EqIRR case)
}

# 2x2x2 full factorial (paper Table 5).  Asset Stack x Contract x GPU vintage.
# Rate scheme (reverse-engineered and documented):
#   new cards:  merchant 3.0, contracted 3.2 ; used cards: merchant 1.9, contracted 2.0
FACTOR_LEVELS = {
    "asset": {"Greenfield": ["power.capex_per_kw=1150", "dc.ready_capex_per_kw=8000"],
              "Brownfield": ["power.capex_per_kw=150", "dc.ready_capex_per_kw=5500"]},
    "contract": {"Merchant": ["gpu.rate_decay=-0.22", "gpu.utilization=0.75"],
                 "Contracted": ["gpu.rate_decay=-0.08", "gpu.utilization=0.95"]},
    "vintage": {"New": ["gpu.capex_per_kw_it=32000", "gpu.residual_pct_at_refresh=0.15"],
                "Used": ["gpu.capex_per_kw_it=12000", "gpu.residual_pct_at_refresh=0.30"]},
}
RATE_BY_CELL = {("New", "Merchant"): 3.0, ("New", "Contracted"): 3.2,
                ("Used", "Merchant"): 1.9, ("Used", "Contracted"): 2.0}

def factorial_cells(cfg):
    out = {}
    for asset, ov_a in FACTOR_LEVELS["asset"].items():
        for contract, ov_c in FACTOR_LEVELS["contract"].items():
            for vintage, ov_v in FACTOR_LEVELS["vintage"].items():
                rate = RATE_BY_CELL[(vintage, contract)]
                overrides = ov_a + ov_c + ov_v + [f"gpu.rate_per_kw_hr={rate}"]
                key = f"{asset} x {contract} x {vintage}"
                out[key] = run_scenario(cfg, "compute", overrides)
    return out

# Shortage-corrected GPU scenario (paper 5.5) ---------------------------------
SHORTAGE_OVERRIDES = ["gpu.rate_decay=-0.05", "gpu.residual_pct_at_refresh=0.30",
                      "gpu.rate_per_kw_hr=3.3", "gpu.utilization=0.85"]

# L5a managed-inference corrected scenario (paper 5.5)
L5A_SHORTAGE_OVERRIDES = ["ai.rate_per_kw_hr=7.0", "ai.rate_decay=-0.10"]

# Layers priced with independent Monte Carlo in the baseline risk block (Table 4 loss column)
INDEPENDENT_MC_LAYERS = ["dev", "shell", "critical_it", "gpu_hosting", "ai_factory"]
INDEPENDENT_MC_N = 1500

# Risk layer ------------------------------------------------------------------
def wilson_ci(k: int, n: int, z: float = 1.96):
    """Wilson 95% confidence interval for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (centre - half, centre + half)

def es_lower(samples: np.ndarray, q: float = 0.05) -> float:
    """Lower-tail expected shortfall ES^-_q = E[X | X <= P_q]."""
    if len(samples) == 0:
        return float("nan")
    p5 = np.quantile(samples, q)
    tail = samples[samples <= p5]
    return float(tail.mean()) if len(tail) else float(p5)

def risk_block(samples: np.ndarray):
    n = len(samples)
    e = float(samples.mean())
    es = es_lower(samples)
    ce = {0.0: e, 0.5: 0.5 * e + 0.5 * es, 1.0: es}
    k = int((samples < 0).sum())
    lo, hi = wilson_ci(k, n)
    return {
        "n": n,
        "e_npv_musd": round(e / 1e6, 1),
        "es5_musd": round(es / 1e6, 1),
        "ce0_musd": round(ce[0.0] / 1e6, 1),
        "ce05_musd": round(ce[0.5] / 1e6, 1),
        "ce1_musd": round(ce[1.0] / 1e6, 1),
        "loss_rate": round(k / n, 4),
        "wilson_lo": round(lo, 4),
        "wilson_hi": round(hi, 4),
    }

def gpu_correlated_mc(cfg, overrides, n_sims: int, seed: int):
    """Correlated MC for the GPU (L4) layer via a Gaussian copula on
    (rate, residual, capex, utilization). rate_decay is left at base.
    Margins: rate/capex/residual lognormal, utilization normal with floor 0.2."""
    c = apply_overrides(cfg, overrides)
    rng = np.random.default_rng(seed)
    rho = np.array([[1.0, 0.6, 0.25, 0.25],
                    [0.6, 1.0, 0.25, 0.25],
                    [0.25, 0.25, 1.0, 0.25],
                    [0.25, 0.25, 0.25, 1.0]])
    L = np.linalg.cholesky(rho)
    sig = {"rate": 0.25, "residual": 0.35, "capex": 0.15, "util": 0.10}
    base = {"rate": c["gpu"]["rate_per_kw_hr"],
            "residual": c["gpu"]["residual_pct_at_refresh"],
            "capex": c["gpu"]["capex_per_kw_it"],
            "util": c["gpu"]["utilization"]}
    npvs = np.empty(n_sims)
    for i in range(n_sims):
        z = L @ rng.standard_normal(4)
        rate = base["rate"] * math.exp(sig["rate"] * z[0] - sig["rate"] ** 2 / 2)
        resid = base["residual"] * math.exp(sig["residual"] * z[1] - sig["residual"] ** 2 / 2)
        capex = base["capex"] * math.exp(sig["capex"] * z[2] - sig["capex"] ** 2 / 2)
        util = base["util"] * max(0.2, 1 + sig["util"] * z[3])
        cc = dict(c)
        cc["gpu"]["rate_per_kw_hr"] = rate
        cc["gpu"]["residual_pct_at_refresh"] = resid
        cc["gpu"]["capex_per_kw_it"] = capex
        cc["gpu"]["utilization"] = util
        npvs[i] = run_full_pipeline(cc, "compute").project_npv
    return npvs

# -----------------------------------------------------------------------------

def compute_all(jurisdiction: str):
    cfg = base_cfg(jurisdiction)
    baseline = {}
    for case in ["dev", "power", "shell", "critical_it", "gpu_hosting", "compute", "ai_factory"]:
        baseline[case] = run_scenario(cfg, case, [])
    power = {k: run_scenario(cfg, "power", v) for k, v in POWER_SCENARIOS.items()}
    factorial = factorial_cells(cfg)
    shortage = run_scenario(cfg, "compute", SHORTAGE_OVERRIDES)

    # Risk / CE-NPV / IRASR (paper Table 6 and section 5.4)
    cfg_l3 = base_cfg(jurisdiction)
    mc_l3 = monte_carlo(cfg_l3, "critical_it", n_sims=1500, seed=SEED_L3)
    npv_l3 = np.asarray(mc_l3.npv_samples)
    npv_l4_short = gpu_correlated_mc(base_cfg(jurisdiction), SHORTAGE_OVERRIDES, 800, SEED_L4)
    npv_l4_base = gpu_correlated_mc(base_cfg(jurisdiction), [], 800, SEED_L4)

    # Independent MC for Table 4 loss column (dev/shell/critical_it/hosting/ai_factory)
    baseline_risk = {}
    for case in INDEPENDENT_MC_LAYERS:
        mc = monte_carlo(base_cfg(jurisdiction), case, n_sims=INDEPENDENT_MC_N, seed=SEED_L3)
        baseline_risk[case] = risk_block(np.asarray(mc.npv_samples))

    l5a_shortage = run_scenario(cfg, "ai_factory", L5A_SHORTAGE_OVERRIDES)

    # deterministic peak equity for IRASR denominator
    cfg_l3b = base_cfg(jurisdiction)
    r_l3 = run_full_pipeline(cfg_l3b, "critical_it")
    cfg_l4s = apply_overrides(base_cfg(jurisdiction), SHORTAGE_OVERRIDES)
    r_l4s = run_full_pipeline(cfg_l4s, "compute")
    ce_l3 = 0.5 * npv_l3.mean() + 0.5 * es_lower(npv_l3)
    ce_l4s = 0.5 * npv_l4_short.mean() + 0.5 * es_lower(npv_l4_short)
    irasr = (ce_l4s - ce_l3) / (r_l4s.peak_equity - r_l3.peak_equity)

    out = {
        "metadata": {
            "jurisdiction": jurisdiction,
            "paper_version": "v3.2",
            "numpy_version": np.__version__,
            "seeds": {"L3": SEED_L3, "L4": SEED_L4},
            "note": "Regenerated from pinned config + code; see docs/REPRODUCIBILITY.md",
        },
        "baseline": baseline,
        "power_coherence": power,
        "factorial_2x2x2": factorial,
        "shortage": shortage,
        "baseline_risk": baseline_risk,
        "l5a_shortage": l5a_shortage,
        "risk": {
            "L3_criticalIT": risk_block(npv_l3),
            "L4_shortage": risk_block(npv_l4_short),
            "L4_baseline": risk_block(npv_l4_base),
        },
        "irasr": {
            "ce_l3_musd": round(ce_l3 / 1e6, 1),
            "ce_l4_shortage_musd": round(ce_l4s / 1e6, 1),
            "peak_l3_musd": round(r_l3.peak_equity / 1e6, 3),
            "peak_l4_shortage_musd": round(r_l4s.peak_equity / 1e6, 3),
            "delta_ce_musd": round((ce_l4s - ce_l3) / 1e6, 1),
            "delta_peak_musd": round((r_l4s.peak_equity - r_l3.peak_equity) / 1e6, 3),
            "value": round(irasr, 2),
        },
    }
    return out

TOL = {
    "npv_musd": 1.0, "capex_musd": 1.0, "sponsor_equity_musd": 1.0, "peak_equity_musd": 1.0,
    "project_irr": 0.001, "equity_irr": 0.001, "min_dscr": 0.01, "moic": 0.02,
    "e_npv_musd": 5.0, "es5_musd": 5.0, "ce0_musd": 5.0, "ce05_musd": 5.0, "ce1_musd": 5.0,
    "loss_rate": 0.01, "wilson_lo": 0.01, "wilson_hi": 0.01,
    "delta_ce_musd": 5.0, "delta_peak_musd": 1.0, "value": 0.05,
}

def compute_baseline(jurisdiction: str):
    """Deterministic baseline only (used for the Texas parenthetical of Table 4)."""
    cfg = base_cfg(jurisdiction)
    baseline = {case: run_scenario(cfg, case, []) for case in
                ["dev", "power", "shell", "critical_it", "gpu_hosting", "compute", "ai_factory"]}
    return {"metadata": {"jurisdiction": jurisdiction, "scope": "baseline only",
                         "numpy_version": np.__version__}, "baseline": baseline}


def check(golden_path: pathlib.Path, jurisdiction: str) -> int:
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    current = compute_all(jurisdiction)
    diffs = []

    def walk(a, b, path=""):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in a:
                if k in b:
                    walk(a[k], b[k], f"{path}.{k}")
                else:
                    diffs.append(f"missing in current: {path}.{k}")
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            key = path.rsplit(".", 1)[-1]
            tol = TOL.get(key, 1.0)
            if abs(a - b) > tol:
                diffs.append(f"{path}: golden={a} current={b} (tol={tol})")
        else:
            if a != b:
                diffs.append(f"{path}: golden={a!r} current={b!r}")

    walk(golden, current)
    if diffs:
        print(f"REPRODUCE CHECK FAILED ({len(diffs)} diffs):")
        for d in diffs[:50]:
            print("  " + d)
        return 1
    print(f"REPRODUCE CHECK PASSED — {jurisdiction} matches golden file.")
    return 0

def main():
    ap = argparse.ArgumentParser(description="AIDC-Optimizer reproduction runner")
    ap.add_argument("action", choices=["run", "check"])
    ap.add_argument("--texas", action="store_true", help="also process Texas baseline")
    args = ap.parse_args()

    if args.texas:
        # Texas: deterministic baseline only (factorial/shortage/risk are Alberta-calibrated;
        # Texas appears only as the parenthetical column of paper Table 4)
        if args.action == "run":
            out = compute_baseline("texas")
            OUT_DIR.mkdir(exist_ok=True)
            (OUT_DIR / "texas.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
            print("wrote expected_outputs/texas.json (baseline only)")
            return 0
        else:
            # Texas golden is baseline-only; compare directly against compute_baseline()
            import tempfile
            golden = json.loads((OUT_DIR / "texas.json").read_text(encoding="utf-8"))
            current = compute_baseline("texas")
            same = json.dumps(golden, sort_keys=True) == json.dumps(current, sort_keys=True)
            print("REPRODUCE CHECK PASSED — texas baseline matches golden file." if same
                  else "REPRODUCE CHECK FAILED — texas baseline differs from golden.")
            return 0 if same else 1

    if args.action == "run":
        out = compute_all("alberta")
        OUT_DIR.mkdir(exist_ok=True)
        (OUT_DIR / "alberta.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print("wrote expected_outputs/alberta.json")
        print(f"IRASR = {out['irasr']['value']} (deltaCE={out['irasr']['delta_ce_musd']}M / deltaPeak={out['irasr']['delta_peak_musd']}M)")
        return 0
    return check(OUT_DIR / "alberta.json", "alberta")

if __name__ == "__main__":
    sys.exit(main())
